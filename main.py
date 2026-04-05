from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import httpx
import uuid
from datetime import datetime

from config import CLIENT_PROMPTS
from dependencies import openai_client
from widget import router as widget_router
from onboarding import router as onboarding_router
from admin import router as admin_router
from banner import router as banner_router
from reviews import router as reviews_router
from toolkit import router as toolkit_router
from database import supabase

load_dotenv()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(widget_router)
app.include_router(onboarding_router)
app.include_router(admin_router)
app.include_router(banner_router)
app.include_router(reviews_router)
app.include_router(toolkit_router)

# ── Startup: load all clients from Supabase ────────────────────────────────────
@app.on_event("startup")
async def load_clients_from_supabase():
    try:
        res = supabase.table("clients").select("id, system_prompt").execute()
        rows = res.data or []
        for row in rows:
            CLIENT_PROMPTS[row["id"]] = row["system_prompt"]
        print(f"✅ Loaded {len(rows)} clients from Supabase")
    except Exception as e:
        print(f"⚠️  Failed to load clients from Supabase: {e}")

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
    page_url: str = ""
    history: list = []
    session_id: str = ""

class Lead(BaseModel):
    client_id: str
    name: str
    email: str

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "API running"}


@app.post("/session")
async def create_session(req: dict):
    try:
        session_id = str(uuid.uuid4())
        supabase.table("sessions").insert({
            "id": session_id,
            "client_id": req.get("client_id"),
            "page_url": req.get("page_url", "")
        }).execute()
        return {"session_id": session_id}
    except Exception as e:
        print(f"⚠️ Session creation failed: {e}")
        return {"session_id": str(uuid.uuid4())}


@app.post("/lead")
@limiter.limit("10/minute")
async def capture_lead(lead: Lead, request: Request):
    # 1. Save lead to Supabase
    try:
        supabase.table("leads").insert({
            "client_id": lead.client_id,
            "name": lead.name,
            "email": lead.email,
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save lead: {str(e)}")

    # 2. Fire-and-forget: email the business owner
    try:
        from email_service import send_lead_notification

        # Fetch owner email from Supabase (fast — usually cached by Supabase client)
        client_res = supabase.table("clients").select("email, business_name").eq("id", lead.client_id).single().execute()
        if client_res.data:
            asyncio.create_task(send_lead_notification(
                owner_email=client_res.data["email"],
                business_name=client_res.data["business_name"],
                lead_name=lead.name,
                lead_email=lead.email,
                page_url=request.headers.get("Referer", ""),
            ))
    except Exception as e:
        print(f"⚠️ Lead email trigger failed: {e}")

    return {"status": "success", "message": "Lead saved"}


@app.post("/chat")
@limiter.limit("20/minute")
def chat(req: ChatRequest, request: Request):
    system_prompt = CLIENT_PROMPTS.get(req.client_id)
    if not system_prompt:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(req.history)
    messages.append({
        "role": "user",
        "content": f"Page content:\n{req.page_content}\n\nUser question:\n{req.message}"
    })

    # Log user message
    try:
        if req.session_id:
            supabase.table("messages").insert({
                "session_id": req.session_id,
                "client_id": req.client_id,
                "role": "user",
                "content": req.message
            }).execute()
    except Exception as e:
        print(f"⚠️ Message logging failed: {e}")
        pass

    full_reply = []

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
                    full_reply.append(delta)
                    yield delta

        # Log assistant reply after streaming completes
        try:
            if req.session_id:
                supabase.table("messages").insert({
                    "session_id": req.session_id,
                    "client_id": req.client_id,
                    "role": "assistant",
                    "content": "".join(full_reply)
                }).execute()
        except Exception:
            pass

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
        }
    )
