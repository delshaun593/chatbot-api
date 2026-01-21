from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

from clients import clients

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class ChatRequest(BaseModel):
    client_id: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    client = clients.get(req.client_id)

    if not client:
        raise HTTPException(status_code=404, detail="Invalid client ID")

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
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "reply": response.choices[0].message.content
    }


