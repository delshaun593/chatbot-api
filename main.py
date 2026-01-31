from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

Load environment variables from .env
load_dotenv()

Create FastAPI app
app = FastAPI()

Enable CORS for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],          # allow all domains
    allow_credentials=True,
    allow_methods=[""],          # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

Request schema (matches frontend)
class ChatRequest(BaseModel):
    message: str
    client_id: str | None = None
    page_content: str | None = None

Health check
@app.get("/")
def root():
    return {"status": "API running"}

Chat endpoint
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful business assistant."
                },
                {
                    "role": "user",
                    "content": req.message
                }
            ]
        )

        return {
            "reply": response.choices[0].message.content
        }

    except Exception as e:
        print("ERROR:", e)
        return {
            "error": "Internal server error"




