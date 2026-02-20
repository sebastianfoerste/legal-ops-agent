"""
Agent L: The "Insolvency" Deal Finder
Purpose: Find business for the Restructuring practice by monitoring insolvency filings.
"""

import time
from datetime import datetime

from ddgs import DDGS

# Mock CRM data (in production: Salesforce/Elite 3E API)
PARTNER_RELATIONSHIPS = {
    "Dr. Thomas Richter": ["Dr. Michael Schmidt (Insolvenzverwalter)", "Kanzlei Müller & Partner"],
    "Anna Weber": ["Dr. Klaus Hoffmann", "Schultze & Braun"],
    "Dr. Marcus Weber": ["Dr. Stefan Weniger", "hww hermann wienberg wilhelm"],
}

KNOWN_ADMINISTRATORS = [
    {"name": "Dr. Michael Schmidt", "firm": "Schmidt Insolvenz"},
    {"name": "Dr. Klaus Hoffmann", "firm": "Hoffmann & Partner"},
    {"name": "Dr. Stefan Weniger", "firm": "Weniger & Kollegen"},
    {"name": "Schultze & Braun", "firm": "Schultze & Braun"},
]


def scan_insolvency_filings() -> list:
    """
    Monitor for new preliminary insolvency filings.
    In production, this would scrape insolvenzbekanntmachungen.de
    """
    print("📡 Scanning Insolvency Registers...")

    results = []
    keywords = [
        "vorläufige Insolvenzverwaltung 2026",
        "Insolvenzverfahren eröffnet",
        "Insolvenz Automobilindustrie",
        "Insolvenz Bauunternehmen",
    ]

    with DDGS() as ddgs:
        for kw in keywords:
            try:
                news = ddgs.news(kw, region="de-de", max_results=3)
                for item in news:
                    results.append(
                        {
                            "title": item.get("title"),
                            "body": item.get("body"),
                            "url": item.get("url"),
                            "date": item.get("date"),
                            "keyword": kw,
                        }
                    )
                time.sleep(1)
            except Exception as e:
                print(f"  Error: {e}")

    return results


def extract_filing_details(filing: dict) -> dict:
    """Extract company and administrator from filing."""
    # In production, this would use NER or structured parsing
    title = filing.get("title", "")
    body = filing.get("body", "")

    return {
        "company": title.split(":")[0] if ":" in title else title[:50],
        "summary": body[:200] if body else "No details",
        "url": filing.get("url"),
        "date": filing.get("date"),
    }


def check_partner_relationships(administrator: str) -> list:
    """Check if any Gunnercooke partner knows this administrator."""
    matches = []
    admin_lower = administrator.lower()

    for partner, relationships in PARTNER_RELATIONSHIPS.items():
        for rel in relationships:
            if admin_lower in rel.lower() or rel.lower() in admin_lower:
                matches.append(
                    {
                        "partner": partner,
                        "known_contact": rel,
                        "relationship_type": "Past matter / Professional network",
                    }
                )

    return matches


def generate_slack_alert(filing: dict, match: dict) -> str:
    """Generate Slack alert message."""
    return f"""
🚨 *NEW INSOLVENCY FILING ALERT*

*Company:* {filing.get("company", "Unknown")}
*Date:* {filing.get("date", "Unknown")}
*Summary:* {filing.get("summary", "N/A")}

👤 *Your Connection:* {match.get("known_contact", "N/A")}
🔗 *Relationship:* {match.get("relationship_type", "N/A")}

📌 *Action:* Reach out NOW to offer support services.

<{filing.get("url", "#")}|View Filing>
"""


def run_deal_finder() -> list:
    """Main function to scan for deals."""
    print("=" * 60)
    print("AGENT L: INSOLVENCY DEAL FINDER")
    print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Scan filings
    filings = scan_insolvency_filings()
    print(f"\n📋 Found {len(filings)} potential filings")

    alerts = []

    for filing in filings:
        details = extract_filing_details(filing)

        # Check for known administrators in the text
        for admin in KNOWN_ADMINISTRATORS:
            if (
                admin["name"].lower()
                in (details.get("summary", "") + details.get("company", "")).lower()
            ):
                # Found an administrator we know - check partner relationships
                matches = check_partner_relationships(admin["name"])

                for match in matches:
                    alert = {
                        "filing": details,
                        "administrator": admin,
                        "partner_match": match,
                        "slack_message": generate_slack_alert(details, match),
                    }
                    alerts.append(alert)
                    print("\n🎯 MATCH FOUND!")
                    print(f"   Company: {details['company']}")
                    print(f"   Admin: {admin['name']}")
                    print(f"   → Alert Partner: {match['partner']}")

    if not alerts:
        print("\n📭 No matches with known administrators found this scan.")

    return alerts


if __name__ == "__main__":
    alerts = run_deal_finder()

    if alerts:
        print("\n" + "=" * 60)
        print("📱 SLACK ALERTS TO SEND:")
        print("=" * 60)
        for a in alerts:
            print(a["slack_message"])
