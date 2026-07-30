from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from models import ReviewDecision
from src.agent_governance import (
    AgentActionEvent,
    ApprovalToken,
    GovernanceController,
    render_governance_cockpit,
    verify_agent_action_chain,
)
from src.legal_ops import build_sample_matter
from src.mcp_tools import run_tool


def _clock(moment: datetime):
    return lambda: moment


def _review_arguments(controller: GovernanceController) -> dict:
    assessment = run_tool(
        "legal.matter.assess",
        build_sample_matter().model_dump(mode="json"),
        controller=controller,
    )
    return {
        "assessment": assessment,
        "decision": ReviewDecision(
            reviewer="General Counsel",
            state="approved",
            note="Approved after documented human review of the synthetic matter.",
        ).model_dump(mode="json"),
    }


def test_policy_allows_inspection_and_blocks_sensitive_or_external_actions() -> None:
    controller = GovernanceController(secret="test-secret")
    allowed_args = {"source_refs": ["public:https://www.eba.europa.eu/"]}
    allowed = controller.preflight(
        controller.make_plan("legal.sources.verify", allowed_args),
        allowed_args,
    )
    assert allowed.status == "allowed"

    sensitive_args = build_sample_matter().model_dump(mode="json")
    sensitive_args["source_refs"] = ["confidential:board-pack"]
    sensitive = controller.preflight(
        controller.make_plan("legal.matter.assess", sensitive_args),
        sensitive_args,
    )
    assert sensitive.status == "blocked"
    assert "blocked_source_prefix" in sensitive.reasons

    external = controller.preflight(
        controller.make_plan("legal.external.send", {}),
        {},
    )
    assert external.status == "blocked"
    assert "external_or_prohibited_action" in external.reasons
    assert "unknown_tool_fail_closed" in external.reasons


def test_consequential_dispatch_requires_bound_human_approval() -> None:
    now = datetime(2026, 7, 30, 10, 0, tzinfo=timezone.utc)
    controller = GovernanceController(secret="test-secret", now=_clock(now))
    arguments = _review_arguments(controller)
    plan = controller.make_plan(
        "legal.review.decide",
        arguments,
        purpose="Apply the documented synthetic review decision",
        requester="human-review-cli",
    )

    required = controller.preflight(plan, arguments)
    assert required.status == "approval_required"

    token = controller.issue_approval_token(
        plan,
        reviewer="Sebastian Reviewer",
        reviewer_role="General Counsel",
        nonce="nonce-approved-001",
    )
    result = run_tool(
        "legal.review.decide",
        arguments,
        controller=controller,
        governance={
            "plan": plan.model_dump(mode="json", by_alias=True),
            "approval_token": token.model_dump(mode="json", by_alias=True),
        },
    )
    assert result["review_state"] == "approved"
    assert result["export_allowed"] is True

    with pytest.raises(ValueError, match="approval_replayed"):
        run_tool(
            "legal.review.decide",
            arguments,
            controller=controller,
            governance={
                "plan": plan.model_dump(mode="json", by_alias=True),
                "approval_token": token.model_dump(mode="json", by_alias=True),
            },
        )


def test_token_tampering_expiry_role_and_argument_mismatch_fail_closed() -> None:
    now = datetime(2026, 7, 30, 10, 0, tzinfo=timezone.utc)
    controller = GovernanceController(secret="test-secret", now=_clock(now))
    arguments = _review_arguments(controller)
    plan = controller.make_plan("legal.review.decide", arguments)
    token = controller.issue_approval_token(
        plan,
        reviewer="Human Reviewer",
        reviewer_role="General Counsel",
        ttl_minutes=1,
        nonce="nonce-binding-001",
    )

    tampered_payload = token.model_dump(mode="json", by_alias=True)
    tampered_payload["reviewer"] = "Different Reviewer"
    tampered = controller.preflight(
        plan,
        arguments,
        ApprovalToken.model_validate(tampered_payload),
    )
    assert tampered.status == "blocked"
    assert "approval_signature_invalid" in tampered.reasons

    mismatched_args = {**arguments, "unexpected": True}
    mismatch = controller.preflight(plan, mismatched_args, token)
    assert mismatch.status == "blocked"
    assert "plan_arguments_mismatch" in mismatch.reasons

    wrong_role_payload = token.model_dump(mode="json", by_alias=True)
    wrong_role_payload["reviewer_role"] = "Legal Operations"
    wrong_role_payload["signature"] = "0" * 64
    wrong_role = controller.preflight(
        plan,
        arguments,
        ApprovalToken.model_validate(wrong_role_payload),
    )
    assert "approval_role_mismatch" in wrong_role.reasons

    expired_controller = GovernanceController(
        secret="test-secret",
        now=_clock(now + timedelta(minutes=2)),
    )
    expired = expired_controller.preflight(plan, arguments, token)
    assert expired.status == "blocked"
    assert "approval_expired" in expired.reasons


def test_concurrent_token_consumption_allows_one_execution_path() -> None:
    now = datetime(2026, 7, 30, 10, 0, tzinfo=timezone.utc)
    controller = GovernanceController(secret="test-secret", now=_clock(now))
    arguments = {"assessment": {"synthetic": True}, "decision": {"state": "approved"}}
    plan = controller.make_plan("legal.review.decide", arguments)
    token = controller.issue_approval_token(
        plan,
        reviewer="Human Reviewer",
        reviewer_role="General Counsel",
        nonce="nonce-concurrent-001",
    )

    def attempt() -> str:
        return controller.preflight(
            plan,
            arguments,
            token,
            consume_token=True,
        ).status

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = sorted(executor.map(lambda _: attempt(), range(2)))
    assert statuses == ["allowed", "blocked"]


def test_kill_switch_chain_verification_and_redacted_incident_bundle(
    tmp_path,
) -> None:
    controller = GovernanceController(secret="test-secret", kill_switch=True)
    arguments = build_sample_matter().model_dump(mode="json")
    blocked = controller.preflight(
        controller.make_plan("legal.matter.assess", arguments),
        arguments,
    )
    assert blocked.status == "blocked"
    assert "kill_switch_active" in blocked.reasons
    status = run_tool("legal.agent.status", controller=controller)
    assert status["kill_switch_active"] is True

    bundle = run_tool("legal.agent.incident.build", controller=controller)
    rendered = str(bundle)
    assert "confidential:" not in rendered
    assert all(record["raw_arguments_included"] is False for record in bundle["replay_records"])
    assert bundle["chain_verification"]["verified"] is True

    tampered_events = deepcopy(controller.events)
    payload = tampered_events[0].model_dump(mode="json", by_alias=True)
    payload["tool_name"] = "legal.changed"
    tampered_events[0] = AgentActionEvent.model_validate(payload)
    assert verify_agent_action_chain(tampered_events)["verified"] is False

    cockpit = render_governance_cockpit(controller.status(), controller.events)
    assert "Governance Control Plane" in cockpit
    assert "confidential:" not in cockpit

    ledger_path = tmp_path / "agent-actions.jsonl"
    persisted = GovernanceController(
        secret="test-secret",
        ledger_path=ledger_path,
    )
    public_args = {"source_refs": ["public:https://www.eba.europa.eu/"]}
    persisted.preflight(
        persisted.make_plan("legal.sources.verify", public_args),
        public_args,
    )
    restored = GovernanceController(
        secret="test-secret",
        ledger_path=ledger_path,
    )
    assert restored.status()["event_count"] == 1
    assert restored.status()["chain_verification"]["verified"] is True
