"""
Agent F: The "Thought Leader" Ghostwriter
Purpose: Turn signals from Agent E into LinkedIn posts.
"""

import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

SYSTEM_PROMPT = """
You are a LinkedIn Ghostwriter for a senior Gunnercooke Partner.

VOICE:
- Direct, authoritative, but not arrogant
- "Tacheles" (straight-talking)
- Empathetic to the pressures mid-sized company CEOs face
- Never salesy, always value-first

INPUT: A topic brief from the Signal Hunter (Agent E)

STRUCTURE (MUST FOLLOW):
1. **Hook** (Lines 1-3): A contrarian statement or a hard question about the topic.
   - Example: "Why the new LkSG ruling is a trap for CEOs."
   - NO hashtags in the first 3 lines!
   
2. **Insight** (Lines 4-10): 3 bullet points explaining the BUSINESS IMPACT, not the legal theory.
   - Use emojis sparingly but effectively
   - Focus on €, risk, and time
   
3. **The Pivot** (Lines 11-13): How the Gunnercooke 'Seniority' model solves this better.
   - Example: "You need a senior advisor, not a junior memo."
   
4. **CTA** (Final line): "DM me for the checklist." or similar

CONSTRAINTS:
- Maximum 1,500 characters total
- Use line breaks for readability (LinkedIn rewards this)
- NO hashtags in the first 3 lines
- Hashtags only at the very end (max 3-5)

OUTPUT FORMAT (JSON):
{
  "linkedin_post": "The full post text with proper line breaks",
  "character_count": 1234,
  "hashtags": ["#LkSG", "#Mittelstand", "#Compliance"]
}
"""


def generate_linkedin_post(signal: dict, partner_name: str = "Senior Partner") -> dict:
    """
    Generate a LinkedIn post from a Signal Hunter brief.

    Args:
        signal: Dict from Agent E with headline, business_pain, suggested_angle, etc.
        partner_name: Name of the partner for voice calibration

    Returns:
        JSON with the LinkedIn post
    """

    prompt = f"""
    {SYSTEM_PROMPT}
    
    SIGNAL INPUT:
    Headline: {signal.get("headline", "Unknown topic")}
    Regulation/Event: {signal.get("regulation_or_event", "N/A")}
    Business Pain: {signal.get("business_pain", "N/A")}
    Target Audience: {signal.get("target_audience", "N/A")}
    Suggested Angle: {signal.get("suggested_angle", "N/A")}
    Urgency: {signal.get("urgency", "MEDIUM")}
    
    PARTNER NAME: {partner_name}
    
    Generate the LinkedIn post as valid JSON. Remember: max 1,500 characters, contrarian hook, business focus, Gunnercooke pivot.
    """

    try:
        response = client.models.generate_content(model="gemini-3-pro", contents=prompt)

        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        result = json.loads(text.strip())
        return result
    except Exception as e:
        return {"error": str(e)}


def format_post_preview(post_data: dict) -> str:
    """Format the post for preview."""
    if "error" in post_data:
        return f"Error: {post_data['error']}"

    post = post_data.get("linkedin_post", "")
    chars = post_data.get("character_count", len(post))
    hashtags = post_data.get("hashtags", [])

    preview = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        LINKEDIN POST PREVIEW                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣

{post}

╠══════════════════════════════════════════════════════════════════════════════╣
║  📊 Characters: {chars}/1500                                                  
║  🏷️  Hashtags: {", ".join(hashtags)}
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    return preview


def process_signals_batch(signals: list, partner_name: str = "Senior Partner") -> list:
    """
    Process multiple signals and generate posts for each.

    Args:
        signals: List of signals from Agent E
        partner_name: Partner whose voice to use

    Returns:
        List of generated posts
    """
    posts = []
    for signal in signals:
        print(f"  Generating post for: {signal.get('headline', 'Unknown')[:40]}...")
        post = generate_linkedin_post(signal, partner_name)
        posts.append({"signal": signal, "post": post})
    return posts


if __name__ == "__main__":
    print("=" * 80)
    print("AGENT F: THOUGHT LEADER GHOSTWRITER")
    print("=" * 80)

    # Example signal (would normally come from Agent E)
    sample_signal = {
        "headline": "New LkSG Enforcement Wave Hits Mittelstand",
        "regulation_or_event": "German Supply Chain Due Diligence Act (LkSG)",
        "business_pain": "Mid-sized manufacturers are receiving BAFA enforcement letters demanding full supply chain audits within 30 days. Many lack the internal resources to comply, facing fines up to 2% of global revenue.",
        "target_audience": "CEOs and Compliance Officers of manufacturing companies with 1,000+ employees",
        "suggested_angle": "The hidden cost isn't the fine – it's the operational disruption of a rushed compliance project",
        "urgency": "HIGH",
    }

    print("\n📝 Generating LinkedIn Post...")
    post = generate_linkedin_post(sample_signal, "Sebastian Förster")
    print(format_post_preview(post))

    print("\n--- RAW JSON ---")
    print(json.dumps(post, indent=2, ensure_ascii=False))
