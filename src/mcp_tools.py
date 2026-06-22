from __future__ import annotations

from typing import Any

from models import LegalOpsAssessment, MatterIntake, ReviewDecision
from src.legal_ops import apply_review_decision, assess_matter
from src.review_packet import build_review_packet
from src.review_packet_runner import run_source_verified_review_packet
from src.source_verification import PUBLIC_REGULATORY_DOMAINS, verify_source_refs


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
                "name": "legal.sources.verify",
                "description": "Verify source-reference boundaries without fetching external content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source_refs": {
                            "type": "array",
                            "items": {"type": "string"},
                        }
                    },
                    "required": ["source_refs"],
                },
            },
            {
                "name": "legal.review.packet",
                "description": "Render a markdown review packet from an assessment.",
                "input_schema": LegalOpsAssessment.model_json_schema(),
            },
            {
                "name": "legal.review.packet.run",
                "description": (
                    "Assess a matter and return a source-verified review packet runner payload."
                ),
                "input_schema": MatterIntake.model_json_schema(),
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

    if name == "legal.sources.verify":
        source_refs = payload.get("source_refs", [])
        if not isinstance(source_refs, list) or not all(
            isinstance(item, str) for item in source_refs
        ):
            raise ValueError("source_refs must be a list of strings")
        records = verify_source_refs(source_refs)
        return {
            "source_verifications": [record.model_dump(mode="json") for record in records],
            "public_regulatory_domains": list(PUBLIC_REGULATORY_DOMAINS),
        }

    if name == "legal.review.packet":
        assessment = LegalOpsAssessment.model_validate(payload)
        return {"markdown": build_review_packet(assessment)}

    if name == "legal.review.packet.run":
        matter = MatterIntake.model_validate(payload)
        return run_source_verified_review_packet(matter).model_dump(
            mode="json",
            by_alias=True,
        )

    raise ValueError(f"unsupported tool: {name}")
