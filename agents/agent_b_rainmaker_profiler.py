"""
Agent B: The "Rainmaker" Profiler
Purpose: Validate the business case (revenue potential) of a candidate by estimating their Portable Book of Business.
"""

import json
import os
import sys

# Add parent directory to path to resolve src config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import GEMINI_3_PRO
from src.gemini_client import client

# Revenue thresholds
MIN_PORTABLE_REVENUE = 200_000  # €200k threshold for "Go"
HOURLY_RATE = 350  # €350/hour average

# Portability Discounts
INSTITUTIONAL_DISCOUNT = 0.80  # 80% discount (only 20% portable)
RELATIONSHIP_DISCOUNT = 0.20  # 20% discount (80% portable)

SYSTEM_PROMPT = """
You are a Financial Analyst for ApexLaw Germany. I will provide you with a lawyer's Deal Sheet or public biography. Your goal is to estimate their 'Portable Book of Business'.

Analysis Instructions:

1. **Extract Clients**: List all recurring clients mentioned in the last 3 years.

2. **Classify Portability**: For each client, determine if it is likely:
   - 'Institutional Client' (loyal to the firm, e.g., Deutsche Bank, Daimler, Siemens) - Apply 80% discount (only 20% portable)
   - 'Relationship Client' (loyal to the lawyer, typically Mittelstand/SME, family offices, startups) - Apply 20% discount (80% portable)

3. **Revenue Estimation**: 
   - Assume an average hourly rate of €350
   - Estimate the hours required for the listed matters
   - Calculate: Estimated_Revenue = Hours × €350 × Portability_Factor

4. **The Strategy**: We are looking for partners who can bring >€200,000 in immediate portable revenue.

Output Format - Return a JSON object:
{
  "candidate_name": "...",
  "clients": [
    {
      "name": "...",
      "type": "Institutional" or "Relationship",
      "estimated_hours_per_year": ...,
      "gross_revenue": ...,
      "portability_factor": ...,
      "portable_revenue": ...
    }
  ],
  "total_gross_revenue": ...,
  "total_portable_revenue": ...,
  "recommendation": "GO" or "NO GO",
  "reasoning": "..."
}
"""


def analyze_book_of_business(deal_sheet: str, candidate_name: str = "Unknown") -> dict:
    """
    Analyzes a lawyer's deal sheet or biography to estimate portable revenue.

    Args:
        deal_sheet: Raw text containing their deals, clients, and matters
        candidate_name: Name of the candidate

    Returns:
        Business case memo as JSON
    """

    full_prompt = f"""
    {SYSTEM_PROMPT}
    
    CANDIDATE NAME: {candidate_name}
    
    DEAL SHEET / BIOGRAPHY:
    {deal_sheet}
    
    Provide your analysis as valid JSON. Be conservative in your estimates.
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


def generate_business_case_memo(analysis: dict) -> str:
    """
    Generates a human-readable Business Case Memo from the analysis.
    """
    if "error" in analysis:
        return f"Error in analysis: {analysis['error']}"

    name = analysis.get("candidate_name", "Unknown")
    total_portable = analysis.get("total_portable_revenue", 0)
    recommendation = analysis.get("recommendation", "UNKNOWN")
    reasoning = analysis.get("reasoning", "")
    clients = analysis.get("clients", [])

    memo = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    BUSINESS CASE MEMO                            ║
║                    ApexLaw Germany                           ║
╠══════════════════════════════════════════════════════════════════╣
║  Candidate: {name:<52} ║
╠══════════════════════════════════════════════════════════════════╣

📊 REVENUE ANALYSIS
───────────────────────────────────────────────────────────────────
"""

    for client in clients:
        client_type = "🏢" if client.get("type") == "Institutional" else "🤝"
        memo += f"""
{client_type} {client.get("name", "Unknown Client")}
   Type: {client.get("type", "Unknown")}
   Est. Hours/Year: {client.get("estimated_hours_per_year", 0):,}
   Gross Revenue: €{client.get("gross_revenue", 0):,.0f}
   Portability: {client.get("portability_factor", 0):.0%}
   → Portable Revenue: €{client.get("portable_revenue", 0):,.0f}
"""

    memo += f"""
───────────────────────────────────────────────────────────────────
💰 TOTAL PORTABLE REVENUE: €{total_portable:,.0f}
   Threshold: €200,000

{"✅" if recommendation == "GO" else "❌"} RECOMMENDATION: {recommendation}

📝 REASONING:
{reasoning}
───────────────────────────────────────────────────────────────────
"""
    return memo


# Manual estimation function for structured data
def estimate_portable_revenue_manual(clients: list) -> dict:
    """
    Manual calculation if you have structured client data.

    Args:
        clients: List of dicts with keys: name, type ('Institutional'/'Relationship'), hours_per_year

    Returns:
        Summary dict
    """
    total_gross = 0
    total_portable = 0

    for client in clients:
        hours = client.get("hours_per_year", 0)
        gross = hours * HOURLY_RATE

        if client.get("type") == "Institutional":
            portable = gross * (1 - INSTITUTIONAL_DISCOUNT)
        else:
            portable = gross * (1 - RELATIONSHIP_DISCOUNT)

        client["gross_revenue"] = gross
        client["portable_revenue"] = portable

        total_gross += gross
        total_portable += portable

    return {
        "clients": clients,
        "total_gross_revenue": total_gross,
        "total_portable_revenue": total_portable,
        "recommendation": "GO" if total_portable >= MIN_PORTABLE_REVENUE else "NO GO",
        "reasoning": f"Portable revenue of €{total_portable:,.0f} {'exceeds' if total_portable >= MIN_PORTABLE_REVENUE else 'is below'} €200k threshold.",
    }


# Example Usage
if __name__ == "__main__":
    sample_deal_sheet = """
    Dr. Marcus Vance - Counsel, Helm & Mueller Düsseldorf
    
    Practice Areas: Restructuring, Distressed M&A, Insolvency
    
    Selected Matters (2022-2025):
    
    1. Galeria Karstadt Kaufhof (2023)
       - Role: Key Contact for creditor committee
       - Client: Major German retail bank (institutional)
       - Estimated: 800 hours
    
    2. Wirecard Insolvency Administration (2022-ongoing)
       - Role: Senior team member
       - Client: Insolvency administrator (institutional)
       - Estimated: 500 hours/year
    
    3. Mittelstand Manufacturing Group Restructuring (2024)
       - Role: Lead restructuring advisor
       - Client: Family-owned manufacturing company, 3rd generation (relationship)
       - Estimated: 600 hours
       - Note: Long-standing personal relationship with CEO
    
    4. Tech Startup Debt Restructuring (2024)
       - Role: Lead advisor
       - Client: Berlin-based FinTech (relationship, founder is personal contact)
       - Estimated: 300 hours
    
    5. Renewable Energy Project Finance Restructuring (2025)
       - Role: Key Contact
       - Client: Family Office from Munich (relationship)
       - Estimated: 400 hours
    
    Chambers & Partners: "A technically excellent lawyer who clients trust implicitly."
    """

    print("=" * 70)
    print("AGENT B: RAINMAKER PROFILER")
    print("=" * 70)
    print("\nAnalyzing Portable Book of Business...\n")

    analysis = analyze_book_of_business(sample_deal_sheet, "Dr. Marcus Vance")
    memo = generate_business_case_memo(analysis)
    print(memo)

    # Also save the raw JSON
    print("\n--- RAW JSON ANALYSIS ---")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
