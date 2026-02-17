import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print("Available Models:")
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
