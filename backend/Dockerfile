FROM python:3.11-slim

# Install FFmpeg and Node.js 20 (Node required for yt-dlp n-challenge solver)
RUN apt-get update && apt-get install -y curl ffmpeg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt_dlp-latest.tar.gz

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
