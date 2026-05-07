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

# android client bypasses n-challenge natively — do NOT pass cookiefile globally
# as it causes android to be skipped, leaving only legacy 360p stream available.
# Cookies are loaded but only used when explicitly needed (e.g. age-restricted).
def get_base_opts():
    return {
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }

@app.get("/formats")
def list_formats(url: str):
    """Debug endpoint — returns all available formats for a URL."""
    opts = {"quiet": True, **get_base_opts()}
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "height": f.get("height"),
                    "width": f.get("width"),
                    "vcodec": f.get("vcodec"),
                    "acodec": f.get("acodec"),
                    "filesize": f.get("filesize"),
                    "tbr": f.get("tbr"),
                }
                for f in info.get("formats", [])
            ]
            return {"formats": formats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/info")
def get_info(url: str):
    opts = {"quiet": True, **get_base_opts()}
    # Do not pass cookiefile — causes android client to be skipped
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
        # Do not pass cookiefile — causes android client to be skipped
        out_path = f"{filepath}.mp3"
        media_type = "audio/mpeg"
    else:
        fmt = (
            f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        )
        ydl_opts = {
            **get_base_opts(),
            "format": fmt,
            "outtmpl": f"{filepath}.mp4",
            "merge_output_format": "mp4",
        }
        # Do not set cookiefile — it causes android client to be skipped
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
