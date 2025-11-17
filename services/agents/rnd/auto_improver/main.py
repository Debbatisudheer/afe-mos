# services/agents/rnd/auto_improver/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, threading, time, re, uuid
from typing import List, Optional

app = FastAPI(title="R&D Auto Improver")

# Config: orchestrator endpoint for experiments
ORCHESTRATOR_EXP_URL = "http://localhost:8000/api/v1/run_experiment"

# Model server URL (used as fallback metric source)
MODEL_URL = "http://localhost:8050/predict"

# Simple in-memory status store (replace with DB for production)
state = {
    "running": False,
    "job_id": None,
    "best": {"param": None, "metric": float("-inf"), "stdout": None},
    "history": []
}

# Input model for starting an auto-improve job
class AutoImproveRequest(BaseModel):
    # a code template must contain the token {param} which will be replaced
    code_template: str
    param_name: str = "param"
    param_values: List[float]           # list of values to try each iteration (grid)
    iterations: int = 5                 # how many rounds of search to run
    delay_between_rounds: float = 0.5   # seconds between experiment submissions

# Simple extractor: looks for "METRIC: <number>" in stdout
_metric_re = re.compile(r"METRIC:\s*([0-9.+-eE]+)")

def parse_metric_from_stdout(stdout: str) -> Optional[float]:
    if not stdout:
        return None
    m = _metric_re.search(stdout)
    if not m:
        return None
    try:
        return float(m.group(1))
    except:
        return None

def submit_experiment_via_orchestrator(description: str, code: str, timeout: int = 15):
    payload = {"description": description, "code": code}
    r = requests.post(ORCHESTRATOR_EXP_URL, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()   # expects experiment_result with stdout/stderr

def model_score(text: str) -> float:
    """
    Fallback metric: send text to model-serving /predict.
    Converts model labels to numeric score:
      positive -> 1.0
      negative -> -1.0
      unknown/other -> 0.0
    """
    try:
        if not text:
            return 0.0
        r = requests.post(MODEL_URL, json={"text": text}, timeout=5)
        r.raise_for_status()
        pred = r.json().get("prediction", "").lower()
        if pred == "positive":
            return 1.0
        if pred == "negative":
            return -1.0
        return 0.0
    except Exception as e:
        # On failure, return neutral score
        return 0.0

def auto_improve_job(job_id: str, req: AutoImproveRequest):
    try:
        state["running"] = True
        state["job_id"] = job_id
        state["history"].clear()
        state["best"] = {"param": None, "metric": float("-inf"), "stdout": None}

        for it in range(1, req.iterations + 1):
            if not state["running"]:
                break
            # Iterate over param grid
            for v in req.param_values:
                if not state["running"]:
                    break
                code = req.code_template.replace("{param}", str(v))
                desc = f"autoimprove_job={job_id} iter={it} try={v}"
                try:
                    result = submit_experiment_via_orchestrator(desc, code)
                except Exception as e:
                    # record failure and continue
                    state["history"].append({
                        "iter": it, "param": v, "metric": None, "error": str(e)
                    })
                    time.sleep(req.delay_between_rounds)
                    continue

                # experiment_result expected shape: { status, stdout, stderr, ... }
                exp = result.get("experiment_result") or result
                stdout = exp.get("stdout", "") or ""
                stderr = exp.get("stderr", "") or ""
                # Try parsing numeric metric first
                metric = parse_metric_from_stdout(stdout)

                # If no numeric metric, use model_score using stdout (fallback)
                if metric is None:
                    # prefer first non-empty line of stdout, else use code text
                    candidate_text = stdout.strip()
                    if not candidate_text:
                        # fallback to code itself (some experiments print nothing)
                        candidate_text = code
                    metric = model_score(candidate_text)

                # store record
                record = {
                    "iter": it,
                    "param": v,
                    "metric": metric,
                    "stdout": stdout,
                    "stderr": stderr
                }
                state["history"].append(record)

                # update best
                if metric is not None and metric > state["best"]["metric"]:
                    state["best"] = {"param": v, "metric": metric, "stdout": stdout}

                time.sleep(req.delay_between_rounds)

        state["running"] = False
    except Exception as e:
        state["running"] = False
        state["history"].append({"error": str(e)})
    finally:
        state["job_id"] = None

@app.post("/start")
def start_autoimprove(req: AutoImproveRequest):
    if state["running"]:
        raise HTTPException(status_code=400, detail="Auto-improver already running")

    job_id = str(uuid.uuid4())[:8]
    t = threading.Thread(target=auto_improve_job, args=(job_id, req), daemon=True)
    t.start()
    return {"status": "started", "job_id": job_id}

@app.post("/stop")
def stop_autoimprove():
    if not state["running"]:
        return {"status": "not_running"}
    state["running"] = False
    return {"status": "stopping"}

@app.get("/status")
def get_status():
    return {
        "running": state["running"],
        "job_id": state["job_id"],
        "best": state["best"],
        "history_len": len(state["history"])
    }

@app.get("/history")
def get_history():
    # return latest 200 records
    return state["history"][-200:]
