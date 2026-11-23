
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load local environment variables
load_dotenv()


def get_gemini_client():

    # First check Streamlit Cloud Secrets
    api_key = st.secrets.get("GEMINI_API_KEY", None)

    # If unavailable, use the local .env file
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Check Streamlit Secrets or your .env file."
        )

    api_key = api_key.strip()

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
