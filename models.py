from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

MatterType = Literal[
    "contract",
    "privacy",
    "ai_governance",
    "product_launch",
    "regulatory_monitoring",
]
Urgency = Literal["low", "medium", "high"]
RiskSeverity = Literal["low", "medium", "high", "blocker"]
ReviewState = Literal["needs_review", "approved", "rejected", "revision_requested", "escalated"]


class MatterIntake(BaseModel):
    """Typed intake record for an incoming legal-operations matter."""

    title: str = Field(..., min_length=6)
    requester: str = Field(..., min_length=2)
    business_unit: str = Field(..., min_length=2)
    matter_type: MatterType
    jurisdiction: str = Field(..., min_length=2)
    summary: str = Field(..., min_length=30)
    urgency: Urgency = "medium"
    data_categories: list[str] = Field(default_factory=list)
    customer_commitments: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class RiskFinding(BaseModel):
    """Deterministic risk finding surfaced by the workflow."""

    category: str = Field(..., min_length=3)
    severity: RiskSeverity
    summary: str = Field(..., min_length=12)
    evidence: str = Field(..., min_length=6)
    recommended_action: str = Field(..., min_length=12)


class RoutingDecision(BaseModel):
    """Review routing decision for a legal matter."""

    owner_role: str = Field(..., min_length=3)
    reviewers: list[str] = Field(..., min_length=1)
    rationale: str = Field(..., min_length=20)
    sla_hours: int = Field(..., ge=1, le=168)


class ReviewDecision(BaseModel):
    """Human review decision. Notes are mandatory for auditability."""

    reviewer: str = Field(..., min_length=2)
    state: ReviewState
    note: str = Field(..., min_length=20)

    @model_validator(mode="after")
    def validate_review_note(self) -> "ReviewDecision":
        if self.state == "approved" and len(self.note.strip()) < 30:
            raise ValueError("approval notes must be at least 30 characters")
        return self


class LegalOpsAssessment(BaseModel):
    """Full assessment record produced by the legal-ops workflow."""

    matter: MatterIntake
    findings: list[RiskFinding]
    routing: RoutingDecision
    review_state: ReviewState = "needs_review"
    export_allowed: bool = False
    review_note: str | None = None

    @model_validator(mode="after")
    def validate_export_gate(self) -> "LegalOpsAssessment":
        if self.export_allowed and self.review_state != "approved":
            raise ValueError("export requires approved review state")
        if self.export_allowed and any(finding.severity == "blocker" for finding in self.findings):
            raise ValueError("export is blocked while blocker findings remain")
        return self
