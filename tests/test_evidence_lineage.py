from pathlib import Path

from models import MatterIntake
from src.evidence_lineage import build_evidence_lineage, render_evidence_lineage
from src.legal_ops import assess_matter

SAAS_MSA_FIXTURE = Path("examples/matters/saas_msa_deviation.json")


def test_lineage_covers_every_surfaced_claim():
    matter = MatterIntake.model_validate_json(SAAS_MSA_FIXTURE.read_text(encoding="utf-8"))
    graph = build_evidence_lineage(assess_matter(matter))

    assert graph.schema_version == "legal-ops-agent.evidence-lineage.v1"
    assert graph.status == "complete"
    assert graph.coverage["claims_total"] > 0
    assert graph.coverage["claims_with_complete_lineage"] == graph.coverage["claims_total"]
    assert graph.coverage["coverage_rate"] == 1.0
    assert len(graph.integrity_sha256) == 64
    assert graph.external_actions_allowed is False
    assert "Claim Evidence Lineage" in render_evidence_lineage(graph)


def test_lineage_redacts_blocked_source_identifier():
    matter = MatterIntake(
        title="Blocked lineage source review",
        requester="Legal",
        business_unit="Enterprise Sales",
        matter_type="contract",
        jurisdiction="EU",
        summary="Reviewer checks that claim lineage never exposes a blocked source identifier.",
        source_refs=["client:acme-secret-dpa"],
    )

    graph = build_evidence_lineage(assess_matter(matter))
    payload = graph.model_dump_json(by_alias=True)

    assert "client:<redacted>" in payload
    assert "acme-secret-dpa" not in payload


def test_lineage_digest_changes_when_the_matter_changes():
    original = MatterIntake.model_validate_json(SAAS_MSA_FIXTURE.read_text(encoding="utf-8"))
    changed = original.model_copy(update={"urgency": "low"})

    assert build_evidence_lineage(assess_matter(original)).integrity_sha256 != (
        build_evidence_lineage(assess_matter(changed)).integrity_sha256
    )
