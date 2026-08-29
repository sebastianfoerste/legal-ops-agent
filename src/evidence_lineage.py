"""Claim-level evidence lineage for supervised legal-operations assessments."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, Field

from models import LegalOpsAssessment
from src.source_verification import BLOCKED_SOURCE_PREFIXES


class LineageNode(BaseModel):
    node_id: str
    kind: Literal["input", "source", "rule", "claim"]
    label: str
    value_digest: str | None = None
    detail: str


class LineageEdge(BaseModel):
    source: str
    target: str
    relationship: Literal["evaluated_by", "supports"]


class EvidenceReviewItem(BaseModel):
    source_node_id: str
    source_ref: str
    source_status: Literal["pass", "warning", "blocker"]
    reason: str
    affected_claim_ids: list[str]
    reviewer_action: str


class EvidenceLineageGraph(BaseModel):
    schema_version: Literal["legal-ops-agent.evidence-lineage.v1"] = Field(alias="schema")
    assessment_id: str
    status: Literal["complete", "blocked"]
    assurance_status: Literal["clear", "review_required", "blocked"]
    coverage: dict[str, int | float]
    nodes: list[LineageNode]
    edges: list[LineageEdge]
    review_queue: list[EvidenceReviewItem]
    integrity_sha256: str
    review_gate: str
    external_actions_allowed: bool = False


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _redact_source_ref(source_ref: str) -> str:
    lower_ref = source_ref.lower()
    for prefix in BLOCKED_SOURCE_PREFIXES:
        if lower_ref.startswith(prefix):
            return f"{prefix}<redacted>"
    return source_ref


def _input_detail(value: Any) -> str:
    if isinstance(value, list):
        return f"value committed by SHA-256; list entries: {len(value)}"
    if value is None:
        return "value committed by SHA-256; value absent"
    return f"value committed by SHA-256; type: {type(value).__name__}"


def build_evidence_lineage(assessment: LegalOpsAssessment) -> EvidenceLineageGraph:
    """Map every surfaced decision claim to matter inputs and a deterministic rule."""

    nodes: dict[str, LineageNode] = {}
    edges: list[LineageEdge] = []
    claim_ids: list[str] = []
    matter = assessment.matter
    raw_inputs: dict[str, Any] = {
        "matter.title": matter.title,
        "matter.matter_type": matter.matter_type,
        "matter.summary": matter.summary,
        "matter.urgency": matter.urgency,
        "matter.data_categories": matter.data_categories,
        "matter.customer_commitments": matter.customer_commitments,
        "matter.source_refs": [_redact_source_ref(ref) for ref in matter.source_refs],
        "assessment.findings": [finding.model_dump(mode="json") for finding in assessment.findings],
        "assessment.review_state": assessment.review_state,
        "assessment.review_note": assessment.review_note,
        "assessment.audit_events": [
            {
                "seq": event.seq,
                "event_type": event.event_type,
                "event_hash": event.event_hash,
            }
            for event in assessment.audit_events
        ],
    }
    for path, value in raw_inputs.items():
        node_id = f"input:{path}"
        nodes[node_id] = LineageNode(
            node_id=node_id,
            kind="input",
            label=path,
            value_digest=_digest(value),
            detail=_input_detail(value),
        )

    for index, verification in enumerate(assessment.source_verifications):
        safe_ref = _redact_source_ref(verification.source_ref)
        node_id = f"source:{index}"
        nodes[node_id] = LineageNode(
            node_id=node_id,
            kind="source",
            label=safe_ref,
            value_digest=_digest(
                {
                    "source_ref": safe_ref,
                    "category": verification.category,
                    "status": verification.status,
                }
            ),
            detail=(
                f"category={verification.category}; status={verification.status}; "
                f"human_review={verification.requires_human_review}"
            ),
        )

    def add_claim(
        *,
        claim_id: str,
        claim_label: str,
        rule_id: str,
        rule_label: str,
        input_paths: list[str],
        claim_value: Any,
    ) -> None:
        claim_ids.append(claim_id)
        rule_node_id = f"rule:{rule_id}"
        nodes.setdefault(
            rule_node_id,
            LineageNode(
                node_id=rule_node_id,
                kind="rule",
                label=rule_label,
                detail="deterministic local rule",
            ),
        )
        nodes[claim_id] = LineageNode(
            node_id=claim_id,
            kind="claim",
            label=claim_label,
            value_digest=_digest(claim_value),
            detail="surfaced assessment claim",
        )
        for path in input_paths:
            edges.append(
                LineageEdge(
                    source=f"input:{path}",
                    target=rule_node_id,
                    relationship="evaluated_by",
                )
            )
        edges.append(
            LineageEdge(
                source=rule_node_id,
                target=claim_id,
                relationship="supports",
            )
        )

    finding_inputs = {
        "source_boundary": ["matter.source_refs"],
        "privacy": ["matter.data_categories"],
        "customer_commitments": ["matter.customer_commitments", "matter.urgency"],
        "ai_governance": ["matter.matter_type", "matter.summary"],
        "product_counsel": ["matter.matter_type", "matter.title"],
        "regulatory_monitoring": ["matter.matter_type", "matter.source_refs"],
        "workflow_control": ["matter.matter_type"],
    }
    for index, finding in enumerate(assessment.findings):
        add_claim(
            claim_id=f"claim:finding:{index}",
            claim_label=f"finding:{finding.category}",
            rule_id=f"generate_findings:{finding.category}",
            rule_label=f"generate_findings category {finding.category}",
            input_paths=finding_inputs.get(finding.category, ["matter.summary"]),
            claim_value=finding.model_dump(mode="json"),
        )

    control_inputs = {
        "source-boundary": ["matter.source_refs"],
        "human-review-gate": ["assessment.review_state"],
        "blocker-gate": ["assessment.findings"],
        "commitment-register": ["matter.customer_commitments"],
        "data-map": ["matter.data_categories"],
    }
    for index, control in enumerate(assessment.controls):
        add_claim(
            claim_id=f"claim:control:{index}",
            claim_label=f"control:{control.control_id}",
            rule_id=f"generate_controls:{control.control_id}",
            rule_label=f"generate_controls control {control.control_id}",
            input_paths=control_inputs.get(control.control_id, ["assessment.findings"]),
            claim_value=control.model_dump(mode="json"),
        )

    for index, verification in enumerate(assessment.source_verifications):
        add_claim(
            claim_id=f"claim:source-verification:{index}",
            claim_label=f"source-verification:{verification.category}",
            rule_id="verify_source_ref",
            rule_label="verify_source_ref source-boundary classification",
            input_paths=["matter.source_refs"],
            claim_value={
                **verification.model_dump(mode="json"),
                "source_ref": _redact_source_ref(verification.source_ref),
            },
        )
        edges.append(
            LineageEdge(
                source=f"source:{index}",
                target="rule:verify_source_ref",
                relationship="evaluated_by",
            )
        )

    add_claim(
        claim_id="claim:routing",
        claim_label="routing decision",
        rule_id="route_matter",
        rule_label="route_matter reviewer and SLA routing",
        input_paths=["matter.matter_type", "matter.urgency", "assessment.findings"],
        claim_value=assessment.routing.model_dump(mode="json"),
    )
    add_claim(
        claim_id="claim:export-gate",
        claim_label="export gate decision",
        rule_id="LegalOpsAssessment.validate_export_gate",
        rule_label="LegalOpsAssessment export validation",
        input_paths=[
            "assessment.review_state",
            "assessment.review_note",
            "assessment.findings",
            "assessment.audit_events",
        ],
        claim_value={
            "review_state": assessment.review_state,
            "export_allowed": assessment.export_allowed,
        },
    )

    incoming_support = {edge.target for edge in edges if edge.relationship == "supports"}
    complete_claims = sum(claim_id in incoming_support for claim_id in claim_ids)
    coverage_rate = complete_claims / len(claim_ids) if claim_ids else 0.0
    status: Literal["complete", "blocked"] = (
        "complete" if complete_claims == len(claim_ids) and claim_ids else "blocked"
    )
    ordered_nodes = sorted(nodes.values(), key=lambda node: node.node_id)
    ordered_edges = sorted(
        edges,
        key=lambda edge: (edge.source, edge.target, edge.relationship),
    )
    source_dependent_rules = {
        edge.target
        for edge in ordered_edges
        if edge.source == "input:matter.source_refs" and edge.relationship == "evaluated_by"
    }
    source_dependent_claims = sorted(
        {
            edge.target
            for edge in ordered_edges
            if edge.source in source_dependent_rules and edge.relationship == "supports"
        }
    )
    review_queue = []
    for index, verification in enumerate(assessment.source_verifications):
        if verification.status == "pass" and not verification.requires_human_review:
            continue
        if verification.status == "blocker":
            reviewer_action = (
                "Replace the blocked source reference with an approved synthetic "
                "or public regulatory source before reliance."
            )
        elif verification.status == "warning":
            reviewer_action = (
                "Validate source provenance, authority, and permitted use before reliance."
            )
        else:
            reviewer_action = (
                "Confirm the current source text, relevance, and pinpoint support before reliance."
            )
        review_queue.append(
            EvidenceReviewItem(
                source_node_id=f"source:{index}",
                source_ref=_redact_source_ref(verification.source_ref),
                source_status=verification.status,
                reason=verification.reason,
                affected_claim_ids=source_dependent_claims,
                reviewer_action=reviewer_action,
            )
        )
    assurance_status: Literal["clear", "review_required", "blocked"]
    if any(item.source_status == "blocker" for item in review_queue):
        assurance_status = "blocked"
    elif review_queue:
        assurance_status = "review_required"
    else:
        assurance_status = "clear"
    canonical_payload = {
        "assessment_id": assessment.assessment_id,
        "status": status,
        "assurance_status": assurance_status,
        "nodes": [node.model_dump(mode="json") for node in ordered_nodes],
        "edges": [edge.model_dump(mode="json") for edge in ordered_edges],
        "review_queue": [item.model_dump(mode="json") for item in review_queue],
    }
    return EvidenceLineageGraph(
        schema="legal-ops-agent.evidence-lineage.v1",
        assessment_id=assessment.assessment_id,
        status=status,
        assurance_status=assurance_status,
        coverage={
            "claims_total": len(claim_ids),
            "claims_with_complete_lineage": complete_claims,
            "coverage_rate": round(coverage_rate, 4),
            "inputs": sum(node.kind == "input" for node in ordered_nodes),
            "sources": sum(node.kind == "source" for node in ordered_nodes),
            "rules": sum(node.kind == "rule" for node in ordered_nodes),
        },
        nodes=ordered_nodes,
        edges=ordered_edges,
        review_queue=review_queue,
        integrity_sha256=_digest(canonical_payload),
        review_gate=(
            "Lineage records which local inputs and deterministic rules support each claim. "
            "Evidence exceptions remain in the review queue until a human confirms source "
            "authority, currency, relevance, and permitted use."
        ),
        external_actions_allowed=False,
    )


def render_evidence_lineage(graph: EvidenceLineageGraph) -> str:
    coverage = graph.coverage
    claim_nodes = [node for node in graph.nodes if node.kind == "claim"]
    lines = [
        "# LegalOps Claim Evidence Lineage",
        "",
        f"- Assessment: `{graph.assessment_id}`",
        f"- Lineage status: `{graph.status}`",
        f"- Evidence assurance: `{graph.assurance_status}`",
        f"- Claim coverage: {coverage['claims_with_complete_lineage']}/"
        f"{coverage['claims_total']} ({float(coverage['coverage_rate']) * 100:.1f}%)",
        f"- Integrity SHA-256: `{graph.integrity_sha256}`",
        "- External actions: disabled",
        "",
        "## Claims",
        "",
        "| Claim | Digest |",
        "| --- | --- |",
    ]
    for node in claim_nodes:
        lines.append(f"| {node.label} | `{node.value_digest}` |")
    lines.extend(
        [
            "",
            "## Evidence review queue",
            "",
            "| Source | Status | Affected claims | Reviewer action |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for item in graph.review_queue:
        lines.append(
            f"| {item.source_ref} | {item.source_status} "
            f"| {len(item.affected_claim_ids)} | {item.reviewer_action} |"
        )
    if not graph.review_queue:
        lines.append("| none | clear | 0 | none |")
    lines.extend(
        [
            "",
            "## Review gate",
            "",
            graph.review_gate,
            "",
        ]
    )
    return "\n".join(lines)
