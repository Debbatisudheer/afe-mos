import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AFE-MOS Dashboard",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------------------
# Sidebar Navigation
# -----------------------------------------------
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["🏠 System Overview", "🔬 R&D Auto-Improver", "💬 Sentiment Tester", "👔 HR Agent"]
)

# -----------------------------------------------
# 1) SYSTEM OVERVIEW
# -----------------------------------------------
if page == "🏠 System Overview":
    st.title("🚀 AFE-MOS – Multi-Agent System Dashboard")

    st.subheader("System Health Check")

    services = {
        "Symptom Analyzer (8001)": "http://localhost:8001/diagnose",
        "Vitals Monitor (8010)": "http://localhost:8010/send_vitals",
        "HR Agent (8020)": "http://localhost:8020/process_request",
        "Orchestrator (8000)": "http://localhost:8000/",
        "R&D Auto Improver (8040)": "http://localhost:8040/status",
        "Model Serving (8050)": "http://localhost:8050/predict"
    }

    cols = st.columns(2)
    i = 0

    for name, url in services.items():
        i += 1
        with cols[i % 2]:
            try:
                requests.get(url, timeout=1)
                st.success(f"🟢 {name}")
            except:
                st.error(f"🔴 {name}")

# -----------------------------------------------
# 2) R&D AUTO-IMPROVER
# -----------------------------------------------
elif page == "🔬 R&D Auto-Improver":
    st.title("🔬 R&D Auto-Improver – Live Results")

    status_url = "http://localhost:8040/status"
    history_url = "http://localhost:8040/history"

    if st.button("Refresh Status"):
        pass

    try:
        status = requests.get(status_url).json()
        st.subheader("📌 Current Status")
        st.json(status)
    except:
        st.error("Unable to reach Auto-Improver service.")

    st.subheader("📚 History")
    try:
        history = requests.get(history_url).json()
        st.json(history)
    except:
        st.error("Unable to load history.")

# -----------------------------------------------
# 3) SENTIMENT TESTER
# -----------------------------------------------
elif page == "💬 Sentiment Tester":
    st.title("💬 Sentiment Model Tester")

    text = st.text_area("Enter some text:")
    if st.button("Predict"):
        try:
            r = requests.post("http://localhost:8050/predict", json={"text": text})
            st.success(f"Prediction: {r.json()['prediction']}")
        except:
            st.error("Model server failed.")

# -----------------------------------------------
# 4) HR AGENT
# -----------------------------------------------
elif page == "👔 HR Agent":
    st.title("👔 HR Agent Interface")

    emp = st.text_input("Employee ID")
    req = st.selectbox("Request Type", ["leave", "salary", "onboarding", "general"])
    msg = st.text_area("Message")

    if st.button("Send Request"):
        try:
            payload = {
                "employee_id": emp,
                "request_type": req,
                "message": msg
            }
            r = requests.post("http://localhost:8020/process_request", json=payload)
            st.json(r.json())
        except:
            st.error("HR agent unreachable.")
