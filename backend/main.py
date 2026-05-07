from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp, os, uuid, tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ytdl-bxd.pages.dev"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

COOKIES_FILE = None
yt_cookies = os.environ.get("YT_COOKIES")
if yt_cookies:
    _cookies_tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    _cookies_tmp.write(yt_cookies)
    _cookies_tmp.close()
    COOKIES_FILE = _cookies_tmp.name

@app.get("/info")
def get_info(url: str):
    opts = {"quiet": True}
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info["title"],
                "thumbnail": info["thumbnail"],
                "duration": info["duration"],
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        if COOKIES_FILE:
            ydl_opts["cookiefile"] = COOKIES_FILE
        out_path = f"{filepath}.mp3"
        media_type = "audio/mpeg"
    else:
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": f"{filepath}.mp4",
        }
        if COOKIES_FILE:
            ydl_opts["cookiefile"] = COOKIES_FILE
        out_path = f"{filepath}.mp4"
        media_type = "video/mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    ext = "mp3" if format == "mp3" else "mp4"
    return FileResponse(
        out_path,
        media_type=media_type,
        filename=f"download.{ext}",
    )


@app.get("/health")
def health():
    return {"status": "ok"}
