# services/orchestrator/main.py
from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

# -------------------------------
# AGENT ENDPOINTS (LOCAL DEV)
# -------------------------------
SYMPTOM_AGENT_URL = os.getenv("SYMPTOM_AGENT_URL", "http://localhost:8001/diagnose")
HR_AGENT_URL = os.getenv("HR_AGENT_URL", "http://localhost:8020/process_request")
RND_AGENT_URL = os.getenv("RND_AGENT_URL", "http://localhost:8030/run_experiment")

# -------------------------------
# BASIC ROOT CHECK
# -------------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "orchestrator"}

# -------------------------------
# HEALTHCARE: SYMPTOM ANALYZER
# -------------------------------
@app.post("/api/v1/submit_symptoms")
def submit_symptoms(payload: dict):

    patient_id = payload.get("patient_id")
    text = payload.get("text")

    if not patient_id or not text:
        raise HTTPException(status_code=400, detail="Missing: patient_id, text")

    try:
        r = requests.post(
            SYMPTOM_AGENT_URL,
            json={"patient_id": patient_id, "text": text},
            timeout=5
        )
        r.raise_for_status()
        agent_resp = r.json()
        return {"status": "accepted", "agent_response": agent_resp}

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Symptom Agent error: {str(e)}")

# -------------------------------
# HEALTHCARE: VITALS MONITOR ALERT
# -------------------------------
@app.post("/api/v1/vitals_alert")
def vitals_alert(payload: dict):

    patient_id = payload.get("patient_id")
    metric = payload.get("metric")
    value = payload.get("value")
    severity = payload.get("severity", "medium")

    if not patient_id or metric is None or value is None:
        raise HTTPException(400, "Missing: patient_id, metric, value")

    print(f"[ALERT] patient={patient_id} metric={metric} value={value} severity={severity}")

    triage_text = f"Vitals alert: {metric}={value} (severity={severity})"

    try:
        r = requests.post(
            SYMPTOM_AGENT_URL,
            json={"patient_id": patient_id, "text": triage_text},
            timeout=5
        )
        r.raise_for_status()
        agent_resp = r.json()

        return {
            "status": "received",
            "forward_status": "ok",
            "agent_response": agent_resp
        }

    except Exception as e:
        return {
            "status": "received",
            "forward_status": "failed",
            "error": str(e)
        }

# -------------------------------
# ENTERPRISE: HR AGENT
# -------------------------------
@app.post("/api/v1/hr_request")
def hr_request(payload: dict):

    employee_id = payload.get("employee_id")
    request_type = payload.get("request_type")
    message = payload.get("message")

    if not employee_id or not request_type or not message:
        raise HTTPException(400, "Missing: employee_id, request_type, message")

    try:
        r = requests.post(HR_AGENT_URL, json=payload, timeout=5)
        r.raise_for_status()
        return {"status": "ok", "hr_response": r.json()}

    except Exception as e:
        raise HTTPException(502, f"HR Agent error: {str(e)}")

# -------------------------------
# R&D: EXPERIMENT PLANNER AGENT
# -------------------------------
@app.post("/api/v1/run_experiment")
def run_experiment(payload: dict):

    description = payload.get("description")
    code = payload.get("code")

    if not description or not code:
        raise HTTPException(400, "Missing: description or code")

    try:
        r = requests.post(RND_AGENT_URL, json=payload, timeout=10)
        r.raise_for_status()
        return {"status": "ok", "experiment_result": r.json()}

    except Exception as e:
        raise HTTPException(502, f"Experiment Agent error: {str(e)}")
