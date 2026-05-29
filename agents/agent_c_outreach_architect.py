"""
Agent C: The Outreach Architect
Purpose: Write hyper-personalized outreach messages that convert.
"""

import json
import os
import sys

# Add parent directory to path to resolve src config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import GEMINI_3_PRO
from src.gemini_client import client

SYSTEM_PROMPT = """
You are the Ghostwriter for the Managing Partner of ApexLaw Germany. You are writing a direct message to a senior lawyer at a competitor firm.

TONE GUIDELINES:
- Professional, 'Tacheles' (direct/plain-speaking), peer-to-peer
- Empathetic to the frustrations of Big Law
- Do NOT use HR buzzwords like 'exciting opportunity', 'great culture', 'innovative environment', or 'dynamic team'
- Write like a peer, not a recruiter

STRUCTURE:
1. **The Hook**: Acknowledge their specific recent success (deal, publication, speaking engagement). Pivot immediately to the 'Sovereign Seniority' value proposition: "You did the work, but did you capture the value?"

2. **The Call to Action**: Ask for a 5-minute virtual coffee to discuss 'autonomy' and 'net revenue share'. Keep the message under 100 words.

3. **Constraint**: End with a P.S. that mentions the specific 'Netto-Rechner' (Income Calculator) concept.

OUTPUT FORMAT:
Return a JSON object:
{
  "subject_line": "...",
  "message_body": "...",
  "ps_line": "...",
  "character_count": ...
}

Keep the total message (body + P.S.) under 100 words.
"""


def generate_outreach(
    candidate_name: str,
    current_firm: str,
    recent_achievement: str,
    practice_area: str,
    sender_name: str = "Managing Partner",
) -> dict:
    """
    Generates a hyper-personalized outreach message.

    Args:
        candidate_name: Name of the target candidate
        current_firm: Their current firm
        recent_achievement: A specific deal, award, or publication to reference
        practice_area: Their specialty
        sender_name: Name of the sender (ApexLaw partner)

    Returns:
        JSON with message components
    """

    full_prompt = f"""
    {SYSTEM_PROMPT}
    
    CANDIDATE CONTEXT:
    - Name: {candidate_name}
    - Current Firm: {current_firm}
    - Practice Area: {practice_area}
    - Recent Achievement: {recent_achievement}
    
    SENDER: {sender_name}, Managing Partner, ApexLaw Germany
    
    Generate the outreach message as valid JSON. Remember: max 100 words total, peer-to-peer tone, reference the Netto-Rechner.
    """

    try:
        response = client.models.generate_content(model=GEMINI_3_PRO, contents=full_prompt)

        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        result = json.loads(text.strip())
        return result
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_response": response.text}
    except Exception as e:
        return {"error": str(e)}


def format_linkedin_message(outreach: dict) -> str:
    """Formats the outreach for copy-paste into LinkedIn."""
    if "error" in outreach:
        return f"Error: {outreach['error']}"

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 LINKEDIN MESSAGE (Copy-Paste Ready)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{outreach.get("message_body", "")}

{outreach.get("ps_line", "")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Stats: {outreach.get("character_count", "N/A")} characters
📌 Subject (if email): {outreach.get("subject_line", "N/A")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# Batch outreach for multiple candidates
def generate_batch_outreach(candidates: list) -> list:
    """
    Generate outreach for multiple candidates.

    Args:
        candidates: List of dicts with keys: name, firm, achievement, practice_area

    Returns:
        List of outreach messages
    """
    results = []
    for c in candidates:
        outreach = generate_outreach(
            c.get("name"), c.get("firm"), c.get("achievement"), c.get("practice_area")
        )
        results.append({"candidate": c.get("name"), "outreach": outreach})
    return results


# Example Usage
if __name__ == "__main__":
    print("=" * 70)
    print("AGENT C: OUTREACH ARCHITECT")
    print("=" * 70)

    # Example candidate from Agent A's output
    outreach = generate_outreach(
        candidate_name="Dr. Marcus Vance",
        current_firm="Helm & Mueller",
        recent_achievement="Lead advisory role on the €120m restructuring of a major German retail group in 2024",
        practice_area="Restructuring & Insolvency",
        sender_name="Alex Vancer",
    )

    print(format_linkedin_message(outreach))

    print("\n--- RAW JSON ---")
    print(json.dumps(outreach, indent=2, ensure_ascii=False))
