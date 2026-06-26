from typing import Any, cast

import os
import re
from dotenv import load_dotenv
import yt_dlp
from pydub import AudioSegment

load_dotenv()

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

COOKIE_FILE = os.getenv("YTDLP_COOKIEFILE") or os.getenv("YTDLP_COOKIES_FILE")
YTDLP_USERNAME = os.getenv("YTDLP_USERNAME")
YTDLP_PASSWORD = os.getenv("YTDLP_PASSWORD")


def download_youtube_audio(url: str, cookie_path: str | None = None) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = cast(Any, {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "no_color": True,
        "nocheckcertificate": True,
        "extractor_args": {"youtube": {"skip": ["dash", "hls"]}},
    })

    if cookie_path:
        cookie_path = os.path.expanduser(cookie_path)
        if os.path.isfile(cookie_path):
            ydl_opts["cookiefile"] = cookie_path
        else:
            raise RuntimeError(
                f"Cookie file path provided, but the file does not exist: {cookie_path}"
            )
    elif COOKIE_FILE:
        cookie_path = os.path.expanduser(COOKIE_FILE)
        if os.path.isfile(cookie_path):
            ydl_opts["cookiefile"] = cookie_path
        else:
            raise RuntimeError(
                f"YTDLP_COOKIEFILE is set to '{cookie_path}', but the file does not exist."
            )

    if YTDLP_USERNAME and YTDLP_PASSWORD:
        ydl_opts["username"] = YTDLP_USERNAME
        ydl_opts["password"] = YTDLP_PASSWORD

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
        return filename
    except Exception as e:
        message = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", str(e))
        lowered = message.lower()
        if any(term in lowered for term in ["please sign in", "sign-in", "login", "account", "restricted"]):
            raise RuntimeError(
                "YouTube download failed because this video requires sign-in or restricted access. "
                "Use a public video URL, a local file, or set a valid YouTube cookies file with YTDLP_COOKIEFILE in .env."
            ) from e
        raise RuntimeError(f"YouTube download failed: {message}") from e


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str, cookie_path: str | None = None) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source, cookie_path)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks