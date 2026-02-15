import os
import sys
import time
from datetime import datetime

import google.generativeai as genai
import requests
import trafilatura
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

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
            timeout=10
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

def search_legal_news(country="USA", max_results=5):
    """
    Search for latest legal news using DuckDuckGo and Brave Search.
    """
    # Define queries
    if country.lower() in ["germany", "de"]:
        primary_query = "site:lto.de OR site:juve.de aktuelle jura nachrichten"
        secondary_query = "aktuelle jura nachrichten deutschland anwalt rechtsprechung"
        fallback_query = "aktuelle jura nachrichten deutschland anwalt"
        region = "de-de"
    else:
        primary_query = "site:abajournal.com OR site:law.com legal news United States"
        secondary_query = "legal news headlines United States"
        fallback_query = "legal news headlines United States"
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
                    results.append({"title": r.get("title"), "href": r.get("href"), "body": r.get("body")})
                print(f"  ✅ DDG Specific found {len(results)} results.")
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
                    results.append({"title": r.get("title"), "href": r.get("href"), "body": r.get("body")})
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
                results.append({
                    "title": item.get("title"),
                    "href": item.get("url"),
                    "body": item.get("description", "")
                })
            
            if results:
                print(f"  ✅ Brave Search found {len(results)} results.")
            else:
                 print("  ⚠️ Brave Search found no parseable results.")
        else:
             print(f"  ⚠️ Brave Search returned no valid data.")
             
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
    Check if the article is a significant legal development using a cheap model.
    """
    if not text or len(text) < 200:
        return False
        
    # Multi-model logic for relevance checking (candidate models not used in current implementation)
    prompt = (
        f"Is this text about a significant legal update or news (not ads/generic)? "
        f"Answer ONLY with YES or NO. TEXT: '{text[:300]}'"
    )
    try:
        # Use a cheaper/faster model for this check
        model = genai.GenerativeModel('models/gemini-flash-latest')
        response = model.generate_content(prompt)
        answer = response.text.strip().upper()
        return "YES" in answer
    except Exception:
        return True # Fallback to include if check fails

# --- 2026 MANIFESTO COMPLIANCE (INTEGRATED VIA intelligence_core.py) ---


def generate_linkedin_posts(articles_text, country):
    """
    Generate LinkedIn posts using Gemini with Manifesto Compliance.
    """
    print(f"Generating posts for {country}...")
    
    # Determine language based on country
    if country.lower() in ["germany", "de"]:
        lang_instr = "IMPORTANT: The output must be in **GERMAN**."
    else:
        lang_instr = "IMPORTANT: The output must be in **ENGLISH**."
    
    formatted_date = datetime.now().strftime("%Y-%m-%d")

    # High-status post generation
    # This prompt is for generating a single high-status post,
    # but the function is designed to generate three.
    # The original prompt structure is retained for multi-post generation.
    # prompt = f"Write a world-class high-status LinkedIn post about this: {articles_text[:6000]}"

    prompt = f"""
    You are Marcus Vane, an expert legal strategist known for being authoritative, cynical, and clarity-obsessed.
    Date: {formatted_date}
    
    Based on the following news relating to law in {country}, create THREE distinct, high-status LinkedIn posts.
    
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
    models = ['models/gemini-3-flash-preview', 'models/gemini-2.5-flash-lite']
    
    for model_name in models:
        try:
            print(f"  Attempting generation with {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            raw_text = response.text
            
            # Apply 2026 Compliance Layers
            final = apply_2026_standards(raw_text)
            return final
        except Exception as e:
            print(f"  ⚠️ {model_name} failed: {e}")
            continue
            
    return "Error: All models in fallback chain failed."

def main():
    countries = ["Germany", "USA"]
    
    final_output = ""
    
    for country in countries:
        print(f"\n--- Processing {country} ---")
        
        # 1. Search
        search_results = search_legal_news(country, max_results=5) # Increased to 5 to allow filtering
        if not search_results:
            print(f"No results found for {country}.")
            continue
            
        print(f"Found {len(search_results)} URLs initially.")
        
        # 2. Scrape & Filter
        aggregated_content = ""
        valid_count = 0
        
        for res in search_results:
            print(f"Scraping: {res['href']}")
            text = scrape_content(res['href'])
            
            if text:
                # Relevance Check
                print("  Checking relevance...")
                if is_relevant(text):
                    print("  ✅ Relevant")
                    # Use title placeholder if real title extraction failed
                    title = res.get('title') or "Legal News Article"
                    aggregated_content += f"\n\n--- Source: {title} ---\n{text[:3000]}" # Limit text per article
                    valid_count += 1
                else:
                    print("  ❌ Not relevant (skipped)")
            else:
                print("  Failed to extract text.")
                
            # Stop if we have enough good content (e.g., 3 good articles)
            if valid_count >= 3:
                break
        
        if not aggregated_content:
            print("No relevant content could be scraped.")
            continue
            
        # 3. Generate
        posts = generate_linkedin_posts(aggregated_content, country)
        
        print("\n=== GENERATED POSTS ===")
        print(posts)
        
        final_output += f"# {country}\n\n{posts}\n\n"
        
    # Save to file with timestamp in subfolder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = "LinkedIn_Posts"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"linkedin_posts_{timestamp}.md")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"\nSaved all posts to '{filename}'.")

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
