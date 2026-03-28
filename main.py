from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from fastapi.responses import StreamingResponse
import httpx
import asyncio
import uuid
from fastapi.responses import HTMLResponse
load_dotenv()
MASTER_SHEET_ID = "17JupQpl8M5e_vluuV6lQlhesW7WzGu-iL4BHYDv129E"
# FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later

    allow_methods=["*"],
    allow_headers=["*"],
)
# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_client_id():
    return "client_" + str(uuid.uuid4())[:8]


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
    history: list = [] 

class Lead(BaseModel):
    client_id: str
    name: str
    email: str

class OnboardingRequest(BaseModel):
    business_name: str
    industry: str
    services: str
    hours: str
    contact: str
    email: str
    extra_info: str = ""


    
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

@app.post("/register")
async def register_client(req: OnboardingRequest):
    # Generate system prompt using GPT
    prompt_instructions = f"""
    Create a helpful chatbot system prompt for the following business:
    
    Business Name: {req.business_name}
    Industry: {req.industry}
    Services: {req.services}
    Opening Hours: {req.hours}
    Contact Info: {req.contact}
    Extra Info: {req.extra_info}
    
    The system prompt should:
    - Give the bot a friendly, professional personality
    - Include all the business details above
    - Instruct the bot to answer clearly and concisely
    - Instruct the bot to encourage users to get in touch when appropriate
    - Include lead capture rules: collect name and email when users ask about pricing, booking, or availability
    - Ask for one detail at a time and not be pushy
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_instructions}],
        temperature=0.4
    )

    system_prompt = response.choices[0].message.content
    client_id = generate_client_id()

    # Save to master Google Sheet
    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=MASTER_SHEET_ID,
            range="A:E",
            valueInputOption="USER_ENTERED",
            body={"values": [[
                client_id,
                req.business_name,
                req.email,
                system_prompt,
                str(datetime.now())
            ]]}
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save client: {str(e)}")

    # Dynamically add to CLIENT_PROMPTS so it works immediately
    CLIENT_PROMPTS[client_id] = system_prompt

    # Generate embed code
    embed_code = f"""<div id="wix-chat-widget"></div>
