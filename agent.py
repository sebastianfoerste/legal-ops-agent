import argparse
import os
import sys
import time
from datetime import datetime

import requests
import trafilatura
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from google import genai
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")


def brave_search_api(query: str):
    """Call Brave Search API directly."""
    if not BRAVE_API_KEY:
        return {}
    params = {"q": query}
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Brave API error: {e}")
    return {}


# Shared Intelligence Core
sys.path.append("/Users/sebastian/Developer/scripts")
try:
    from intelligence_core import BANNED_WORDS, apply_2026_standards
except ImportError:
    BANNED_WORDS = []

    def apply_2026_standards(text: str) -> str:
        return text


def search_legal_news(country="USA", max_results=5, topic=None):
    """
    Search for latest legal news using DuckDuckGo and Brave Search.
    Optional topic used to narrow the search.
    """
    # Define queries
    topic_str = f" {topic}" if topic else ""
    if country.lower() in ["germany", "de"]:
        primary_query = f"site:lto.de OR site:juve.de aktuelle jura nachrichten{topic_str}"
        secondary_query = f"aktuelle jura nachrichten deutschland anwalt rechtsprechung{topic_str}"
        fallback_query = f"aktuelle jura nachrichten deutschland anwalt{topic_str}"
        region = "de-de"
    else:
        primary_query = f"site:abajournal.com OR site:law.com legal news United States{topic_str}"
        secondary_query = f"legal news headlines United States{topic_str}"
        fallback_query = f"legal news headlines United States{topic_str}"
        region = "us-en"

    print(f"Searching for legal news in {country}...")
    results = []

    # --- 1. Primary: DuckDuckGo Specific ---
    try:
        with DDGS() as ddgs:
            # Narrow search to reliable domains for specific legal news
            ddg_results = ddgs.text(primary_query, region=region, max_results=max_results)
            if ddg_results:
                for r in ddg_results:
                    results.append(
                        {"title": r.get("title"), "href": r.get("href"), "body": r.get("body")}
                    )
                msg = (
                    f" Marcus Vane Intelligence: Analyzing {len(results)} "
                    f"news items for {country}..."
                )
                print(msg)
                return results
    except Exception as e:
        print(f"  ❌ DDG Specific failed: {e}")

    # --- 2. Secondary: DuckDuckGo Broad ---
    try:
        time.sleep(2)
        with DDGS() as ddgs:
            # Broad search for current legal headlines
            ddg_results = ddgs.text(secondary_query, region=region, max_results=max_results)
            if ddg_results:
                for r in ddg_results:
                    results.append(
                        {"title": r.get("title"), "href": r.get("href"), "body": r.get("body")}
                    )
                print(f"  ✅ DDG Broad found {len(results)} results.")
                return results
    except Exception as e:
        print(f"  ❌ DDG Broad failed: {e}")

    # --- 3. Fallback: Brave Search API ---
    print(f"Attempting Fallback Search (Brave API): {fallback_query}")
    try:
        data = brave_search_api(fallback_query)
        if data and "web" in data and "results" in data["web"]:
            for item in data["web"]["results"][:max_results]:
                results.append(
                    {
                        "title": item.get("title"),
                        "href": item.get("url"),
                        "body": item.get("description", ""),
                    }
                )

            if results:
                msg = (
                    f" Marcus Vane Strategy: Creating {len(results)} "
                    f"strategic content pieces for {country}..."
                )
                print(msg)
            else:
                print("  ⚠️ Brave Search found no parseable results.")
        else:
            print("  ⚠️ Brave Search returned no valid data.")

    except Exception as e:
        print(f"  ❌ Brave Search failed: {e}")

    return results


