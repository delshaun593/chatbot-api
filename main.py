from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()  # <-- THIS MUST EXIST

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
    message: str
    client_id: str
    page_content: str = ""

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/chat")
def chat(req: ChatRequest):
    # 1️⃣ Get client-specific system prompt
    system_prompt = CLIENT_PROMPTS.get(req.client_id, "You are a helpful assistant.")

    # 2️⃣ Combine system prompt with page content
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Page content:\n{req.page_content}\nUser question:\n{req.message}"}
    ]

    try:
        # 3️⃣ Send request to OpenAI Chat API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        # 4️⃣ Return the AI's reply
        return {"reply": response.choices[0].message.content}

    except Exception as e:
        # 5️⃣ Catch errors (e.g., quota, network, API key)
        return {"error": str(e)}




