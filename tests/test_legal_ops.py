from models import MatterIntake, ReviewDecision
from src.legal_ops import apply_review_decision, assess_matter, build_sample_matter


def test_assess_matter_blocks_export_before_review():
    assessment = assess_matter(build_sample_matter())
    assert assessment.review_state == "needs_review"
    assert assessment.export_allowed is False
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
