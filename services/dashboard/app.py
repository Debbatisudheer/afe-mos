import streamlit as st
import requests

st.set_page_config(page_title="AFE-MOS Dashboard", page_icon="🩺", layout="centered")

st.title("🩺 AFE-MOS Dashboard")
st.write("Simple interface to test all your deployed services.")

# -----------------------------
# SERVICE URLS (CHANGE THESE)
# -----------------------------
VITALS_URL = "http://localhost:8010/send_vitals"
ORCH_URL   = "http://localhost:8000/api/v1/vitals_alert"
SYMPTOM_URL = "http://localhost:8001/diagnose"

tab1, tab2, tab3 = st.tabs(["📡 Send Vitals", "🧠 Orchestrator", "🩺 Symptom Analyzer"])


# -----------------------------
# TAB 1 — VITALS MONITOR
# -----------------------------
with tab1:
    st.subheader("📡 Send Vitals to Vitals-Monitor")

    pid = st.text_input("Patient ID", "P1")
    metric = st.selectbox("Metric", ["HR", "SpO2", "BP_sys"])
    value = st.number_input("Value", value=130.0)

    if st.button("Send Vitals"):
        data = {"patient_id": pid, "metric": metric, "value": value}
        try:
            r = requests.post(VITALS_URL, json=data)
            st.json(r.json())
        except Exception as e:
            st.error(str(e))


# -----------------------------
# TAB 2 — ORCHESTRATOR
# -----------------------------
with tab2:
    st.subheader("🧠 Trigger Orchestrator Manually")

    pid = st.text_input("Patient ID (Orch)", "P1")
    metric = st.text_input("Metric", "HR")
    value = st.number_input("Value", value=120.0)
    severity = st.selectbox("Severity", ["medium", "high"])

    if st.button("Send Alert → Orchestrator"):
        data = {"patient_id": pid, "metric": metric, "value": value, "severity": severity}
        try:
            r = requests.post(ORCH_URL, json=data)
            st.json(r.json())
        except Exception as e:
            st.error(str(e))


# -----------------------------
# TAB 3 — SYMPTOM ANALYZER
# -----------------------------
with tab3:
    st.subheader("🩺 Run Symptom Analyzer")

    pid = st.text_input("Patient ID (Symptom)", "P1")
    text = st.text_area("Patient Symptoms", "I am feeling tired and coughing.")

    if st.button("Analyze Symptoms"):
        data = {"patient_id": pid, "text": text}
        try:
            r = requests.post(SYMPTOM_URL, json=data)
            st.json(r.json())
        except Exception as e:
            st.error(str(e))
