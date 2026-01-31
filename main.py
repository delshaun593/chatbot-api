from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

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

# Client system prompts
CLIENT_PROMPTS = {
    "client_a": """You are a helpful assistant for Client A.
Their website is https://clienta.com
They sell gym equipment and fitness services.
Answer user questions based on this information.""",

    "client_b": """You are a helpful assistant for Client B.
Their website is https://clientb.com
They run a boutique interior design studio.
Answer user questions about their services and contact info.""",
    
    "client_c": """You are a helpful assistant for Voice Of Help.
Their website is https://clientc.com
They are a charitable trust partenered with Mental Health Foundation New Zealand(MHFNZ), dedicated to spreading awareness about mental health in New Zealand.
Answer user questions based on this information.""",
    
}

# Request model
class ChatRequest(BaseModel):
    client_id: str
    message: str
    page_content: str = ""

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











