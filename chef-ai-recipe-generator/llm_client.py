import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
from pydantic import BaseModel
from typing import TypeVar, Type
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            # Try to get from Streamlit secrets if not in environment
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
            
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable or Streamlit secret is not set.")
        
    return genai.Client(api_key=api_key)

def generate_structured(prompt: str, response_schema: Type[T]) -> T:
    """
    Calls the Gemini model and returns a structured response matching the given Pydantic schema.
    """
    logger.info(f"Generating structured response for schema {response_schema.__name__}")
    client = get_client()
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Switching to Flash to avoid free-tier rate limits
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': response_schema,
            'temperature': 0.7
        },
    )
    
    return response_schema.model_validate_json(response.text)
