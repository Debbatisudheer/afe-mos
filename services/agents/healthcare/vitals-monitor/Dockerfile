FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn requests --no-cache-dir

EXPOSE 8010

CMD ["python", "main.py"]
