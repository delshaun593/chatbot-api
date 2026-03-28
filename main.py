from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import httpx
from datetime import datetime

from config import CLIENT_PROMPTS, CLIENT_SHEETS, MASTER_SHEET_ID
from dependencies import openai_client, sheets_service
from widget import router as widget_router
from onboarding import router as onboarding_router

load_dotenv()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(widget_router)
app.include_router(onboarding_router)

# ── Startup: load all clients from master sheet ────────────────────────────────
@app.on_event("startup")
async def load_clients_from_sheet():
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=MASTER_SHEET_ID,
            range="A:E"
        ).execute()
        rows = result.get("values", [])
        loaded = 0
        for row in rows[1:]:  # skip header row
            if len(row) >= 4:
                client_id, _, _, system_prompt = row[0], row[1], row[2], row[3]
                CLIENT_PROMPTS[client_id] = system_prompt
                loaded += 1
        print(f"✅ Loaded {loaded} clients from Google Sheets")
    except Exception as e:
        print(f"⚠️  Failed to load clients from sheet: {e}")

# ── Keep-alive ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def keep_alive():
    async def ping():
        while True:
            await asyncio.sleep(14 * 60)
            try:
                async with httpx.AsyncClient() as client:
                    await client.get("https://chatbot-api-4ssr.onrender.com/")
            except Exception:
                pass
    asyncio.create_task(ping())

# ── Models ─────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    client_id: str
    message: str
    page_content: str = ""
    history: list = []

class Lead(BaseModel):
    client_id: str
    name: str
    email: str

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "API running"}


@app.post("/lead")
async def capture_lead(lead: Lead):
    sheet_id = CLIENT_SHEETS.get(lead.client_id)
    if not sheet_id:
        raise HTTPException(status_code=404, detail="Client spreadsheet not found")

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="A:C",
            valueInputOption="USER_ENTERED",
            body={"values": [[lead.name, lead.email, str(datetime.now())]]}
        ).execute()
        return {"status": "success", "message": "Lead saved to Google Sheets"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save lead: {str(e)}")


@app.post("/chat")
def chat(req: ChatRequest):
    system_prompt = CLIENT_PROMPTS.get(req.client_id)
    if not system_prompt:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(req.history)
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















