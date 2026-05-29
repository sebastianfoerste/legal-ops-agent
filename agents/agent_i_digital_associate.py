"""
Agent I: The "Digital Associate"
Purpose: Perform legal grunt work - review NDAs/contracts against playbook.
"""

import json
import os

# Add parent directory to path to resolve src config
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.gemini_client import client

SYSTEM_PROMPT = """
You are a Senior Associate at a top-tier law firm. Review the attached document.

TASK: Compare against the 'ApexLaw Standard Playbook' and create a 'Red Flag Report'.

OUTPUT FORMAT (JSON):
{
  "document_type": "NDA/Service Agreement/etc",
  "red_flags": [
    {
      "clause": "Name of clause (e.g., Indemnity)",
      "risk_level": "HIGH/MEDIUM/LOW",
      "current_text": "The problematic text",
      "suggested_edit": "Your redline/fix",
      "explanation": "Why this matters for the client's business"
    }
  ],
  "overall_risk": "HIGH/MEDIUM/LOW",
  "summary": "2-3 sentence executive summary"
}

CONSTRAINT: Be commercially pragmatic. Do NOT flag minor stylistic issues.
Focus on: unlimited liability, broad indemnities, IP assignment, non-compete, termination rights.
"""


def review_contract(contract_text: str, contract_type: str = "NDA") -> dict:
    """Review a contract and generate a Red Flag Report."""

    prompt = f"""
    {SYSTEM_PROMPT}
    
    DOCUMENT TYPE: {contract_type}
    
    DOCUMENT TEXT:
    {contract_text[:15000]}
    
    Generate the Red Flag Report as valid JSON.
    """

    try:
        response = client.models.generate_content(model="gemini-3-pro", contents=prompt)

        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        return json.loads(text.strip())
    except Exception as e:
        return {"error": str(e)}


def format_red_flag_report(report: dict) -> str:
    """Format the report for display."""
    if "error" in report:
        return f"Error: {report['error']}"

    output = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    RED FLAG REPORT                               ║
║                    Agent I: Digital Associate                    ║
╠══════════════════════════════════════════════════════════════════╣
║ Document: {report.get("document_type", "Unknown"):<52} ║
║ Overall Risk: {report.get("overall_risk", "Unknown"):<48} ║
╠══════════════════════════════════════════════════════════════════╣

📋 SUMMARY:
{report.get("summary", "No summary")}

🚩 RED FLAGS:
"""

    for i, flag in enumerate(report.get("red_flags", []), 1):
        risk_icon = (
            "🔴"
            if flag["risk_level"] == "HIGH"
            else "🟡"
            if flag["risk_level"] == "MEDIUM"
            else "🟢"
        )
        output += f"""
{risk_icon} #{i}: {flag["clause"]} [{flag["risk_level"]}]
   Current: "{flag.get("current_text", "N/A")[:100]}..."
   Fix: "{flag.get("suggested_edit", "N/A")[:100]}..."
   Why: {flag.get("explanation", "N/A")}
"""

    return output


if __name__ == "__main__":
    sample_nda = """
    MUTUAL NON-DISCLOSURE AGREEMENT
    
    1. CONFIDENTIAL INFORMATION
    Each party agrees to hold in confidence all information disclosed by the other party.
    
    2. INDEMNIFICATION
    The Receiving Party shall indemnify, defend, and hold harmless the Disclosing Party 
    from any and all claims, damages, losses, costs, and expenses (including unlimited 
    attorney's fees) arising from any breach of this Agreement.
    
    3. TERM
    This Agreement shall remain in effect for a period of 5 years. The confidentiality 
    obligations shall survive termination indefinitely.
    
    4. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of Delaware.
    
    5. LIMITATION OF LIABILITY
    [Intentionally left blank]
    """

    print("=" * 70)
    print("AGENT I: DIGITAL ASSOCIATE")
    print("=" * 70)

    report = review_contract(sample_nda, "Mutual NDA")
    print(format_red_flag_report(report))