def scrape_content(url):
    """
    Extract main text from a URL using Trafilatura.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def is_relevant(text):
    """
    Detektiv für juristische Marktsignale. Er scannt News, Urteile und
    Marktbewegungen, um Business-Development-Chancen für Anwälte zu finden.
    """
    if not text or len(text) < 200:
        return False

    # Multi-model logic for relevance checking (candidate models not used in current implementation)
    try:
        # Use a cheaper/faster model for this check
        response = client.models.generate_content(
            model="gemini-flash-latest", contents=f"Is this article relevant? {text[:2000]}"
        )
        return "yes" in (response.text or "").lower()
    except Exception:
        return True  # Fallback to include if check fails


# --- 2026 MANIFESTO COMPLIANCE (INTEGRATED VIA intelligence_core.py) ---


def generate_linkedin_posts(articles_text, country):
    """
    Generate LinkedIn posts using Gemini with Manifesto Compliance.
    """
    print(f"Generating posts for {country}...")

    # Determine language based on country
    if country.lower() in ["germany", "de"]:
        lang_instr = "IMPORTANT: The output must be in **GERMAN**."
        country_model = "gemini-flash-latest"  # Example, adjust as needed
    else:
        lang_instr = "IMPORTANT: The output must be in **ENGLISH**."
        country_model = "gemini-flash-latest"  # Example, adjust as needed

    formatted_date = datetime.now().strftime("%Y-%m-%d")

    # High-status post generation
    # This prompt is for generating a single high-status post,
    # but the function is designed to generate three.
    # The original prompt structure is retained for multi-post generation.
    # prompt = f"Write a world-class high-status LinkedIn post about this: {articles_text[:6000]}"

    prompt = f"""
    You are Marcus Vane, an expert legal strategist known for being
    authoritative, cynical, and clarity-obsessed.
    Spezialist für Nischen-Positionierung. Er findet profitable Rechtsnischen
    und erstellt Content-Pläne, um den Anwalt dort als Platzhirsch zu etablieren.
    Ghostwriter für LinkedIn-Content. Er wandelt komplexe Urteile in 'Bro-etry'
    um – ein Satz pro Zeile, hohe Emotionalität, maximale Reichweite.
    Date: {formatted_date}

    Based on the following news relating to law in {country},
    create THREE distinct, high-status LinkedIn posts.

    {lang_instr}

    CORE PROTOCOLS:
    1. THE ANTI-ROBOT FILTER (CRITICAL):
       - BANNED: {", ".join(BANNED_WORDS)}
       - If you use these, the post is invalid. Use simple, sharp words instead.
    
    2. THE VIRAL SYNTAX (BRO-ETRY):
       - Formatting: EVERY SENTENCE must be its own paragraph.
       - Spacing: Use DOUBLE line breaks between EVERY single sentence.
    
    3. THE HOOK:
       - Start with a "Pattern Interrupt" or a cold open under 10 words.
    
    SOURCE TEXT:
    {articles_text[:30000]}
    
    OUTPUT FORMAT:
    Post 1:
    [Viral Content]
    IMAGE PROMPT: [Minimalist/Cinematic description]
    
    Post 2:
    [Viral Content]
    IMAGE PROMPT: [Minimalist/Cinematic description]
    
    Post 3:
    [Viral Content]
    IMAGE PROMPT: [Minimalist/Cinematic description]
    """

    # Multi-Model Fallback Chain

    for model_name in [country_model, "gemini-3-flash", "gemini-flash-latest"]:
        try:
            print(f"  Attempting generation with {model_name}...")
            response = client.models.generate_content(model=model_name, contents=prompt)

            if response.text:
                raw_text = response.text
                # Apply 2026 Compliance Layers
                final = apply_2026_standards(raw_text)
                return final
        except Exception as e:
            print(f"  ⚠️ {model_name} failed: {e}")
            continue

    return "Error: All models in fallback chain failed."


def show_phone_preview(posts_text):
    """Render posts in a terminal-based phone preview."""
    console = Console()
    # Split by "Post X:"
    chunks = []
    current_post = ""
    for line in posts_text.split("\n"):
        if line.startswith("Post ") and ":" in line:
            if current_post:
                chunks.append(current_post.strip())
            current_post = line + "\n"
        else:
            current_post += line + "\n"
    if current_post:
        chunks.append(current_post.strip())

    for i, content in enumerate(chunks):
        title = f"Post {i + 1} Preview (Mobile View)"
        # Strip the "Post X:" header for the panel body
        panel_body = content.split("\n", 1)[-1] if "\n" in content else content

        console.print("\n")
        console.print(
            Panel(
                Text(panel_body),
                title=f"[bold]📱 {title}[/]",
                width=50,
                padding=(1, 2),
                border_style="bright_blue",
                box=ROUNDED,
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description="Marcus Vane: AI Legal Strategist & Content Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--countries",
        nargs="+",
        default=["Germany", "USA"],
        help="List of countries to process news for",
    )
    parser.add_argument(
        "--max-results", type=int, default=5, help="Max news results to scrape per country"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode, prompting for country details",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Specific legal topic to newsjack (e.g. 'Insolvency')",
    )

    args = parser.parse_args()

    countries = args.countries
    if args.interactive:
        print("\n--- 🕵️ Marcus Vane Interactive Mode ---")
        user_input = input("Enter countries separated by space (default: Germany USA): ").strip()
        if user_input:
            countries = user_input.split()

    final_output = ""

    for country in countries:
        print(f"\n--- 🌍 Processing {country} ---")

        # 1. Search
        search_results = search_legal_news(country, max_results=args.max_results, topic=args.topic)
        if not search_results:
            print(f"  ⚠️ No results found for {country}.")
            continue

        print(f"  Found {len(search_results)} URLs initially.")

        # 2. Scrape & Filter
        aggregated_content = ""
        valid_count = 0

        for res in search_results:
            print(f"  🔍 Scraping: {res['href']}")
            text = scrape_content(res["href"])

            if text:
                # Relevance Check
                print("  ✅ Generating Strategy...")
                if is_relevant(text):
                    print("    Checking relevance...")
                    title = res.get("title") or "Legal News Article"
                    aggregated_content += f"\n\n--- Source: {title} ---\n{text[:3000]}"
                    valid_count += 1
                else:
                    print("    ❌ Not relevant (skipped)")
            else:
                print("    ⚠️ Failed to extract text.")

            if valid_count >= 3:
                break

        if not aggregated_content:
            print("  ⚠️ No relevant content could be scraped.")
            continue

        # 3. Generate
        posts = generate_linkedin_posts(aggregated_content, country)

        print("\n=== ✨ GENERATED POSTS ===")
        show_phone_preview(posts)

        final_output += f"# {country}\n\n{posts}\n\n"

    if final_output:
        # Save to file with timestamp in subfolder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = "LinkedIn_Posts"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"linkedin_posts_{timestamp}.md")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_output)
        print(f"\n✅ Saved all posts to '{filename}'.")
    else:
        print("\n⚠️ No content generated.")


if __name__ == "__main__":
    main()
