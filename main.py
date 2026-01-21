
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# ================================
# uvicorn main:app --reload
# 
# http://127.0.0.1:8000/docs
# ================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # <- allows requests from anywhere
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

client = OpenAI(
    api_key="OPENAI_API_KEY"
)
# ================================

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are a helpful business assistant."

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful website assistant."},
                {"role": "user", "content": req.message}
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        # Print the error in terminal and return it in response
        print("ERROR:", e)
        return {"error": str(e)}