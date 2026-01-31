@@ -1,51 +1,69 @@
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

from clients import clients
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()  # <-- THIS MUST EXIST

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_methods=[""],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CLIENT_PROMPTS = {
    "client_a": """You are a helpful assistant for Client A.
Their website is https://clienta.com
They sell gym equipment and fitness services.
Answer user questions based on this information.""",

    "client_b": """You are a helpful assistant for Client B.
Their website is https://clientb.com
They run a boutique interior design studio.
Answer user questions about their services and contact info."""
}

class ChatRequest(BaseModel):
    client_id: str
    message: str
    client_id: str
    page_content: str = ""

@app.post("/chat")
async def chat(req: ChatRequest):
    client = clients.get(req.client_id)
@app.get("/")
def root():
    return {"status": "API running"}

    if not client:
        raise HTTPException(status_code=404, detail="Invalid client ID")
@app.post("/chat")
def chat(req: ChatRequest):
    # 1️⃣ Get client-specific system prompt
    system_prompt = CLIENT_PROMPTS.get(req.client_id, "You are a helpful assistant.")

    # 2️⃣ Combine system prompt with page content
    messages = [
        {
            "role": "system",
            "content": client["system_prompt"]
        },
        {
            "role": "system",
            "content": f"BUSINESS CONTEXT:\n{client['context']}"
        },
        {
            "role": "user",
            "content": req.message
        }
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Page content:\n{req.page_content}\nUser question:\n{req.message}"}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.3
        # 3️⃣ Send request to OpenAI Chat API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        # 4️⃣ Return the AI's reply
        return {"reply": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        # 5️⃣ Catch errors (e.g., quota, network, API key)
        return {"error": str(e)}


    return {
        "reply": response.choices[0].message.content
    }







