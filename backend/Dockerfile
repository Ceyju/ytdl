FROM python:3.11-slim

# Install FFmpeg, curl, unzip
RUN apt-get update && apt-get install -y curl ffmpeg unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Deno (yt-dlp EJS runtime for n-challenge solving)
RUN curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "yt-dlp @ https://github.com/yt-dlp/yt-dlp/archive/refs/heads/master.tar.gz"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
