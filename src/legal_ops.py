from __future__ import annotations

from models import LegalOpsAssessment, MatterIntake, ReviewDecision, RiskFinding, RoutingDecision


def build_sample_matter() -> MatterIntake:
    return MatterIntake(
        title="Enterprise customer DPA review",
        requester="Sales Ops",
        business_unit="Enterprise Sales",
        matter_type="privacy",
        jurisdiction="EU and California",
        summary=(
            "A prospective enterprise customer asks for DPA changes, regional data hosting, "
            "model training restrictions and a bespoke audit commitment before signature."
        ),
        urgency="high",
        data_categories=["customer account data", "support tickets", "workspace prompts"],
        customer_commitments=["EU hosting", "no model training", "annual audit evidence"],
        source_refs=["synthetic:dpa-review-example"],
    )


def generate_findings(matter: MatterIntake) -> list[RiskFinding]:
    findings: list[RiskFinding] = []

    if matter.data_categories:
        findings.append(
            RiskFinding(
                category="privacy",
                severity="medium",
                summary="Personal or customer data categories are in scope.",
                evidence=", ".join(matter.data_categories),
                recommended_action="Confirm DPA roles, transfer basis, subprocessors and deletion mechanics.",
            )
        )

    if matter.customer_commitments:
        findings.append(
            RiskFinding(
                category="customer_commitments",
                severity="high" if matter.urgency == "high" else "medium",
                summary="The matter includes bespoke customer commitments.",
                evidence=", ".join(matter.customer_commitments),
                recommended_action="Record each commitment in the customer obligations register before approval.",
            )
        )

    if matter.matter_type == "ai_governance" or "model training" in matter.summary.lower():
        findings.append(
            RiskFinding(
                category="ai_governance",
                severity="medium",
                summary="AI processing or model-training restrictions require review.",
                evidence=matter.summary,
                recommended_action="Check training opt-out language and product configuration before signature.",
            )
        )

    if matter.matter_type == "product_launch":
        findings.append(
            RiskFinding(
                category="product_counsel",
                severity="medium",
                summary="Product launch requires privacy, AI and customer-contract review.",
                evidence=matter.title,
                recommended_action="Route launch through product counsel checklist and security review.",
            )
        )

    if not findings:
        findings.append(
            RiskFinding(
                category="workflow_control",
                severity="low",
                summary="No elevated deterministic flags were found.",
                evidence=matter.matter_type,
                recommended_action="Keep matter in standard review queue and document final decision.",
            )
        )

    return findings


def route_matter(matter: MatterIntake, findings: list[RiskFinding]) -> RoutingDecision:
    reviewers = ["Legal Ops"]
    owner_role = "Legal Operations"

    categories = {finding.category for finding in findings}
    if "privacy" in categories:
        reviewers.append("Privacy Counsel")
        owner_role = "Privacy Counsel"
    if "ai_governance" in categories:
        reviewers.append("AI Governance Lead")
    if "customer_commitments" in categories:
        reviewers.append("Commercial Counsel")
    if matter.urgency == "high":
        reviewers.append("General Counsel")

    unique_reviewers = list(dict.fromkeys(reviewers))
    sla_hours = 24 if matter.urgency == "high" else 72
    return RoutingDecision(
        owner_role=owner_role,
        reviewers=unique_reviewers,
        rationale=(
            "Routing is based on matter type, deterministic risk categories and urgency. "
            "Export remains blocked until human approval."
        ),
        sla_hours=sla_hours,
    )


def assess_matter(matter: MatterIntake) -> LegalOpsAssessment:
    findings = generate_findings(matter)
    routing = route_matter(matter, findings)
    return LegalOpsAssessment(
        matter=matter,
        findings=findings,
        routing=routing,
        review_state="needs_review",
        export_allowed=False,
    )


def apply_review_decision(
    assessment: LegalOpsAssessment,
    decision: ReviewDecision,
) -> LegalOpsAssessment:
    blocker_present = any(finding.severity == "blocker" for finding in assessment.findings)
    export_allowed = decision.state == "approved" and not blocker_present
    return assessment.model_copy(
        update={
            "review_state": decision.state,
            "review_note": f"{decision.reviewer}: {decision.note}",
            "export_allowed": export_allowed,
        }
    )
