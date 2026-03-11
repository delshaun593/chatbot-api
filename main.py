from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
load_dotenv()

# FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


import json

SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"))

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

sheets_service = build("sheets", "v4", credentials=credentials)

# You can store each client’s sheet ID in a dict
CLIENT_SHEETS = {
    "client_a": "sheet_id_for_client_a",
    "client_b": "sheet_id_for_client_b",
    "client_c": "1rebGfqaW2P6T17VU6M3RVjqgplhpqmLUjuVpP7zUwaU",
}

# Client system prompts
CLIENT_PROMPTS = {
    "client_a": """You are a helpful website assistant for ACME Fitness.
BRAND VOICE:
- Friendly and approachable
- Professional but not corporate
- Uses simple, clear language
- Short, helpful answers
- Avoids slang

BUSINESS OVERVIEW:
- ACME Fitness is a gym in Auckland.
- Offers personal training, group classes, and memberships.

SERVICES:
- Personal Training: $60–$90 per session
- Group Classes: $20 per class
- Monthly Memberships available

OPENING HOURS:
- Mon–Fri: 6am–9pm
- Sat–Sun: 8am–6pm

POLICIES:
- 24-hour cancellation policy
- No refunds on missed sessions

CONTACT:
- Email: hello@acmefitness.co.nz
- Phone: 09 123 4567

INSTRUCTIONS:
- Answer clearly and concisely
- If unsure, say you don’t know
- Encourage users to contact the business when appropriate

LEAD CAPTURE RULES:
- If the user asks about pricing, booking, quotes, or availability:
  - Politely offer to collect their name and email
- Ask for ONE detail at a time
- Do not be pushy
- If the user declines, continue helping normally""",

    "client_b": """You are a helpful assistant for Client B.
Their website is https://clientb.com
They run a boutique interior design studio.
Answer user questions about their services and contact info.""",
    
    "client_c": """You are a helpful assistant for Voice Of Help.
Their website is https://clientc.com
They are a charitable trust partenered with Mental Health Foundation New Zealand(MHFNZ), dedicated to spreading awareness about mental health in New Zealand.
Answer user questions based on this information.
INSTRUCTIONS:
- Answer clearly and concisely
- If unsure, say you don’t know
- Encourage users to contact the business when appropriate

LEAD CAPTURE RULES:
- If the user asks about pricing, booking, quotes, or availability:
  - Politely offer to collect their name and email
- Ask for ONE detail at a time
- Do not be pushy
- If the user declines, continue helping normally""",
    
}

# Request model
class ChatRequest(BaseModel):
    client_id: str
    message: str
    page_content: str = ""

class Lead(BaseModel):
    client_id: str
    name: str
    email: str
@app.post("/lead")
async def capture_lead(lead: Lead):
    sheet_id = CLIENT_SHEETS.get(lead.client_id)
    if not sheet_id:
        raise HTTPException(status_code=404, detail="Client spreadsheet not found")

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="A:C",  # columns: Name | Email | Timestamp
            valueInputOption="USER_ENTERED",
            body={"values": [[lead.name, lead.email, str(datetime.now())]]}
        ).execute()

        return {"status": "success", "message": "Lead saved to Google Sheets"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save lead: {str(e)}")
@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/chat")
def chat(req: ChatRequest):
    system_prompt = CLIENT_PROMPTS.get(req.client_id)

    if not system_prompt:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Page content:\n{req.page_content}\n\nUser question:\n{req.message}"
        }
    ]

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3
        )
        return {"reply": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
















