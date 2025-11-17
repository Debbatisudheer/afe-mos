# services/agents/healthcare/vitals-monitor/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import time
from typing import Optional

app = FastAPI()

# Orchestrator URL - when running locally, use localhost
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/api/v1/vitals_alert")

class VitalsPayload(BaseModel):
    patient_id: str
    metric: str           # e.g. "HR", "BP_sys", "BP_dia", "SpO2"
    value: float
    ts: Optional[str] = None

def severity_for(metric: str, value: float) -> str:
    """
    Simple heuristic rules - tweak for your use-case.
    """
    m = metric.lower()
    if m == "hr":
        if value < 40 or value > 120:
            return "high"
        if value < 55 or value > 100:
            return "medium"
        return "low"
    if m == "spo2":
        if value < 88:
            return "high"
        if value < 94:
            return "medium"
        return "low"
    if m.startswith("bp"):
        # assume value is systolic for simplicity
        if value > 180 or value < 80:
            return "high"
        if value > 140 or value < 90:
            return "medium"
        return "low"
    return "medium"

@app.post("/send_vitals")
def send_vitals(payload: VitalsPayload):
    """
    Endpoint that simulates receiving vitals from a device.
    If an anomaly is detected, this service will POST to orchestrator's /vitals_alert.
    """
    severity = severity_for(payload.metric, payload.value)
    # If severity is medium or high, create alert
    if severity in ("medium", "high"):
        alert = {
            "patient_id": payload.patient_id,
            "metric": payload.metric,
            "value": payload.value,
            "ts": payload.ts or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "severity": severity
        }
        try:
            r = requests.post(ORCHESTRATOR_URL, json=alert, timeout=5)
            r.raise_for_status()
            return {"status": "alert_sent", "orchestrator_response": r.json()}
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Failed to send alert to orchestrator: {e}")
    # If low severity, no alert (just ack)
    return {"status": "ok", "severity": severity}
