from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.agent_governance import (
    GovernanceController,
    PolicyDecision,
    render_governance_cockpit,
)

DEMO_TIME = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)


def build_governance_demo() -> dict[str, Any]:
    controller = GovernanceController(
        secret=None,
        now=lambda: DEMO_TIME,
        kill_switch=False,
    )
    decisions: list[PolicyDecision] = []

    allowed_args = {"source_refs": ["public:https://www.eba.europa.eu/"]}
    allowed_plan = controller.make_plan(
        "legal.sources.verify",
        allowed_args,
        purpose="Verify an approved public regulatory source reference",
        requester="synthetic-demo",
    )
    allowed = controller.preflight(allowed_plan, allowed_args)
    decisions.append(allowed)
    controller.record_execution(
        allowed,
        success=True,
        reason="synthetic_verification_completed",
    )

    review_args = {
        "assessment_digest": "a" * 64,
        "decision": {"state": "approved", "reviewer": "General Counsel"},
    }
    review_plan = controller.make_plan(
        "legal.review.decide",
        review_args,
        purpose="Demonstrate the human approval boundary",
        requester="synthetic-demo",
    )
    decisions.append(controller.preflight(review_plan, review_args))

    confidential_args = {
        "title": "Synthetic source-boundary test",
        "source_refs": ["confidential:redacted-demonstration"],
    }
    confidential_plan = controller.make_plan(
        "legal.matter.assess",
        confidential_args,
        purpose="Demonstrate blocked confidential source handling",
        requester="synthetic-demo",
    )
    decisions.append(controller.preflight(confidential_plan, confidential_args))

    external_plan = controller.make_plan(
        "legal.external.send",
        {},
        purpose="Demonstrate the prohibited external action boundary",
        requester="synthetic-demo",
    )
    decisions.append(controller.preflight(external_plan, {}))

    status = controller.status()
    incident = controller.incident_bundle()
    return {
        "schema": "legal-ops-agent.governance-demonstration.v1",
        "generated_at_utc": DEMO_TIME.isoformat(),
        "fixture": "synthetic four-action governance demonstration",
        "decisions": [decision.model_dump(mode="json", by_alias=True) for decision in decisions],
        "runtime_status": status,
        "events": [event.model_dump(mode="json", by_alias=True) for event in controller.events],
        "incident_bundle": incident.model_dump(mode="json", by_alias=True),
        "raw_arguments_included": False,
        "external_actions_allowed": False,
        "review_gate": (
            "Only the human-facing local CLI can issue a consequential approval token. "
            "This demonstration issues no token and executes no consequential action."
        ),
    }


def render_governance_demo_markdown(demo: dict[str, Any]) -> str:
    lines = [
        "# Legal Agent Governance Control Plane",
        "",
        f"**Synthetic snapshot: {demo['generated_at_utc']}**",
        "",
        "## Demonstrated decisions",
        "",
        "| Tool | Decision | Reasons |",
        "| --- | --- | --- |",
    ]
    for decision in demo["decisions"]:
        lines.append(
            f"| `{decision['tool_name']}` | {decision['status']} "
            f"| {', '.join(decision['reasons'])} |"
        )
    status = demo["runtime_status"]
    lines.extend(
        [
            "",
            "## Runtime assurance",
            "",
            f"- Action events: {status['event_count']}",
            f"- Chain verified: {status['chain_verification']['verified']}",
            f"- Kill switch active: {status['kill_switch_active']}",
            "- Raw arguments included: false",
            "- External actions allowed: false",
            "",
            "## Review gate",
            "",
            demo["review_gate"],
            "",
        ]
    )
    return "\n".join(lines)


def render_governance_demo_html(demo: dict[str, Any]) -> str:
    controller = GovernanceController(
        secret=None,
        now=lambda: DEMO_TIME,
        kill_switch=False,
    )
    from src.agent_governance import AgentActionEvent

    controller.events = [AgentActionEvent.model_validate(event) for event in demo["events"]]
    return render_governance_cockpit(demo["runtime_status"], controller.events)
