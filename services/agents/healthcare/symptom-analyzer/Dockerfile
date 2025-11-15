# Build Stage
FROM golang:1.21 AS builder

WORKDIR /app
COPY . .

# ❗ Build STATIC binary (VERY IMPORTANT)
ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64
RUN go build -o app .

# Run Stage
FROM scratch

WORKDIR /app
COPY --from=builder /app/app .

EXPOSE 8001
CMD ["./app"]
