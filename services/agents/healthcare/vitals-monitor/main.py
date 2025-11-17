# services/agents/healthcare/vitals-monitor/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import time
from typing import Optional
import uvicorn    # <-- REQUIRED FOR RENDER

app = FastAPI()

ORCHESTRATOR_URL = os.getenv(
    "ORCHESTRATOR_URL",
    "http://localhost:8000/api/v1/vitals_alert"
)

class VitalsPayload(BaseModel):
    patient_id: str
    metric: str
    value: float
    ts: Optional[str] = None

def severity_for(metric: str, value: float) -> str:
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
        if value > 180 or value < 80:
            return "high"
        if value > 140 or value < 90:
            return "medium"
        return "low"

    return "medium"

@app.post("/send_vitals")
def send_vitals(payload: VitalsPayload):
    severity = severity_for(payload.metric, payload.value)

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
            raise HTTPException(
                status_code=502,
                detail=f"Failed to send alert to orchestrator: {e}"
            )

    return {"status": "ok", "severity": severity}


# ------------------------------
# REQUIRED ENTRYPOINT FOR RENDER
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
