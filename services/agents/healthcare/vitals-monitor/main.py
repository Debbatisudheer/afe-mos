# services/orchestrator/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# -----------------------------
# URLs for Render microservices
# -----------------------------
SYMPTOM_ANALYZER_URL = os.getenv(
    "SYMPTOM_ANALYZER_URL",
    "https://symptom-analyzer-wi82.onrender.com/diagnose"
)

# (Later we will also call model-serving; keeping it optional now)
MODEL_SERVING_URL = os.getenv(
    "MODEL_SERVING_URL",
    "https://model-serving-s7cj.onrender.com/predict"
)

# -----------------------------
# Request format from vitals-monitor
# -----------------------------
class VitalsAlert(BaseModel):
    patient_id: str
    metric: str
    value: float
    ts: str
    severity: str

@app.get("/")
def root():
    return {"status": "orchestrator-running"}

# --------------------------------------
# Vitals Monitor → Orchestrator endpoint
# --------------------------------------
@app.post("/api/v1/vitals_alert")
def receive_vitals_alert(alert: VitalsAlert):
    """
    Receives abnormal vitals from vitals-monitor service.
    Then forwards patient text/condition to Symptom Analyzer.
    """

    # -----------------------------
    # Example patient message for demo
    # Later you can pass real clinical text
    # -----------------------------
    patient_text = f"Patient has abnormal {alert.metric} with value {alert.value}"

    try:
        # Forward to Symptom Analyzer
        response = requests.post(
            SYMPTOM_ANALYZER_URL,
            json={"patient_id": alert.patient_id, "text": patient_text},
            timeout=10
        )
        response.raise_for_status()

        diagnosis = response.json()

        return {
            "status": "received",
            "forward_status": "success",
            "diagnosis_response": diagnosis
        }

    except Exception as e:
        return {
            "status": "received",
            "forward_status": "failed",
            "error": str(e)
        }


# -----------------------
# REQUIRED FOR RENDER
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
