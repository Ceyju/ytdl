from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp, os, uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ramify.kurtangelobenavides-mejorada.workers.dev/"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.get("/info")
def get_info(url: str):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info["title"],
            "thumbnail": info["thumbnail"],
            "duration": info["duration"],
        }


@app.get("/download")
def download(url: str, format: str = "mp3"):
    filename = str(uuid.uuid4())
    filepath = f"{DOWNLOAD_DIR}/{filename}"

    if format == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": filepath,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
        }
        out_path = f"{filepath}.mp3"
        media_type = "audio/mpeg"
    else:
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": f"{filepath}.mp4",
        }
        out_path = f"{filepath}.mp4"
        media_type = "video/mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    ext = "mp3" if format == "mp3" else "mp4"
    return FileResponse(
        out_path,
        media_type=media_type,
        filename=f"download.{ext}",
    )


@app.get("/health")
def health():
    return {"status": "ok"}
