"""
Agent D: The Scheduling Concierge
Purpose: Handle logistics and interviewer briefing for candidate interviews.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from google import genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

# Configuration
MAX_INTERVIEWS_PER_PARTNER_PER_WEEK = 3
PREFERRED_HOURS = ["18:00", "18:30", "19:00", "19:30", "20:00"]  # Evening slots for discretion

# Mock Partner Database (in production, this would be Salesforce/Elite 3E)
PARTNER_DATABASE = {
    "crypto": [
        {"name": "Dr. Thomas Richter", "specialty": "Crypto/Blockchain", "interviews_this_week": 1},
        {"name": "Lisa Hoffmann", "specialty": "FinTech/DeFi", "interviews_this_week": 2},
    ],
    "restructuring": [
        {
            "name": "Dr. Klaus Müller",
            "specialty": "Restructuring/Insolvency",
            "interviews_this_week": 0,
        },
        {"name": "Anna Weber", "specialty": "Distressed M&A", "interviews_this_week": 3},
    ],
    "m&a": [
        {"name": "Michael Schmidt", "specialty": "M&A/Private Equity", "interviews_this_week": 1},
    ],
    "employment": [
        {"name": "Dr. Sarah Klein", "specialty": "Employment Law", "interviews_this_week": 2},
    ],
}


def find_matching_interviewer(candidate_niche: str) -> dict:
    """
    Match candidate with a Gunnercooke partner in the same niche.
    Checks interviewer load to ensure no partner does >3 interviews/week.
    """
    niche_key = candidate_niche.lower()

    # Try exact match first
    for key in PARTNER_DATABASE:
        if key in niche_key or niche_key in key:
            partners = PARTNER_DATABASE[key]
            available = [
                p
                for p in partners
                if p["interviews_this_week"] < MAX_INTERVIEWS_PER_PARTNER_PER_WEEK
            ]
            if available:
                # Return the one with lowest load
                return min(available, key=lambda x: x["interviews_this_week"])

    # Fallback: return any available partner
    for _key, partners in PARTNER_DATABASE.items():
        available = [
            p for p in partners if p["interviews_this_week"] < MAX_INTERVIEWS_PER_PARTNER_PER_WEEK
        ]
        if available:
            return min(available, key=lambda x: x["interviews_this_week"])

    return None


def generate_time_slots(days_ahead: int = 7) -> list:
    """Generate available evening time slots for the next N days."""
    # The original logic for generating slots is replaced by a call to the generative model.
    # The model will be prompted to suggest evening slots for the next N days.

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    Generate a list of 10 distinct evening time slots for interviews over the next {days_ahead} days, starting from tomorrow ({today}).
    Each slot should be in the format: "DayOfWeek, Day Month Year at HH:MM CET".
    Prioritize times between 18:00 and 20:00 CET.
    Ensure no weekend dates are included.
    Return only the list of slots, one per line, without any introductory or concluding text.
    Example:
    Tuesday, 23 July 2024 at 18:00 CET
    Tuesday, 23 July 2024 at 18:30 CET
    Wednesday, 24 July 2024 at 19:00 CET
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash",  # Using gemini-1.5-flash as gemini-3-flash is not a standard model name
        contents=prompt,
    )

    # Parse the response into a list of strings
    slots = [s.strip() for s in response.text.split("\n") if s.strip()]
    return slots[:10]  # Ensure we return at most 10 options as per original function's intent


def generate_scheduling_email(candidate_name: str) -> str:
    """Generate the scheduling email to send to candidate."""
    slots = generate_time_slots()

    email = f"""
Dear {candidate_name},

Thank you for your interest in a conversation with Gunnercooke Germany.

To ensure complete discretion, we prefer evening meetings. Please let me know which of the following times works for you:

"""
    for i, slot in enumerate(slots, 1):
        email += f"  {i}. {slot}\n"

    email += """
The call will be a relaxed 30-minute virtual coffee – no formal interview structure. We simply want to understand your goals and share how our model works.

If none of these times suit, please suggest alternatives that work for you.

