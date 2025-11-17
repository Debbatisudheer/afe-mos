# ----------------------------
# Vitals Monitor Agent Dockerfile
# ----------------------------
FROM python:3.10

# Set work directory
WORKDIR /app

# Add only FastAPI + requests (minimal)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

EXPOSE 8010

CMD ["python", "main.py"]
