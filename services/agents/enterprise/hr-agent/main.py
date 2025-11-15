from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import datetime

app = FastAPI()

MODEL_URL = "http://localhost:8050/predict"  # sentiment model server

# ----------------------------------------------------
# REQUEST BODY
# ----------------------------------------------------
class HRRequest(BaseModel):
    employee_id: str
    request_type: str   # leave, salary, onboarding, general
    message: str


# ----------------------------------------------------
# SENTIMENT ANALYSIS
# ----------------------------------------------------
def get_sentiment(text: str) -> str:
    try:
        r = requests.post(MODEL_URL, json={"text": text}, timeout=5)
        r.raise_for_status()
        return r.json().get("prediction", "unknown")
    except:
        return "unknown"


# ----------------------------------------------------
# HR LOGIC HANDLERS
# ----------------------------------------------------
def process_leave_request(emp: str, msg: str):
    return f"Leave request received for employee {emp}. HR will review and update you soon."


def process_salary_request(emp: str, msg: str):
    return f"Salary details request received. Current payroll cycle is active. Finance team will respond shortly."


def process_onboarding(emp: str, msg: str):
    return f"Onboarding request noted for employee {emp}. HR will assist you with the next steps."


def process_general(emp: str, msg: str):
    return f"Your message has been received. HR will look into it."


# ----------------------------------------------------
# MAIN ENDPOINT
# ----------------------------------------------------
@app.post("/process_request")
def process_request(payload: HRRequest):

    sentiment = get_sentiment(payload.message)

    # Intelligent HR routing
    if payload.request_type.lower() == "leave":
        reply = process_leave_request(payload.employee_id, payload.message)

    elif payload.request_type.lower() == "salary":
        reply = process_salary_request(payload.employee_id, payload.message)

    elif payload.request_type.lower() == "onboarding":
        reply = process_onboarding(payload.employee_id, payload.message)

    else:
        reply = process_general(payload.employee_id, payload.message)

    # Special handling for negative messages
    escalation = None
    if sentiment == "negative":
        escalation = "Employee message seems negative. HR should follow up personally."

    return {
        "status": "processed",
        "agent": "HR",
        "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "response": reply,
        "sentiment": sentiment,
        "escalation": escalation
    }
