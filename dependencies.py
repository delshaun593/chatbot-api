"""
Shared dependency instances used across routers.
Populated at startup in main.py.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"))
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
sheets_service = build("sheets", "v4", credentials=credentials)
