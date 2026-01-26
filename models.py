from pydantic import BaseModel, Field
from typing import List, Optional

class CandidateProfile(BaseModel):
    """Represents a potential recruit for the firm."""
    name: str = Field(..., description="Full name of the candidate")
    current_role: str = Field(..., description="Current job title")
    current_firm: str = Field(..., description="Current employer")
    years_experience: int = Field(..., description="Total years of professional experience")
    
    # Scored by Agent A
    frustration_score: int = Field(..., ge=0, le=100, description="Likelihood of leaving (0-100)")
    frustration_reason: Optional[str] = Field(None, description="Why they might leave")
    
    # Scored by Agent B
    book_of_business: Optional[float] = Field(None, description="Estimated portable revenue in GBP")
    practice_area: Optional[str] = Field(None, description="Primary legal specialization")

class Signal(BaseModel):
    """Represents a market signal or regulatory change."""
    source: str = Field(..., description="Origin of the signal (e.g., 'FT', 'LawGazette')")
    headline: str = Field(..., description="Title of the news item")
    summary: str = Field(..., description="Brief summary of the event")
    impact_rating: int = Field(..., ge=1, le=10, description="Relevance to the firm (1-10)")
    relevant_practice_areas: List[str] = Field(default_factory=list, description="Which departments care about this")

class OutreachMessage(BaseModel):
    """Represents a generated message for a candidate."""
    candidate_name: str
    platform: str = Field("LinkedIn", description="Platform for the message")
    subject: str
    body: str
