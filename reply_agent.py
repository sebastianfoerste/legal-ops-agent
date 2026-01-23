import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing")

genai.configure(api_key=GOOGLE_API_KEY)

def generate_replies(input_text):
    prompt = f"""
    You are a witty, professional legal influencer on LinkedIn.
    You need to comment on the following post/article summary.
    
    The goal is to drive engagement to your profile.
    
    Generate 3 distinct comment options:
    1.  **The Supporter**: Validating the author's point but adding a specific nuance.
    2.  **The Challenger**: Respectfully disagreeing or playing devil's advocate.
    3.  **The Questioner**: Asking a deep, open-ended question that forces a reply.
    
    INPUT TEXT:
    {input_text[:2000]}
    
    OUTPUT FORMAT:
    Option 1 (Support): [Comment]
    Option 2 (Challenge): [Comment]
    Option 3 (Question): [Comment]
    """
    
    try:
        model = genai.GenerativeModel('models/gemini-3-flash-preview')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("--- LinkedIn Reply Generator ---")
    if len(sys.argv) > 1:
        # Accepting text file path usually, but for simplicity let's assume CLI arg is the text or we prompt
        input_data = sys.argv[1]
        if os.path.isfile(input_data):
            with open(input_data, "r") as f:
                text = f.read()
        else:
            text = input_data
    else:
        print("Please paste the text of the post you want to comment on (Ctrl+D to finish):")
        text = sys.stdin.read()
        
    replies = generate_replies(text)
    print("\n=== GENERATED REPLIES ===\n")
    print(replies)
