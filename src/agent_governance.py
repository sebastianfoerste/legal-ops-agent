from __future__ import annotations

import hashlib
import hmac
import html
import json
import os
import threading
from collections import Counter
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

POLICY_SCHEMA = "legal-ops-agent.agent-policy.v1"
PLAN_SCHEMA = "legal-ops-agent.agent-action-plan.v1"
TOKEN_SCHEMA = "legal-ops-agent.approval-token.v1"
DECISION_SCHEMA = "legal-ops-agent.policy-decision.v1"
EVENT_SCHEMA = "legal-ops-agent.agent-action-event.v1"
INCIDENT_SCHEMA = "legal-ops-agent.incident-bundle.v1"
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[1] / "policy" / "agent_policy.v1.json"

DecisionStatus = Literal["allowed", "blocked", "approval_required"]
ActionStatus = Literal["allowed", "blocked", "approval_required", "executed", "failed"]


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


class ToolPolicy(BaseModel):
    tool_name: str
    effect: Literal["inspect_local", "draft_local", "consequential_local"]
    consequence: Literal["low", "medium", "high"]
    required_reviewer_role: str | None = None


class AgentPolicy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["legal-ops-agent.agent-policy.v1"] = Field(alias="schema")
    policy_version: str
    default_decision: Literal["block"] = "block"
    blocked_source_prefixes: list[str]
    blocked_data_classes: list[str]
    prohibited_action_terms: list[str]
    kill_switch_exempt_tools: list[str]
    tools: list[ToolPolicy]

    @model_validator(mode="after")
    def unique_tools(self) -> AgentPolicy:
        names = [tool.tool_name for tool in self.tools]
        if len(names) != len(set(names)):
            raise ValueError("agent policy tool names must be unique")
        return self

    def tool(self, name: str) -> ToolPolicy | None:
        return next((tool for tool in self.tools if tool.tool_name == name), None)


class PlannedToolCall(BaseModel):
    call_id: str = Field(..., min_length=6)
    tool_name: str = Field(..., min_length=3)
    arguments_digest: str = Field(..., min_length=64, max_length=64)


