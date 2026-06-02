from src.legal_ops import assess_matter, build_sample_matter
from src.review_packet import build_review_packet


def test_review_packet_contains_controls_commitments_and_audit_trail():
    assessment = assess_matter(build_sample_matter())
    packet = build_review_packet(assessment)

    assert "# LegalOps Review Packet" in packet
    assert "## Controls" in packet
    assert "## Source Verification" in packet
    assert "## Customer Commitment Register" in packet
    assert "## Audit Trail" in packet
    assert assessment.assessment_id in packet
    assert "Export: `blocked`" in packet
    assert "review_packet_generated" in packet
