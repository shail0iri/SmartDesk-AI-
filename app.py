from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os

# Load trained models
sentiment_model = joblib.load("models/sentiment_best.joblib")
urgency_model = joblib.load("models/urgency_best.joblib")
category_model = joblib.load("models/category_best.joblib")

# FastAPI app
app = FastAPI(title="SmartDesk AI", version="1.0")

class Ticket(BaseModel):
    ticket_text: str

@app.post("/predict/")
def predict(ticket: Ticket):
    text = [ticket.ticket_text]
    return {
        "ticket_text": ticket.ticket_text,
        "sentiment": sentiment_model.predict(text)[0],
        "urgency": urgency_model.predict(text)[0],
        "category": category_model.predict(text)[0]
    }
