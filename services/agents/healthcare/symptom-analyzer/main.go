package main

import (
    "bytes"
    "encoding/json"
    "log"
    "net/http"
)

// -------------------------
// Request Body Structure
// -------------------------
type Request struct {
    PatientID string `json:"patient_id"`
    Text      string `json:"text"`
}

// --------------------------------------------------
// Sentiment Analysis (calls model-serving on port 8050)
// --------------------------------------------------
func GetSentiment(text string) string {
    payload := map[string]string{"text": text}
    jsonData, _ := json.Marshal(payload)

    resp, err := http.Post(
        "http://localhost:8050/predict",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        return "unknown"
    }
    defer resp.Body.Close()

    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)

    sentiment, ok := result["prediction"].(string)
    if !ok {
        return "unknown"
    }
    return sentiment
}

// -------------------------
// Diagnose Handler
// -------------------------
func diagnose(w http.ResponseWriter, r *http.Request) {
    var req Request
    json.NewDecoder(r.Body).Decode(&req)

    sentiment := GetSentiment(req.Text)

    resp := map[string]interface{}{
        "message":    "Diagnosis complete",
        "patient_id": req.PatientID,
        "diagnoses":  []string{"common cold", "viral infection"},
        "sentiment":  sentiment, // ← added!
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp)
}

// -------------------------
// MAIN
// -------------------------
func main() {
    http.HandleFunc("/diagnose", diagnose)
    log.Println("Symptom Analyzer running on port 8001...")
    http.ListenAndServe(":8001", nil)
}
