"""
Agent E: The "Signal Hunter"
Purpose: Find relevant topics for partners to write about by monitoring regulatory feeds,
insolvency registers, and competitor blogs.
"""

import json
import os
import time
from datetime import datetime

from ddgs import DDGS
from dotenv import load_dotenv
from google import genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

# Monitoring Configuration
REGULATORY_KEYWORDS = [
    "MiCAR Verordnung",
    "DORA Regulation Germany",
    "LkSG Lieferkettengesetz",
    "Supply Chain Due Diligence Act",
    "Digital Operational Resilience Act",
    "Markets in Crypto Assets Regulation",
]

INSOLVENCY_KEYWORDS = [
    "Insolvenz Automobilindustrie",
    "Insolvenz Bauunternehmen",
    "vorläufige Insolvenzverwaltung",
    "insolvency filing Germany automotive",
    "construction company insolvency Germany",
]

COMPETITOR_BLOGS = [
    "site:freshfields.com/insights",
    "site:hengeler.com/aktuelles",
    "site:ypog.law/news",
    "site:noerr.com/insights",
]

SYSTEM_PROMPT = """
You are a Legal Market Scout for Gunnercooke Germany.

I will provide you with a news item or regulatory update. Your task is to:

1. **Identify the Business Implication**: Do NOT summarize the law. Instead, summarize the PAIN it causes for a mid-sized German company (Mittelstand).

2. **Generate Topic Brief**: Create a topic brief for a Gunnercooke Partner to write about.

Output Format (JSON):
{
  "headline": "Short, punchy headline for internal use",
  "regulation_or_event": "Name of the regulation or event",
  "business_pain": "2-3 sentences describing the specific pain point for a mid-sized German CEO",
  "target_audience": "Who should care (e.g., CFOs of manufacturing companies)",
  "suggested_angle": "The contrarian or 'insider' angle a partner could take",
  "urgency": "HIGH / MEDIUM / LOW",
  "source_url": "Original source URL"
}
"""


def scan_regulatory_feeds() -> list:
    """Scan for regulatory updates."""
    results = []

    with DDGS() as ddgs:
        for keyword in REGULATORY_KEYWORDS:
            try:
                news = ddgs.news(keyword, region="de-de", max_results=3)
                for item in news:
                    results.append(
                        {
                            "type": "regulatory",
                            "keyword": keyword,
                            "title": item.get("title"),
                            "body": item.get("body"),
                            "url": item.get("url"),
                            "date": item.get("date"),
                        }
                    )
                time.sleep(1)
            except Exception as e:
                print(f"  Error scanning '{keyword}': {e}")

    return results


def scan_insolvency_news() -> list:
    """Scan for major insolvency filings."""
    results = []

    with DDGS() as ddgs:
        for keyword in INSOLVENCY_KEYWORDS:
            try:
                news = ddgs.news(keyword, region="de-de", max_results=3)
                for item in news:
                    results.append(
                        {
                            "type": "insolvency",
                            "keyword": keyword,
                            "title": item.get("title"),
                            "body": item.get("body"),
                            "url": item.get("url"),
                            "date": item.get("date"),
                        }
                    )
                time.sleep(1)
            except Exception as e:
                print(f"  Error scanning '{keyword}': {e}")

    return results


def scan_competitor_blogs() -> list:
    """Scan competitor law firm blogs."""
    results = []

    with DDGS() as ddgs:
        for site_query in COMPETITOR_BLOGS:
            try:
                search_results = ddgs.text(site_query, region="de-de", max_results=3)
                for item in search_results:
                    results.append(
                        {
                            "type": "competitor",
                            "source": site_query.split("site:")[1].split("/")[0]
                            if "site:" in site_query
                            else "Unknown",
                            "title": item.get("title"),
                            "body": item.get("body"),
                            "url": item.get("href"),
                        }
                    )
                time.sleep(1)
            except Exception as e:
                print(f"  Error scanning '{site_query}': {e}")

    return results


def analyze_signal(signal: dict) -> dict:
    """
    Use Gemini to analyze a signal and extract the business pain.
    """
    prompt = f"""
    {SYSTEM_PROMPT}
    
    NEWS ITEM:
    Type: {signal.get("type", "Unknown")}
    Title: {signal.get("title", "No title")}
    Summary: {signal.get("body", "No summary")}
    URL: {signal.get("url", "No URL")}
    
    Analyze this and return valid JSON.
    """

    try:
        response = client.models.generate_content(model="gemini-1.5-pro", contents=prompt)

        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        return json.loads(text.strip())
    except Exception as e:
        return {"error": str(e), "raw_signal": signal}


def run_signal_hunter() -> list:
    """
    Main function to run the signal hunter.
    Returns list of analyzed signals ready for Agent F.
    """
    print("=" * 70)
    print("AGENT E: SIGNAL HUNTER")
    print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    all_signals = []

    # Scan all sources
    print("\n📡 Scanning Regulatory Feeds...")
    reg_signals = scan_regulatory_feeds()
    print(f"   Found {len(reg_signals)} regulatory signals")
    all_signals.extend(reg_signals)

    print("\n📡 Scanning Insolvency News...")
    insolvency_signals = scan_insolvency_news()
    print(f"   Found {len(insolvency_signals)} insolvency signals")
    all_signals.extend(insolvency_signals)

    print("\n📡 Scanning Competitor Blogs...")
    competitor_signals = scan_competitor_blogs()
    print(f"   Found {len(competitor_signals)} competitor signals")
    all_signals.extend(competitor_signals)

    # Deduplicate by URL
    seen_urls = set()
    unique_signals = []
    for s in all_signals:
        url = s.get("url", s.get("href", ""))
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_signals.append(s)

    print(f"\n📊 Total Unique Signals: {len(unique_signals)}")

    # Analyze top signals
    analyzed = []
    print("\n🔬 Analyzing top signals with Gemini...")

    for signal in unique_signals[:5]:  # Analyze top 5 to save API calls
        print(f"   Analyzing: {signal.get('title', 'Unknown')[:50]}...")
        analysis = analyze_signal(signal)
        if "error" not in analysis:
            analyzed.append(analysis)

    return analyzed


def format_signal_report(signals: list) -> str:
    """Format signals as a readable report."""
    report = "\n" + "=" * 70 + "\n"
    report += "📋 SIGNAL HUNTER REPORT\n"
    report += "=" * 70 + "\n"

    for i, s in enumerate(signals, 1):
        urgency_icon = (
            "🔴" if s.get("urgency") == "HIGH" else "🟡" if s.get("urgency") == "MEDIUM" else "🟢"
        )

        report += f"""
{urgency_icon} SIGNAL #{i}: {s.get("headline", "Unknown")}
───────────────────────────────────────────────────────────────────────
📌 Regulation/Event: {s.get("regulation_or_event", "N/A")}
😰 Business Pain: {s.get("business_pain", "N/A")}
🎯 Target Audience: {s.get("target_audience", "N/A")}
💡 Suggested Angle: {s.get("suggested_angle", "N/A")}
⏰ Urgency: {s.get("urgency", "N/A")}
🔗 Source: {s.get("source_url", "N/A")}
"""

    return report


if __name__ == "__main__":
    signals = run_signal_hunter()
    print(format_signal_report(signals))

    # Save signals for Agent F
    output_path = "signal_hunter_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved {len(signals)} signals to {output_path}")
