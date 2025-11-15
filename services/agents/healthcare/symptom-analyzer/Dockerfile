# Build Stage
FROM golang:1.21 AS builder

WORKDIR /app
COPY . .

RUN go mod init symptom-analyzer || true
RUN go mod tidy
RUN go build -o app .

# Run Stage
FROM alpine:latest

WORKDIR /app
COPY --from=builder /app/app .

EXPOSE 8001
CMD ["./app"]
