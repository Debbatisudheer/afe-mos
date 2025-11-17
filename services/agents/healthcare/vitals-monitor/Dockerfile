FROM python:3.10

WORKDIR /app

# Copy all files from vitals-monitor directory
COPY . .

# Install dependencies directly
RUN pip install fastapi uvicorn requests --no-cache-dir

EXPOSE 8010

CMD ["python", "main.py"]
