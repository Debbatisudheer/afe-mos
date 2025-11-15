# services/model-serving/server.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI(title="Model Serving Agent")

# Load model + vectorizer
vec, model = joblib.load("model.pkl")

class PredictInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "model-serving-running"}

@app.post("/predict")
def predict(data: PredictInput):
    text = data.text
    X = vec.transform([text])
    pred = model.predict(X)[0]
    return {
        "input": text,
        "prediction": pred
    }