Best regards,
Scheduling Coordinator
Gunnercooke Germany
"""
    return email


def generate_briefing_dossier(
    candidate_name: str,
    current_firm: str,
    practice_area: str,
    frustration_score: int,
    frustration_reasons: str,
    portable_revenue: float,
    interviewer_name: str,
) -> str:
    """
    Generate a Briefing Dossier for the interviewer.

    Includes Frustration Score from Agent A and Revenue Estimate from Agent B.
    """

    dossier = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CONFIDENTIAL BRIEFING DOSSIER                        ║
║                            Gunnercooke Germany                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Interview Date: [TO BE SCHEDULED]                                           ║
║  Interviewer: {interviewer_name:<60} ║
╠══════════════════════════════════════════════════════════════════════════════╣

📋 CANDIDATE PROFILE
───────────────────────────────────────────────────────────────────────────────
  Name:           {candidate_name}
  Current Firm:   {current_firm}
  Practice Area:  {practice_area}

📊 AGENT A: FRUSTRATION SCORE
───────────────────────────────────────────────────────────────────────────────
  Score: {frustration_score}/100 {"🔥🔥🔥" if frustration_score > 80 else "🔥🔥" if frustration_score > 60 else "🔥"}
  
  Reasons:
  {frustration_reasons}

💰 AGENT B: REVENUE ESTIMATE
───────────────────────────────────────────────────────────────────────────────
  Estimated Portable Revenue: €{portable_revenue:,.0f}
  Assessment: {"✅ GO (>€200k)" if portable_revenue >= 200000 else "⚠️ BORDERLINE" if portable_revenue >= 150000 else "❌ BELOW THRESHOLD"}

🎯 INTERVIEW GUIDANCE
───────────────────────────────────────────────────────────────────────────────

  ⚠️  REMINDER: This is a SALES CONVERSATION, not an interrogation.
  
  FOCUS ON:
  ✓ Their frustrations with Big Law (they have a score of {frustration_score}!)
  ✓ The FREEDOM they will gain (no billable targets, equity from day 1)
  ✓ The UPSIDE (70/30 split, transparent Netto-Rechner)
  
  AVOID:
  ✗ Asking why they want to leave (they are blocked – that's why)
  ✗ Testing their technical knowledge
  ✗ Making them "sell" themselves to you
  
  KEY TALKING POINTS:
  1. "At Gunnercooke, you keep what you earn. Let me show you the numbers."
  2. "You've been a Senior Associate for {frustration_score // 10} years doing Partner work. 
      Here, you'd be equity partner from day one."
  3. "Our model is designed for people exactly like you – senior, frustrated, ready."

  CLOSE WITH:
  "If this sounds interesting, we move fast. Would you like me to send you the 
   Netto-Rechner so you can model your own income?"

═══════════════════════════════════════════════════════════════════════════════
"""
    return dossier


class SchedulingConcierge:
    """Main class for Agent D functionality."""

    def __init__(self):
        self.pending_interviews = []

    def process_acceptance(
        self,
        candidate_name: str,
        candidate_email: str,
        current_firm: str,
        practice_area: str,
        frustration_score: int,
        frustration_reasons: str,
        portable_revenue: float,
    ) -> dict:
        """
        Process when a candidate accepts an interview request.

        Returns scheduling email and briefing dossier.
        """
        # Task 1: Find matching interviewer
        interviewer = find_matching_interviewer(practice_area)
        if not interviewer:
            return {"error": "No available interviewers for this niche"}

        # Task 2: Generate scheduling email
        scheduling_email = generate_scheduling_email(candidate_name)

        # Task 3: Generate briefing dossier
        briefing = generate_briefing_dossier(
            candidate_name=candidate_name,
            current_firm=current_firm,
            practice_area=practice_area,
            frustration_score=frustration_score,
            frustration_reasons=frustration_reasons,
            portable_revenue=portable_revenue,
            interviewer_name=interviewer["name"],
        )

        return {
            "status": "success",
            "interviewer": interviewer,
            "scheduling_email": scheduling_email,
            "briefing_dossier": briefing,
        }


# Example Usage
if __name__ == "__main__":
    print("=" * 80)
    print("AGENT D: SCHEDULING CONCIERGE")
    print("=" * 80)

    concierge = SchedulingConcierge()

    # Simulate candidate acceptance (data would come from Agent A & B)
    result = concierge.process_acceptance(
        candidate_name="Dr. Marcus Weber",
        candidate_email="m.weber@hengeler.com",
        current_firm="Hengeler Mueller",
        practice_area="Restructuring",
        frustration_score=85,
        frustration_reasons="Counsel for 6 years at Tier-1 firm; Lead on major deals but not Partner; Up-or-Out policy",
        portable_revenue=280000,
    )

    if result["status"] == "success":
        print(f"\n✅ Matched with Interviewer: {result['interviewer']['name']}")
        print(f"   Specialty: {result['interviewer']['specialty']}")
        print(
            f"   Current Load: {result['interviewer']['interviews_this_week']}/{MAX_INTERVIEWS_PER_PARTNER_PER_WEEK} interviews this week"
        )

        print("\n" + "=" * 80)
        print("📧 SCHEDULING EMAIL (Send to Candidate)")
        print("=" * 80)
        print(result["scheduling_email"])

        print("\n" + "=" * 80)
        print("📋 BRIEFING DOSSIER (Send to Interviewer)")
        print("=" * 80)
        print(result["briefing_dossier"])
    else:
        print(f"Error: {result['error']}")
