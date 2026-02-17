"""
Agent G: The "Niche Authority" Amplifier
Purpose: Engage with potential clients on LinkedIn by drafting thoughtful comments.
"""

import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

# Mock CRM data - Top 50 Target CEOs (in production, this would be Salesforce)
TARGET_CEOS = [
    {"name": "Dr. Michael Schneider", "company": "TechMach GmbH", "industry": "Manufacturing", "linkedin_url": "linkedin.com/in/mschneider"},
    {"name": "Anna Hoffmann", "company": "GreenBau AG", "industry": "Construction", "linkedin_url": "linkedin.com/in/ahoffmann"},
    {"name": "Thomas Weber", "company": "FinServ Solutions", "industry": "FinTech", "linkedin_url": "linkedin.com/in/tweber"},
    # ... would be 50 in production
]

SYSTEM_PROMPT = """
You are a Community Manager for a Gunnercooke Partner. Your task is to draft LinkedIn comments on posts by target CEOs.

GOAL: Move the partner from 'Invisible' to 'Top Voice' in that comment section.

ANALYSIS STEPS:
1. Analyze the post's sentiment (positive/negative/neutral)
2. Identify the core business challenge or celebration mentioned
3. Draft a comment that adds SPECIFIC legal/strategic nuance

FORBIDDEN PHRASES (NEVER USE):
- "Great post!"
- "Agreed!"
- "Love this!"
- "Thanks for sharing!"
- Any direct selling of services
- Any self-promotion

COMMENT GUIDELINES:
- 2-3 sentences maximum
- Add genuine value or a specific insight
- Ask a thought-provoking question that positions you as an expert
- Reference a specific data point or trend if possible

OUTPUT FORMAT (JSON):
{
  "sentiment_analysis": "positive/negative/neutral",
  "key_theme": "What the post is really about",
  "comment_draft": "The actual comment to post",
  "strategic_intent": "Why this comment positions you as an authority"
}
"""

def analyze_and_comment(post_text: str, ceo_name: str, ceo_company: str, ceo_industry: str) -> dict:
    """
    Analyze a CEO's post and generate a strategic comment.
    
    Args:
        post_text: The content of the CEO's LinkedIn post
        ceo_name: Name of the CEO
        ceo_company: Their company
        ceo_industry: Their industry
    
    Returns:
        JSON with comment and analysis
    """
    
    prompt = f"""
    {SYSTEM_PROMPT}
    
    CEO CONTEXT:
    Name: {ceo_name}
    Company: {ceo_company}
    Industry: {ceo_industry}
    
    THEIR POST:
    {post_text}
    
    Generate a thoughtful comment as valid JSON. Remember: NO generic phrases, NO selling, ADD specific value.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3-pro',
            contents=prompt
        )
        
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        return json.loads(text.strip())
    except Exception as e:
        return {"error": str(e)}

def generate_engagement_plan(ceo_posts: list) -> list:
    """
    Generate an engagement plan for multiple CEO posts.
    
    Args:
        ceo_posts: List of dicts with ceo_name, company, industry, post_text
    
    Returns:
        List of analysis + comments
    """
    plan = []
    for post in ceo_posts:
        result = analyze_and_comment(
            post_text=post.get('post_text', ''),
            ceo_name=post.get('ceo_name', 'Unknown'),
            ceo_company=post.get('company', 'Unknown'),
            ceo_industry=post.get('industry', 'Unknown')
        )
        plan.append({
            "ceo": post.get('ceo_name'),
            "company": post.get('company'),
            "analysis": result
        })
    return plan

def format_engagement_card(ceo: str, company: str, analysis: dict) -> str:
    """Format a single engagement opportunity."""
    if "error" in analysis:
        return f"Error analyzing {ceo}'s post: {analysis['error']}"
    
    return f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🎯 ENGAGEMENT TARGET: {ceo} ({company})
├──────────────────────────────────────────────────────────────────────────────┤
│ 📊 Sentiment: {analysis.get('sentiment_analysis', 'Unknown')}
│ 🎯 Key Theme: {analysis.get('key_theme', 'Unknown')}
├──────────────────────────────────────────────────────────────────────────────┤
│ 💬 COMMENT TO POST:
│ 
│ "{analysis.get('comment_draft', 'No comment generated')}"
│
├──────────────────────────────────────────────────────────────────────────────┤
│ 🧠 Strategic Intent: {analysis.get('strategic_intent', 'N/A')}
└──────────────────────────────────────────────────────────────────────────────┘
"""


if __name__ == "__main__":
    print("=" * 80)
    print("AGENT G: NICHE AUTHORITY AMPLIFIER")
    print("=" * 80)
    
    # Example CEO posts (in production, these would be scraped from LinkedIn)
    sample_posts = [
        {
            "ceo_name": "Dr. Michael Schneider",
            "company": "TechMach GmbH",
            "industry": "Manufacturing",
            "post_text": """
            We just finished our first supply chain audit under the LkSG. 
            It took 4 months, cost us €200k, and I'm still not sure we're fully compliant.
            
            The regulation has good intentions but the implementation burden on mid-sized 
            companies is enormous. We had to hire 2 full-time compliance officers.
            
            Is anyone else struggling with this?
            """
        },
        {
            "ceo_name": "Anna Hoffmann",
            "company": "GreenBau AG",
            "industry": "Construction",
            "post_text": """
            Excited to announce we've secured our largest infrastructure project yet - 
            a €50m renewable energy hub in Bavaria! 🎉
            
            This wouldn't have been possible without our amazing team and 
            our commitment to sustainable building practices.
            
            #Construction #Sustainability #Growth
            """
        }
    ]
    
    print("\n📊 Generating Strategic Engagement Plan...\n")
    
    for post in sample_posts:
        analysis = analyze_and_comment(
            post_text=post['post_text'],
            ceo_name=post['ceo_name'],
            ceo_company=post['company'],
            ceo_industry=post['industry']
        )
        print(format_engagement_card(post['ceo_name'], post['company'], analysis))
