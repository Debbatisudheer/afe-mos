FROM python:3.10

WORKDIR /app

# Copy only the vitals-monitor service folder
COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8010

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
