import re
import random
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

API_KEY = "blahblahblah"  # change if you want

app = FastAPI(title="Agentic Honey-Pot API")

memory = {}

class Message(BaseModel):
    sender_id: str
    message: str

scam_keywords = [
    "prize", "won", "urgent", "click", "upi",
    "bank", "reward", "offer", "limited"
]

persona_replies = [
    "I am interested. Please share UPI details.",
    "Okay sir, should I send via bank or UPI?",
    "I want to proceed. Please guide me.",
    "Is there any processing fee? Share payment details.",
    "I am ready to pay. Please send account or UPI ID."
]

def authenticate(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/chat")
def chat(data: Message, x_api_key: str = Header(...)):
    authenticate(x_api_key)

    sid = data.sender_id
    msg = data.message

    if sid not in memory:
        memory[sid] = []

    memory[sid].append({
        "from": "scammer",
        "message": msg,
        "timestamp": str(datetime.now())
    })

    scam = any(word in msg.lower() for word in scam_keywords)
    reply = random.choice(persona_replies) if scam else "Please explain more."

    memory[sid].append({
        "from": "agent",
        "message": reply,
        "timestamp": str(datetime.now())
    })

    upi = re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", msg)
    links = re.findall(r"https?://\S+", msg)
    banks = re.findall(r"\b\d{9,18}\b", msg)

    return {
        "sender_id": sid,
        "scam_detected": scam,
        "scam_confidence": min(1.0, 0.3 + 0.1 * len(memory[sid])),
        "agent_reply": reply,
        "extracted_intelligence": {
            "upi_ids": upi,
            "phishing_links": links,
            "bank_account_numbers": banks
        },
        "conversation_history": memory[sid]
    }
