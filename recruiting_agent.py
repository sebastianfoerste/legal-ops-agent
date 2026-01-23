import os
import requests
import json
import time
import random
from datetime import datetime
from dotenv import load_dotenv

# Third-party libraries
import trafilatura
from bs4 import BeautifulSoup
from ddgs import DDGS
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)

def search_legal_news(country="USA", max_results=5):
    """
    Search for latest legal news using DuckDuckGo (Steps 1 & 2) and Brave Search (Fallback).
    """
    # Define queries
    if country.lower() in ["germany", "de"]:
        # 1. DuckDuckGo Specific
        primary_query = "site:lto.de OR site:juve.de aktuelle jura nachrichten"
        # 2. DuckDuckGo Broad
        secondary_query = "aktuelle jura nachrichten deutschland anwalt rechtsprechung"
        # 3. Brave Fallback
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
    print(f"Attempting Primary Search (DDG Specific): {primary_query}")
    try:
        with DDGS() as ddgs:
            ddg_results = ddgs.text(primary_query, region=region, max_results=max_results)
            if ddg_results:
                for r in ddg_results:
                    results.append({
                        "title": r.get("title"),
                        "href": r.get("href"),
                        "body": r.get("body")
                    })
                print(f"  ✅ DDG Specific found {len(results)} results.")
                return results
            else:
                print("  ⚠️ DDG Specific returned no results.")
    except Exception as e:
        print(f"  ❌ DDG Specific failed: {e}")

    # --- 2. Secondary: DuckDuckGo Broad ---
    print(f"Attempting Secondary Search (DDG Broad): {secondary_query}")
    try:
        # Short sleep to be nice
        time.sleep(2)
        with DDGS() as ddgs:
            ddg_results = ddgs.text(secondary_query, region=region, max_results=max_results)
            if ddg_results:
                for r in ddg_results:
                     results.append({
                        "title": r.get("title"),
                        "href": r.get("href"),
                        "body": r.get("body")
                    })
                print(f"  ✅ DDG Broad found {len(results)} results.")
                return results
            else:
                print("  ⚠️ DDG Broad returned no results.")
    except Exception as e:
        print(f"  ❌ DDG Broad failed: {e}")
    
    # Removed brittle Brave fallback to prevent hanging
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
        
    prompt = f"""
    Is this article about a significant legal development? 
    Answer ONLY with YES or NO.
    
    TEXT:
    {text[:500]}
    """
    try:
        # Use a cheaper/faster model for this check
        model = genai.GenerativeModel('models/gemini-flash-latest')
        response = model.generate_content(prompt)
        answer = response.text.strip().upper()
        return "YES" in answer
    except Exception:
        return True # Fallback to include if check fails

def generate_linkedin_posts(articles_text, country):
    """
    Generate LinkedIn posts using Gemini.
    """
    print(f"Generating posts for {country}...")
    
    # Determine language based on country
    if country.lower() in ["germany", "de"]:
        lang_instr = "IMPORTANT: The output must be in **GERMAN**."
        placeholder = "[Content in German]"
    else:
        lang_instr = "IMPORTANT: The output must be in **ENGLISH**."
        placeholder = "[Content in English]"
    
    formatted_date = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
    You are a Senior Partner at a prestigious, forward-thinking law firm. Your goal is to position the firm as a thought leader and the **best place for top legal talent to work**.
    Date: {formatted_date}
    
    Based on the following news summaries relating to law in {country}, create THREE distinct, engaging LinkedIn posts.
    
    {lang_instr}
    
    IMPORTANT FORMATTING RULES:
    - Do NOT use Markdown (no **, no ##, no __).
    - Use UNICODE text for bolding (e.g., 𝗕𝗼𝗹𝗱) and italics (e.g., 𝘐𝘵𝘢𝘭𝘪𝘤𝘴) where emphasis is needed.
    - Use plenty of whitespace (line breaks).
    
    STRUCTURE EACH POST FOR VIRALITY & RECRUITING:
    1.  **The Hook (Lines 1-2)**: A controversial statement, a question, or a "surprising fact" that forces the user to click "See more".
    2.  **The Insight (Body)**: Don't just report the news. Analyze it. Ask: "What does this mean for our clients?" or "This is the kind of complex puzzle we love solving."
    3.  **The Recruiting Pitch (Subtle)**: Weave in that your firm effectively handles these high-stakes matters. 
    4.  **The Call to Action (CTA)**: Explicitly invite candidates. 
        - *Example:* "Does this kind of complex litigation excite you? We are expanding our team. DM me or check the link in bio."
    5.  **The Engagement Bait**: End with a question to drive comments.
    
    SOURCE TEXT:
    {articles_text[:30000]}
    
    OUTPUT FORMAT:
    Post 1:
    {placeholder}
    POLL:
    Question: [Poll Question?]
    Option A: [Option 1]
    Option B: [Option 2]
    Option C: [Option 3]
    IMAGE PROMPT: [Detailed description for a high-converting visual (e.g., minimalist chart, metaphorical photo)]
    
    Post 2:
    {placeholder}
    POLL:
    Question: [Poll Question?]
    Option A: [Option 1]
    Option B: [Option 2]
    Option C: [Option 3]
    IMAGE PROMPT: [Detailed description]
    
    Post 3:
    {placeholder}
    POLL:
    Question: [Poll Question?]
    Option A: [Option 1]
    Option B: [Option 2]
    Option C: [Option 3]
    IMAGE PROMPT: [Detailed description]
    """

    try:
        # Switching to Gemini 3 Flash Preview as currently active/working
        model = genai.GenerativeModel('models/gemini-3-flash-preview')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error gathering generation: {e}"

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
        final_output_utf8 = final_output # This line was in the instruction, though it's redundant
        f.write(final_output)
    print(f"\nSaved all posts to '{filename}'.")

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
