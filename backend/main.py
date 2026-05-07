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

# When cookies are present: use default web client (supports cookies, Node.js handles n-challenge)
# When no cookies: use android client (bypasses n-challenge without Node.js)
def get_base_opts():
    if COOKIES_FILE:
        return {}  # web client used by default; Node.js in container solves n-challenge
    return {"extractor_args": {"youtube": {"player_client": ["android", "web"]}}}

@app.get("/info")
def get_info(url: str):
    opts = {"quiet": True, **get_base_opts()}
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
def download(url: str, format: str = "mp3", quality: str = "720"):
    if format not in ("mp3", "mp4"):
        raise HTTPException(status_code=400, detail="format must be mp3 or mp4")
    if quality not in ("480", "720", "1080"):
        raise HTTPException(status_code=400, detail="quality must be 480, 720, or 1080")
    filename = str(uuid.uuid4())
    filepath = f"{DOWNLOAD_DIR}/{filename}"

    if format == "mp3":
        ydl_opts = {
            **get_base_opts(),
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
        # Prefer exact height, fall back to next best mp4, then any best
        fmt = f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={quality}]+bestaudio/best[ext=mp4]/best"
        ydl_opts = {
            **get_base_opts(),
            "format": fmt,
            "outtmpl": f"{filepath}.mp4",
            "merge_output_format": "mp4",
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
