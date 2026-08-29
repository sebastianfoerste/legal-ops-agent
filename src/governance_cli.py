from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path
from typing import Any

from src.agent_governance import (
    AgentActionPlan,
    ApprovalToken,
    GovernanceController,
)


def _read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Human-facing local CLI for legal agent governance."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    issue = sub.add_parser(
        "issue-approval",
        help="Issue a short-lived token for one exact consequential tool plan.",
    )
    issue.add_argument("--plan", type=Path, required=True)
    issue.add_argument("--reviewer", required=True)
    issue.add_argument("--reviewer-role", default="General Counsel")
    issue.add_argument("--ttl-minutes", type=int, default=15)
    issue.add_argument("--nonce")
    issue.add_argument("--out", type=Path)

    preflight = sub.add_parser(
        "preflight",
        help="Evaluate a plan and exact arguments without executing the tool.",
    )
    preflight.add_argument("--plan", type=Path, required=True)
    preflight.add_argument("--arguments", type=Path, required=True)
    preflight.add_argument("--approval-token", type=Path)
    preflight.add_argument("--out", type=Path)
    return parser


def _write_or_print(payload: dict[str, Any], output: Path | None) -> None:
    document = json.dumps(payload, indent=2) + "\n"
    if output is None:
        print(document, end="")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")


def main() -> None:
    args = build_parser().parse_args()
    controller = GovernanceController()
    plan = AgentActionPlan.model_validate(_read_object(args.plan))
    if args.command == "issue-approval":
        token = controller.issue_approval_token(
            plan,
            reviewer=args.reviewer,
            reviewer_role=args.reviewer_role,
            ttl_minutes=args.ttl_minutes,
            nonce=args.nonce or secrets.token_hex(16),
        )
        _write_or_print(
            token.model_dump(mode="json", by_alias=True),
            args.out,
        )
        return

    arguments = _read_object(args.arguments)
    token = (
        ApprovalToken.model_validate(_read_object(args.approval_token))
        if args.approval_token
        else None
    )
    decision = controller.preflight(
        plan,
        arguments,
        token,
        consume_token=False,
    )
    _write_or_print(
        decision.model_dump(mode="json", by_alias=True),
        args.out,
    )


if __name__ == "__main__":
    main()
