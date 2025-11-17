# ------------ BUILD STAGE ------------
FROM golang:1.25 AS builder

WORKDIR /app

COPY go.mod ./
RUN go mod tidy || true

COPY . .

ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64
RUN go build -o app main.go

# ------------ RUN STAGE ------------
FROM alpine:latest
WORKDIR /app

COPY --from=builder /app/app .

EXPOSE 8001
CMD ["./app"]
