"""
Shared dependency instances used across routers.
Google Sheets / service account removed — all storage now in Supabase.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
