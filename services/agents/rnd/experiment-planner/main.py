from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import uuid
import os
import time
import json

app = FastAPI()

class ExperimentInput(BaseModel):
    description: str
    code: str

@app.get("/")
def root():
    return {"status": "R&D Experiment Planner running"}

@app.post("/run_experiment")
def run_experiment(exp: ExperimentInput):

    request_id = str(uuid.uuid4())[:8]
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    # SAFE: Write experiment code with UTF-8
    filename = f"exp_{request_id}.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(exp.code + "\n")

    try:
        # Windows-safe Subprocess call
        result = subprocess.run(
            ["python", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            timeout=5
        )
    except Exception as e:
        raise HTTPException(500, f"Experiment execution failed: {e}")

    # Clean up file
    try:
        os.remove(filename)
    except:
        pass

    return {
        "status": "completed",
        "experiment_id": request_id,
        "timestamp": ts,
        "description": exp.description,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
