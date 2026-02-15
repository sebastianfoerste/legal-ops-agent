import pytest
from pydantic import ValidationError

from models import CandidateProfile, OutreachMessage, Signal


def test_candidate_profile_accepts_optional_fields():
    candidate = CandidateProfile(
        name="Jane Doe",
        current_role="Partner",
        current_firm="Example LLP",
        years_experience=12,
        frustration_score=65,
    )
    assert candidate.book_of_business is None
    assert candidate.practice_area is None


def test_candidate_profile_rejects_invalid_frustration_score():
    with pytest.raises(ValidationError):
        CandidateProfile(
            name="Jane Doe",
            current_role="Partner",
            current_firm="Example LLP",
            years_experience=12,
            frustration_score=120,
        )


def test_signal_rejects_invalid_impact_rating():
    with pytest.raises(ValidationError):
        Signal(
            source="Law Gazette",
            headline="New Regulation",
            summary="A summary",
            impact_rating=11,
            relevant_practice_areas=["Corporate"],
        )


def test_outreach_message_defaults_to_linkedin_platform():
    message = OutreachMessage(
        candidate_name="Jane Doe",
        subject="Intro",
        body="Hello",
    )
    assert message.platform == "LinkedIn"
