
import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_gemini_client():

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found.")

    return genai.Client(api_key=api_key.strip())



def ask_gemini(prompt):

    try:
        client = get_gemini_client()

        models = [
            "gemini-3.8-flash",
            "gemini-3.5-flash-lite"
        ]

        errors = []

        for model in models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                return response.text

            except Exception as e:
                errors.append(
                    f"{model}: {str(e)}"
                )

                time.sleep(2)

        return (
            "Gemini models could not generate a response.\n\n"
            + "\n\n".join(errors)
        )

    except Exception as e:
        return f"Gemini API Error: {str(e)}"
