
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found in .env")
else:
    client = genai.Client(api_key=api_key.strip())

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Say hello in one sentence."
        )

        print("SUCCESS!")
        print(response.text)

    except Exception as e:
        print("API TEST FAILED:")
        print(str(e))
