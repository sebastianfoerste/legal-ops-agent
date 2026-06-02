from models import MatterIntake, ReviewDecision
from src.legal_ops import apply_review_decision, assess_matter, build_sample_matter


def test_assess_matter_blocks_export_before_review():
    assessment = assess_matter(build_sample_matter())
    assert assessment.review_state == "needs_review"
    assert assessment.export_allowed is False
    assert assessment.assessment_id.startswith("loa_")
    assert assessment.controls
    assert assessment.customer_commitments
    assert assessment.audit_events[0].event_type == "assessment_created"
    assert {finding.category for finding in assessment.findings} >= {
        "privacy",
        "customer_commitments",
        "ai_governance",
    }


def test_apply_review_decision_allows_export_without_blockers():
    assessment = assess_matter(build_sample_matter())
    reviewed = apply_review_decision(
        assessment,
        ReviewDecision(
            reviewer="General Counsel",
            state="approved",
            note="Approved after privacy, AI governance and customer commitment review.",
        ),
    )
    assert reviewed.review_state == "approved"
    assert reviewed.export_allowed is True
    assert reviewed.review_note is not None
    assert reviewed.audit_events[-1].event_type == "review_decision_applied"


def test_route_matter_adds_gc_for_high_urgency():
    matter = MatterIntake(
        title="Product launch review",
        requester="Product",
        business_unit="Core Product",
        matter_type="product_launch",
        jurisdiction="EU",
        summary="Launch requires customer contract review, privacy review and AI governance review.",
        urgency="high",
    )
    assessment = assess_matter(matter)
    assert "General Counsel" in assessment.routing.reviewers
    assert assessment.routing.sla_hours == 24


def test_blocked_source_reference_prevents_export_after_approval():
    matter = MatterIntake(
        title="Privileged source boundary check",
        requester="Legal",
        business_unit="Enterprise Sales",
        matter_type="contract",
        jurisdiction="EU",
        summary="Reviewer checks that privileged or client source references are blocked.",
        urgency="medium",
        source_refs=["client:acme-dpa"],
    )

    assessment = assess_matter(matter)
    reviewed = apply_review_decision(
        assessment,
        ReviewDecision(
            reviewer="General Counsel",
            state="approved",
            note="Approved only for source-boundary control testing with blocker still present.",
        ),
    )

    assert any(finding.category == "source_boundary" for finding in assessment.findings)
    assert any(control.status == "blocker" for control in assessment.controls)
    assert reviewed.export_allowed is False
