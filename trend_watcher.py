import time
from ddgs import DDGS

def check_trends():
    """
    Checks for breaking legal news in Germany and USA using 'breaking' keywords via DuckDuckGo.
    """
    print("--- 🔍 Scanning for Legal Trends (Trendjack) ---")
    
    keywords = [
        ("Germany", "eilmeldung jura urteil verfassungsgericht"),
        ("Germany", "breaking legal news germany"),
        ("USA", "breaking legal news supreme court ruling"),
        ("USA", "major lawsuit filed today")
    ]
    
    found_trends = False
    
    with DDGS() as ddgs:
        for country, query in keywords:
            print(f"Scanning {country}: '{query}'...")
            try:
                # Use 'news' search specifically if available, else 'text' with time filter 'd' (day)
                # ddgs.news() is often better for trending
                results = ddgs.news(query, region="de-de" if country == "Germany" else "us-en", safesearch="off", max_results=3)
                
                if results:
                    found_trends = True
                    print(f"\n🚨 TREND ALERT ({country}):")
                    for r in results:
                        # Depending on version r is dict or object. Usually dict.
                        title = r.get('title')
                        date = r.get('date') # Might be relative like "2 hours ago"
                        url = r.get('url')
                        print(f"  - [{date}] {title}")
                        print(f"    Link: {url}")
            except Exception as e:
                print(f"  Error scanning {country}: {e}")
            
            time.sleep(2) # be nice
            
    if not found_trends:
        print("\nNo major breaking trends found right now.")

if __name__ == "__main__":
    check_trends()
