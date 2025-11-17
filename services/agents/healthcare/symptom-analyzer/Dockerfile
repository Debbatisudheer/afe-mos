# -------------------------
# 1. Build Stage
# -------------------------
FROM golang:1.21 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64

RUN go build -o app main.go

# -------------------------
# 2. Run Stage
# -------------------------
FROM alpine:3.19

WORKDIR /app

COPY --from=builder /app/app .

EXPOSE 8001

CMD ["./app"]
