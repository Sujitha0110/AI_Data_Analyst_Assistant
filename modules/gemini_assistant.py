
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Check your .env file."
        )

    return genai.Client(api_key=api_key)


def ask_gemini(prompt):
    try:
        client = get_gemini_client()

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Gemini API Error: {str(e)}"