<script src="https://chatbot-api-4ssr.onrender.com/widget.js?client_id={client_id}"></script>"""

    return {
        "client_id": client_id,
        "system_prompt": system_prompt,
        "embed_code": embed_code
    }

@app.on_event("startup")
async def load_clients_from_sheet():
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=MASTER_SHEET_ID,
            range="A:E"
        ).execute()
        rows = result.get("values", [])
        for row in rows[1:]:  # skip header row
            if len(row) >= 4:
                client_id, business_name, email, system_prompt = row[0], row[1], row[2], row[3]
                CLIENT_PROMPTS[client_id] = system_prompt
        print(f"Loaded {len(rows) - 1} clients from Google Sheets")
    except Exception as e:
        print(f"Failed to load clients: {e}")
async def keep_alive():
    async def ping():
        while True:
            await asyncio.sleep(14 * 60)  # every 14 minutes
            try:
                async with httpx.AsyncClient() as client:
                    await client.get("https://chatbot-api-4ssr.onrender.com/")
            except:
                pass
    asyncio.create_task(ping())


@app.get("/onboarding", response_class=HTMLResponse)
def onboarding_form():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Onboarding</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: sans-serif; background: #f5f5f5; display: flex; justify-content: center; padding: 40px 20px; }
        .form-container { background: white; padding: 40px; border-radius: 12px; width: 100%; max-width: 600px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
        h1 { margin-bottom: 8px; font-size: 24px; }
        p.subtitle { color: #666; margin-bottom: 32px; }
        .field { margin-bottom: 20px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 14px; }
        input, textarea { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        input:focus, textarea:focus { border-color: #007bff; }
        textarea { resize: vertical; min-height: 80px; }
        button { width: 100%; padding: 14px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 8px; }
        button:hover { background: #0056b3; }
        button:disabled { background: #aaa; cursor: not-allowed; }
        .result { margin-top: 32px; padding: 20px; background: #f0f9f0; border-radius: 8px; border: 1px solid #b2dfb2; display: none; }
        .result h2 { color: #2e7d32; margin-bottom: 12px; }
        .code-box { background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 13px; white-space: pre-wrap; word-break: break-all; margin: 12px 0; }
        .copy-btn { width: auto; padding: 8px 16px; font-size: 14px; margin-top: 0; }
        .error { margin-top: 16px; padding: 12px; background: #fff0f0; border-radius: 8px; border: 1px solid #ffcccc; color: #c00; display: none; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>Set Up Your Chatbot</h1>
        <p class="subtitle">Fill in your business details and we'll generate a custom chatbot for your website.</p>

        <div class="field">
            <label>Business Name *</label>
            <input type="text" id="business_name" placeholder="e.g. Auckland Plumbing Co." />
        </div>
        <div class="field">
            <label>Industry *</label>
            <input type="text" id="industry" placeholder="e.g. Plumbing, Fitness, Legal" />
        </div>
        <div class="field">
            <label>Services Offered *</label>
            <textarea id="services" placeholder="e.g. Emergency plumbing, pipe repairs, bathroom installations..."></textarea>
        </div>
        <div class="field">
            <label>Opening Hours *</label>
            <input type="text" id="hours" placeholder="e.g. Mon-Fri 8am-6pm, Sat 9am-2pm" />
        </div>
        <div class="field">
            <label>Contact Information *</label>
            <input type="text" id="contact" placeholder="e.g. Phone: 09 123 4567, Email: hello@business.co.nz" />
        </div>
        <div class="field">
            <label>Your Email Address * (for receiving leads)</label>
            <input type="email" id="email" placeholder="you@yourbusiness.com" />
        </div>
        <div class="field">
            <label>Anything else the chatbot should know? (optional)</label>
            <textarea id="extra_info" placeholder="e.g. We offer a free first consultation. We service the Auckland region only."></textarea>
        </div>

        <button id="submit-btn" onclick="submitForm()">Generate My Chatbot →</button>
        <div class="error" id="error-box"></div>

        <div class="result" id="result-box">
            <h2>✅ Your chatbot is ready!</h2>
            <p>Copy and paste this code into your Wix HTML Embed:</p>
            <div class="code-box" id="embed-code"></div>
            <button class="copy-btn" onclick="copyCode()">Copy Code</button>
            <p style="margin-top:16px; color:#555; font-size:13px;">Your Client ID: <strong id="client-id-display"></strong></p>
        </div>
    </div>

    <script>
        async function submitForm() {
            const btn = document.getElementById("submit-btn");
            const errorBox = document.getElementById("error-box");
            errorBox.style.display = "none";

            const fields = {
                business_name: document.getElementById("business_name").value.trim(),
                industry: document.getElementById("industry").value.trim(),
                services: document.getElementById("services").value.trim(),
                hours: document.getElementById("hours").value.trim(),
                contact: document.getElementById("contact").value.trim(),
                email: document.getElementById("email").value.trim(),
                extra_info: document.getElementById("extra_info").value.trim()
            };

            // Basic validation
            for (const [key, value] of Object.entries(fields)) {
                if (!value && key !== "extra_info") {
                    errorBox.textContent = "Please fill in all required fields.";
                    errorBox.style.display = "block";
                    return;
                }
            }

            btn.disabled = true;
            btn.textContent = "Generating your chatbot...";

            try {
                const res = await fetch("/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(fields)
                });

                if (!res.ok) throw new Error("Server error");

                const data = await res.json();

                document.getElementById("embed-code").textContent = data.embed_code;
                document.getElementById("client-id-display").textContent = data.client_id;
                document.getElementById("result-box").style.display = "block";
                btn.textContent = "Generate My Chatbot →";
                btn.disabled = false;

            } catch {
                errorBox.textContent = "Something went wrong. Please try again.";
                errorBox.style.display = "block";
                btn.textContent = "Generate My Chatbot →";
                btn.disabled = false;
            }
        }

        function copyCode() {
            const code = document.getElementById("embed-code").textContent;
            navigator.clipboard.writeText(code).then(() => {
                const btn = document.querySelector(".copy-btn");
                btn.textContent = "Copied!";
                setTimeout(() => btn.textContent = "Copy Code", 2000);
            });
        }
    </script>
</body>
</html>
"""
    


@app.post("/chat")
def chat(req: ChatRequest):
    system_prompt = CLIENT_PROMPTS.get(req.client_id)

    if not system_prompt:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    # Start with system prompt
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    messages.extend(req.history)
    
    # Add current message
    messages.append({
        "role": "user",
        "content": f"Page content:\n{req.page_content}\n\nUser question:\n{req.message}"
    })

    def generate():
        with openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            stream=True
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

    return StreamingResponse(
    generate(),
    media_type="text/plain",
    headers={
        "X-Accel-Buffering": "no",
        "Cache-Control": "no-cache",
    }
)
















