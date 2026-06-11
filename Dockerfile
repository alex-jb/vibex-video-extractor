FROM python:3.12-slim

# ffmpeg is yt-dlp's hard dependency for muxing audio+video tracks.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Railway sets $PORT dynamically; uvicorn reads it from env in main.py.
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -fsS http://localhost:${PORT:-8000}/healthz || exit 1

CMD ["python", "main.py"]
