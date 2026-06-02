from __future__ import annotations

from typing import Any

from models import LegalOpsAssessment, MatterIntake, ReviewDecision
from src.legal_ops import apply_review_decision, assess_matter
from src.review_packet import build_review_packet


def legal_ops_mcp_manifest() -> dict[str, Any]:
    return {
        "server": {
            "name": "legal-ops-agent",
            "version": "1.0.0",
            "description": "Local legal-operations tools with typed intake and human review gates.",
        },
        "tools": [
            {
                "name": "legal.matter.assess",
                "description": "Assess a synthetic or approved legal matter and return risk findings.",
                "input_schema": MatterIntake.model_json_schema(),
            },
            {
                "name": "legal.review.decide",
                "description": "Apply a documented human review decision to an assessment.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "assessment": LegalOpsAssessment.model_json_schema(),
                        "decision": ReviewDecision.model_json_schema(),
                    },
                    "required": ["assessment", "decision"],
                },
            },
            {
                "name": "legal.sources.list",
                "description": "Return the source and data boundary for the public demo.",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "legal.review.packet",
                "description": "Render a markdown review packet from an assessment.",
                "input_schema": LegalOpsAssessment.model_json_schema(),
            },
        ],
    }


def run_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = arguments or {}
    if name == "legal.matter.assess":
        matter = MatterIntake.model_validate(payload)
        return assess_matter(matter).model_dump(mode="json")

    if name == "legal.review.decide":
        assessment = LegalOpsAssessment.model_validate(payload["assessment"])
        decision = ReviewDecision.model_validate(payload["decision"])
        return apply_review_decision(assessment, decision).model_dump(mode="json")

    if name == "legal.sources.list":
        return {
            "allowed_sources": ["synthetic examples", "public regulatory materials"],
            "blocked_sources": [
                "client documents",
                "candidate data",
                "privileged advice",
                "confidential commercial material",
            ],
            "external_processing": "disabled by default",
        }

    if name == "legal.review.packet":
        assessment = LegalOpsAssessment.model_validate(payload)
        return {"markdown": build_review_packet(assessment)}

    raise ValueError(f"unsupported tool: {name}")