class AgentActionPlan(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["legal-ops-agent.agent-action-plan.v1"] = Field(alias="schema")
    plan_id: str = Field(..., min_length=6)
    purpose: str = Field(..., min_length=12)
    requester: str = Field(..., min_length=2)
    data_classes: list[str] = Field(default_factory=lambda: ["synthetic"])
    tool_call: PlannedToolCall

    def digest(self) -> str:
        return sha256_payload(self.model_dump(mode="json", by_alias=True))


class ApprovalToken(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["legal-ops-agent.approval-token.v1"] = Field(alias="schema")
    token_id: str = Field(..., min_length=8)
    plan_digest: str = Field(..., min_length=64, max_length=64)
    tool_name: str
    arguments_digest: str = Field(..., min_length=64, max_length=64)
    policy_version: str
    reviewer: str = Field(..., min_length=2)
    reviewer_role: str = Field(..., min_length=3)
    issued_at_utc: str
    expires_at_utc: str
    nonce: str = Field(..., min_length=8)
    signature: str = Field(..., min_length=64, max_length=64)

    def unsigned_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json", by_alias=True)
        payload.pop("signature")
        return payload


class PolicyDecision(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["legal-ops-agent.policy-decision.v1"] = Field(alias="schema")
    status: DecisionStatus
    plan_id: str
    plan_digest: str
    tool_name: str
    arguments_digest: str
    policy_version: str
    effect: str | None = None
    consequence: str | None = None
    reasons: list[str]
    approval_token_id: str | None = None
    external_actions_allowed: bool = False


class AgentActionEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["legal-ops-agent.agent-action-event.v1"] = Field(alias="schema")
    seq: int = Field(..., ge=0)
    event_id: str
    timestamp_utc: str
    status: ActionStatus
    tool_name: str
    plan_id: str
    plan_digest: str
    arguments_digest: str
    policy_version: str
    reasons: list[str]
    approval_token_id: str | None = None
    prev_hash: str | None = None
    event_hash: str


class IncidentBundle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["legal-ops-agent.incident-bundle.v1"] = Field(alias="schema")
    generated_at_utc: str
    policy_version: str
    kill_switch_active: bool
    summary: dict[str, int]
    chain_verification: dict[str, Any]
    violations: list[dict[str, Any]]
    replay_records: list[dict[str, Any]]
    source_boundary: str
    external_actions_allowed: bool = False
    integrity_sha256: str


def load_agent_policy(path: Path = DEFAULT_POLICY_PATH) -> AgentPolicy:
    return AgentPolicy.model_validate_json(path.read_text(encoding="utf-8"))


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_walk_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_walk_strings(item))
        return strings
    return []


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("approval token timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def _event_hash(payload: dict[str, Any]) -> str:
    return sha256_payload(payload)


def verify_agent_action_chain(events: list[AgentActionEvent]) -> dict[str, Any]:
    expected_previous: str | None = None
    for index, event in enumerate(events):
        if event.seq != index:
            return {
                "verified": False,
                "event_count": len(events),
                "broken_at_seq": event.seq,
                "reason": "sequence_mismatch",
                "chain_root_hash": None,
            }
        payload = event.model_dump(mode="json", by_alias=True)
        submitted_hash = payload.pop("event_hash")
        if event.prev_hash != expected_previous or _event_hash(payload) != submitted_hash:
            return {
                "verified": False,
                "event_count": len(events),
                "broken_at_seq": event.seq,
                "reason": "hash_chain_mismatch",
                "chain_root_hash": None,
            }
        expected_previous = submitted_hash
    return {
        "verified": bool(events),
        "event_count": len(events),
        "broken_at_seq": None,
        "reason": "chain_intact" if events else "no_events",
        "chain_root_hash": expected_previous,
    }


class GovernanceController:
    def __init__(
        self,
        policy: AgentPolicy | None = None,
        *,
        secret: str | None = None,
        now: Callable[[], datetime] | None = None,
        ledger_path: Path | None = None,
        kill_switch: bool | None = None,
    ) -> None:
        self.policy = policy or load_agent_policy()
        self.secret = secret if secret is not None else os.getenv("LEGAL_OPS_APPROVAL_SECRET")
        self._now = now or (lambda: datetime.now(timezone.utc))
        self.ledger_path = ledger_path
        self.kill_switch = (
            kill_switch
            if kill_switch is not None
            else os.getenv("LEGAL_OPS_AGENT_KILL_SWITCH", "").lower() in {"1", "true", "yes"}
        )
        self.events: list[AgentActionEvent] = []
        self._consumed_tokens: set[str] = set()
        self._lock = threading.Lock()
        self._load_existing_ledger()

    def _load_existing_ledger(self) -> None:
        if self.ledger_path is None or not self.ledger_path.is_file():
            return
        events: list[AgentActionEvent] = []
        for line_number, line in enumerate(
            self.ledger_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                events.append(AgentActionEvent.model_validate_json(line))
            except ValueError as exc:
                raise ValueError(f"invalid action ledger event at line {line_number}") from exc
        verification = verify_agent_action_chain(events)
        if events and not verification["verified"]:
            raise ValueError(
                f"existing action ledger failed verification: {verification['reason']}"
            )
        self.events = events
        self._consumed_tokens = {
            event.approval_token_id
            for event in events
            if event.approval_token_id and event.status in {"allowed", "executed"}
        }

    def make_plan(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        purpose: str | None = None,
        requester: str = "local-runtime",
        data_classes: list[str] | None = None,
    ) -> AgentActionPlan:
        arguments_digest = sha256_payload(arguments)
        plan_id = f"plan-{arguments_digest[:16]}"
        return AgentActionPlan(
            schema="legal-ops-agent.agent-action-plan.v1",
            plan_id=plan_id,
            purpose=purpose or f"Run controlled local tool {tool_name}",
            requester=requester,
            data_classes=data_classes or ["synthetic"],
            tool_call=PlannedToolCall(
                call_id=f"call-{arguments_digest[:16]}",
                tool_name=tool_name,
                arguments_digest=arguments_digest,
            ),
        )

    def issue_approval_token(
        self,
        plan: AgentActionPlan,
        *,
        reviewer: str,
        reviewer_role: str,
        ttl_minutes: int = 15,
        nonce: str,
    ) -> ApprovalToken:
        if not self.secret:
            raise ValueError("LEGAL_OPS_APPROVAL_SECRET is required to issue approval tokens")
        if ttl_minutes < 1 or ttl_minutes > 60:
            raise ValueError("approval token TTL must be between 1 and 60 minutes")
        tool_policy = self.policy.tool(plan.tool_call.tool_name)
        if tool_policy is None or tool_policy.required_reviewer_role != reviewer_role:
            raise ValueError("reviewer role does not satisfy the tool policy")
        issued_at = self._now().astimezone(timezone.utc)
        unsigned = {
            "schema": TOKEN_SCHEMA,
            "token_id": f"approval-{sha256_payload([plan.digest(), reviewer, nonce])[:16]}",
            "plan_digest": plan.digest(),
            "tool_name": plan.tool_call.tool_name,
            "arguments_digest": plan.tool_call.arguments_digest,
            "policy_version": self.policy.policy_version,
            "reviewer": reviewer,
            "reviewer_role": reviewer_role,
            "issued_at_utc": issued_at.isoformat(),
            "expires_at_utc": (issued_at + timedelta(minutes=ttl_minutes)).isoformat(),
            "nonce": nonce,
        }
        signature = hmac.new(
            self.secret.encode("utf-8"),
            canonical_json(unsigned).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return ApprovalToken.model_validate({**unsigned, "signature": signature})

    def _approval_reasons(
        self,
        plan: AgentActionPlan,
        token: ApprovalToken | None,
        required_role: str,
        *,
        consume: bool,
    ) -> tuple[list[str], str | None]:
        if token is None:
            return ["documented_human_approval_required"], None
        if not self.secret:
            return ["approval_secret_unavailable"], token.token_id
        expected = hmac.new(
            self.secret.encode("utf-8"),
            canonical_json(token.unsigned_payload()).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        reasons: list[str] = []
        if not hmac.compare_digest(expected, token.signature):
            reasons.append("approval_signature_invalid")
        if token.plan_digest != plan.digest():
            reasons.append("approval_plan_mismatch")
        if token.tool_name != plan.tool_call.tool_name:
            reasons.append("approval_tool_mismatch")
        if token.arguments_digest != plan.tool_call.arguments_digest:
            reasons.append("approval_arguments_mismatch")
        if token.policy_version != self.policy.policy_version:
            reasons.append("approval_policy_mismatch")
        if token.reviewer_role != required_role:
            reasons.append("approval_role_mismatch")
        now = self._now().astimezone(timezone.utc)
        if _parse_timestamp(token.expires_at_utc) <= now:
            reasons.append("approval_expired")
        if _parse_timestamp(token.issued_at_utc) > now:
            reasons.append("approval_issued_in_future")
        if token.token_id in self._consumed_tokens:
            reasons.append("approval_replayed")
        if not reasons and consume:
            self._consumed_tokens.add(token.token_id)
        return reasons, token.token_id

    def preflight(
        self,
        plan: AgentActionPlan,
        arguments: dict[str, Any],
        token: ApprovalToken | None = None,
        *,
        consume_token: bool = False,
        record: bool = True,
    ) -> PolicyDecision:
        with self._lock:
            decision = self._preflight_locked(plan, arguments, token, consume_token=consume_token)
            if record:
                self._record(
                    decision.status,
                    decision,
                    decision.reasons,
                    decision.approval_token_id,
                )
            return decision

    def _preflight_locked(
        self,
        plan: AgentActionPlan,
        arguments: dict[str, Any],
        token: ApprovalToken | None,
        *,
        consume_token: bool,
    ) -> PolicyDecision:
        tool_name = plan.tool_call.tool_name
        actual_digest = sha256_payload(arguments)
        reasons: list[str] = []
        tool_policy = self.policy.tool(tool_name)
        effect = tool_policy.effect if tool_policy else None
        consequence = tool_policy.consequence if tool_policy else None

        if plan.tool_call.arguments_digest != actual_digest:
            reasons.append("plan_arguments_mismatch")
        if self.kill_switch and tool_name not in self.policy.kill_switch_exempt_tools:
            reasons.append("kill_switch_active")
        lowered_name = tool_name.lower()
        if any(term in lowered_name for term in self.policy.prohibited_action_terms):
            reasons.append("external_or_prohibited_action")
        if tool_policy is None:
            reasons.append("unknown_tool_fail_closed")
        if set(plan.data_classes) & set(self.policy.blocked_data_classes):
            reasons.append("blocked_data_class")
        strings = [item.lower() for item in _walk_strings(arguments)]
        if tool_name != "legal.sources.verify" and any(
            value.startswith(prefix.lower())
            for value in strings
            for prefix in self.policy.blocked_source_prefixes
        ):
            reasons.append("blocked_source_prefix")

        status: DecisionStatus
        token_id: str | None = token.token_id if token else None
        if reasons:
            status = "blocked"
        elif tool_policy and tool_policy.required_reviewer_role:
            approval_reasons, token_id = self._approval_reasons(
                plan,
                token,
                tool_policy.required_reviewer_role,
                consume=consume_token,
            )
            if approval_reasons:
                status = (
                    "approval_required"
                    if approval_reasons == ["documented_human_approval_required"]
                    else "blocked"
                )
                reasons.extend(approval_reasons)
            else:
                status = "allowed"
                reasons.append("bound_human_approval_verified")
        else:
            status = "allowed"
            reasons.append("local_policy_allows_tool")

        return PolicyDecision(
            schema="legal-ops-agent.policy-decision.v1",
            status=status,
            plan_id=plan.plan_id,
            plan_digest=plan.digest(),
            tool_name=tool_name,
            arguments_digest=actual_digest,
            policy_version=self.policy.policy_version,
            effect=effect,
            consequence=consequence,
            reasons=sorted(set(reasons)),
            approval_token_id=token_id,
        )

    def _record(
        self,
        status: ActionStatus,
        decision: PolicyDecision,
        reasons: list[str],
        token_id: str | None,
    ) -> AgentActionEvent:
        previous_hash = self.events[-1].event_hash if self.events else None
        base = {
            "schema": EVENT_SCHEMA,
            "seq": len(self.events),
            "event_id": f"action-{len(self.events):04d}-{decision.plan_digest[:10]}",
            "timestamp_utc": self._now().astimezone(timezone.utc).isoformat(),
            "status": status,
            "tool_name": decision.tool_name,
            "plan_id": decision.plan_id,
            "plan_digest": decision.plan_digest,
            "arguments_digest": decision.arguments_digest,
            "policy_version": decision.policy_version,
            "reasons": sorted(set(reasons)),
            "approval_token_id": token_id,
            "prev_hash": previous_hash,
        }
        event = AgentActionEvent.model_validate({**base, "event_hash": _event_hash(base)})
        self.events.append(event)
        if self.ledger_path is not None:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with self.ledger_path.open("a", encoding="utf-8") as handle:
                handle.write(event.model_dump_json(by_alias=True) + "\n")
        return event

    def record_execution(
        self,
        decision: PolicyDecision,
        *,
        success: bool,
        reason: str,
    ) -> AgentActionEvent:
        with self._lock:
            return self._record(
                "executed" if success else "failed",
                decision,
                [reason],
                decision.approval_token_id,
            )

    def status(self) -> dict[str, Any]:
        counts = Counter(event.status for event in self.events)
        return {
            "schema": "legal-ops-agent.agent-runtime-status.v1",
            "policy_version": self.policy.policy_version,
            "kill_switch_active": self.kill_switch,
            "event_count": len(self.events),
            "status_counts": dict(sorted(counts.items())),
            "consumed_approval_tokens": len(self._consumed_tokens),
            "chain_verification": verify_agent_action_chain(self.events),
            "external_actions_allowed": False,
        }

    def incident_bundle(self) -> IncidentBundle:
        summary = Counter(event.status for event in self.events)
        violations = [
            {
                "event_id": event.event_id,
                "status": event.status,
                "tool_name": event.tool_name,
                "reasons": event.reasons,
                "plan_digest": event.plan_digest,
            }
            for event in self.events
            if event.status in {"blocked", "approval_required", "failed"}
        ]
        replay = [
            {
                "event_id": event.event_id,
                "tool_name": event.tool_name,
                "plan_id": event.plan_id,
                "plan_digest": event.plan_digest,
                "arguments_digest": event.arguments_digest,
                "policy_version": event.policy_version,
                "raw_arguments_included": False,
            }
            for event in self.events
        ]
        payload = {
            "schema": INCIDENT_SCHEMA,
            "generated_at_utc": self._now().astimezone(timezone.utc).isoformat(),
            "policy_version": self.policy.policy_version,
            "kill_switch_active": self.kill_switch,
            "summary": dict(sorted(summary.items())),
            "chain_verification": verify_agent_action_chain(self.events),
            "violations": violations,
            "replay_records": replay,
            "source_boundary": (
                "Only policy decisions, canonical digests, redacted metadata, and "
                "synthetic demonstration identifiers are included."
            ),
            "external_actions_allowed": False,
        }
        return IncidentBundle.model_validate(
            {**payload, "integrity_sha256": sha256_payload(payload)}
        )


def render_governance_cockpit(
    status: dict[str, Any],
    events: list[AgentActionEvent],
) -> str:
    counts = status["status_counts"]
    rows = (
        "".join(
            "<tr>"
            f"<td>{event.seq}</td>"
            f"<td>{html.escape(event.tool_name)}</td>"
            f"<td>{html.escape(event.status)}</td>"
            f"<td><code>{event.arguments_digest[:14]}</code></td>"
            f"<td>{html.escape(', '.join(event.reasons))}</td>"
            "</tr>"
            for event in reversed(events)
        )
        or "<tr><td colspan='5'>No governed actions recorded.</td></tr>"
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Legal Agent Governance Control Plane</title>
<style>
body{{margin:0;background:#edf1f2;color:#172126;font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1100px;margin:auto;padding:42px 24px}}h1{{font:700 34px/1.2 Georgia,serif;margin:0}}
.eyebrow{{color:#14544d;font-weight:700;text-transform:uppercase;letter-spacing:.08em;font-size:12px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}
.card,section{{background:white;border:1px solid #dce3e5;border-radius:10px;padding:18px}}
.card strong{{display:block;font-size:27px}}section{{margin-top:18px;overflow:auto}}
table{{width:100%;border-collapse:collapse;min-width:760px}}th,td{{padding:10px;border-bottom:1px solid #e3e8ea;text-align:left}}
th{{font-size:12px;color:#5e6a70;text-transform:uppercase}}code{{font-size:12px}}
.blocked{{color:#8c2f23}}@media(max-width:720px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><main>
<p class="eyebrow">Local runtime oversight · synthetic demonstration</p>
<h1>Legal Agent Governance Control Plane</h1>
<p>Policy <code>{html.escape(status['policy_version'])}</code>. External actions remain disabled.</p>
<div class="grid">
<div class="card"><strong>{status['event_count']}</strong><span>action events</span></div>
<div class="card"><strong>{counts.get('executed', 0)}</strong><span>executed</span></div>
<div class="card"><strong class="blocked">{counts.get('blocked', 0)}</strong><span>blocked</span></div>
<div class="card"><strong>{str(status['chain_verification']['verified']).lower()}</strong><span>chain verified</span></div>
</div>
<section><h2>Runtime action ledger</h2><table><thead><tr><th>Seq</th><th>Tool</th><th>Status</th><th>Argument digest</th><th>Reason</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>Control boundary</h2><p>Consequential decisions require a short-lived, role-bound, one-time approval token. The ledger stores digests and redacted metadata only.</p></section>
</main></body></html>"""


_DEFAULT_CONTROLLER: GovernanceController | None = None
_DEFAULT_LOCK = threading.Lock()


def get_default_controller() -> GovernanceController:
    global _DEFAULT_CONTROLLER
    with _DEFAULT_LOCK:
        if _DEFAULT_CONTROLLER is None:
            ledger = os.getenv("LEGAL_OPS_ACTION_LEDGER")
            _DEFAULT_CONTROLLER = GovernanceController(ledger_path=Path(ledger) if ledger else None)
        return _DEFAULT_CONTROLLER
