"""
Agent A: The "Glass Ceiling" Scout
Purpose: Identify high-potential candidates blocked from partnership at Tier-1 firms.
"""

import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

# Tier-1 Firm List (German Market)
TIER_1_FIRMS = [
    "Freshfields", "Hengeler Mueller", "Kirkland & Ellis", "Latham & Watkins",
    "Sullivan & Cromwell", "Skadden", "Linklaters", "Clifford Chance",
    "Allen & Overy", "White & Case", "Gleiss Lutz", "Noerr", "CMS", "Hogan Lovells"
]

UP_OR_OUT_FIRMS = ["Freshfields", "Linklaters", "Clifford Chance", "Allen & Overy", "Latham & Watkins", "Kirkland & Ellis"]

SYSTEM_PROMPT = """
You are an expert Executive Search Researcher for Gunnercooke Germany. Your objective is to identify 'undervalued assets' in the German legal market based on the 'Glass Ceiling' hypothesis.

Your Task:
Analyze the provided list of lawyer profiles and assign a 'Frustration Score' (0-100) to each based on the following logic:

1. **Tenure Check**: Identify lawyers with the titles 'Counsel', 'Senior Associate', or 'Principal Associate'. If they have held this title for >5 years at the same Tier-1 firm (e.g., Freshfields, Hengeler, Kirkland), add 30 points.

2. **Deal Activity**: Specific to the 'Crypto/FinTech' or 'Restructuring' sectors. If they are listed as 'Key Contact' or 'Lead' on deals >€20m but are not a Partner, add 40 points.

3. **Firm Structure**: If the firm has a known 'Up-or-Out' policy or recently appointed new Equity Partners in the same practice group (excluding this candidate), add 30 points.

Output Format:
Return a JSON array. For each candidate with a score >70, include:
{
  "Name": "...",
  "Current_Firm": "...",
  "Years_in_Role": ...,
  "Estimated_Book_of_Business": "...",
  "Frustration_Score": ...,
  "Reason_for_Score": "..."
}

IMPORTANT: Only output candidates with a Frustration Score >70. Return valid JSON only.
"""

def analyze_profiles(profiles_text: str) -> dict:
    """
    Analyzes lawyer profiles and returns frustration scores.
    
    Args:
        profiles_text: Raw text containing lawyer profiles (from LinkedIn, JUVE, Legal 500, etc.)
    
    Returns:
        JSON object with scored candidates
    """
    
    # Enrich the prompt with firm context
    firm_context = f"""
    Known Tier-1 Firms: {', '.join(TIER_1_FIRMS)}
    Firms with Up-or-Out Policy: {', '.join(UP_OR_OUT_FIRMS)}
    """
    
    full_prompt = f"""
    {SYSTEM_PROMPT}
    
    FIRM CONTEXT:
    {firm_context}
    
    CANDIDATE PROFILES TO ANALYZE:
    {profiles_text}
    
    Return your analysis as a JSON array. If no candidates score >70, return an empty array [].
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3-pro',
            contents=full_prompt
        )
        
        # Extract JSON from response
        text = response.text
        # Clean potential markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_response": response.text}
    except Exception as e:
        return {"error": str(e)}

def score_candidate_manual(candidate: dict) -> dict:
    """
    Manual scoring logic if you have structured data.
    
    Args:
        candidate: Dict with keys like 'name', 'firm', 'title', 'years_in_role', 'deals', 'practice_area'
    
    Returns:
        Scored candidate dict
    """
    score = 0
    reasons = []
    
    # 1. Tenure Check
    title = candidate.get('title', '').lower()
    years = candidate.get('years_in_role', 0)
    firm = candidate.get('firm', '')
    
    blocked_titles = ['counsel', 'senior associate', 'principal associate', 'of counsel']
    is_blocked_title = any(t in title for t in blocked_titles)
    is_tier_1 = any(f.lower() in firm.lower() for f in TIER_1_FIRMS)
    
    if is_blocked_title and years > 5 and is_tier_1:
        score += 30
        reasons.append(f"Held '{title}' for {years} years at Tier-1 firm {firm}")
    
    # 2. Deal Activity
    practice = candidate.get('practice_area', '').lower()
    deals = candidate.get('deals', [])
    hot_sectors = ['crypto', 'fintech', 'restructuring', 'blockchain', 'digital assets']
    
    is_hot_sector = any(s in practice for s in hot_sectors)
    has_lead_deals = any(d.get('role', '').lower() in ['lead', 'key contact'] and d.get('value', 0) > 20_000_000 for d in deals)
    
    if is_hot_sector and has_lead_deals and 'partner' not in title:
        score += 40
        reasons.append(f"Lead on major deals in {practice} but not Partner")
    
    # 3. Firm Structure
    is_up_or_out = any(f.lower() in firm.lower() for f in UP_OR_OUT_FIRMS)
    recent_partner_promotions = candidate.get('recent_partner_promotions_in_group', False)
    
    if is_up_or_out or recent_partner_promotions:
        score += 30
        if is_up_or_out:
            reasons.append(f"{firm} has Up-or-Out policy")
        if recent_partner_promotions:
            reasons.append("Recent partner promotions in same group (passed over)")
    
    return {
        "Name": candidate.get('name'),
        "Current_Firm": firm,
        "Years_in_Role": years,
        "Estimated_Book_of_Business": candidate.get('estimated_book', 'Unknown'),
        "Frustration_Score": score,
        "Reason_for_Score": "; ".join(reasons) if reasons else "Below threshold"
    }

def filter_high_potential(candidates: list) -> list:
    """Filter to only high-potential candidates (score >70)"""
    return [c for c in candidates if c.get('Frustration_Score', 0) > 70]


# Example Usage
if __name__ == "__main__":
    # Demo with sample profiles text (in production, this would come from LinkedIn/JUVE scraping)
    sample_profiles = """
    1. Dr. Anna Müller
       - Firm: Freshfields Bruckhaus Deringer, Frankfurt
       - Title: Senior Associate (since 2018)
       - Practice: Banking & Finance, FinTech
       - Notable Deals: Lead on €50m crypto custody framework for major German bank
       - Bio: 8 years at Freshfields, recognized in Legal 500 as "Rising Star"
    
    2. Marcus Weber
       - Firm: Hengeler Mueller, Düsseldorf
       - Title: Counsel (since 2019)
       - Practice: M&A, Restructuring
       - Notable Deals: Key Contact on €120m restructuring of retail group
       - Bio: 10 years at Hengeler, passed over in 2023 partner round
    
    3. Dr. Lisa Schneider
       - Firm: CMS, Berlin
       - Title: Partner (since 2020)
       - Practice: Employment Law
       - Bio: Recently promoted, growing team
    """
    
    print("=" * 60)
    print("AGENT A: GLASS CEILING SCOUT")
    print("=" * 60)
    print("\nAnalyzing profiles for 'Frustration Score'...\n")
    
    results = analyze_profiles(sample_profiles)
    
    if isinstance(results, list):
        high_potential = [r for r in results if r.get('Frustration_Score', 0) > 70]
        print(f"Found {len(high_potential)} high-potential candidates (Score >70):\n")
        print(json.dumps(high_potential, indent=2, ensure_ascii=False))
    else:
        print("Analysis Results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
