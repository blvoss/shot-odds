import os
import uuid

import cv2
import yt_dlp

VIDEO_STORAGE_DIR = os.environ.get("VIDEO_STORAGE_DIR", "./storage/videos")
FRAME_STORAGE_DIR = os.environ.get("FRAME_STORAGE_DIR", "./storage/frames")

os.makedirs(VIDEO_STORAGE_DIR, exist_ok=True)
os.makedirs(FRAME_STORAGE_DIR, exist_ok=True)


def save_uploaded_video(filename: str, content: bytes) -> str:
    ext = os.path.splitext(filename)[1] or ".mp4"
    dest_path = os.path.join(VIDEO_STORAGE_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(dest_path, "wb") as f:
        f.write(content)
    return dest_path


def download_youtube_video(url: str) -> str:
    dest_template = os.path.join(VIDEO_STORAGE_DIR, f"{uuid.uuid4().hex}.%(ext)s")
    ydl_opts = {
        "format": "mp4/bestvideo+bestaudio/best",
        "outtmpl": dest_template,
        "merge_output_format": "mp4",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def extract_first_frame(video_path: str, match_id: int) -> tuple[str, int, int]:
    """Extracts the first frame of the video as a JPEG for calibration.

    Returns (frame_path, width, height).
    """
    cap = cv2.VideoCapture(video_path)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise ValueError(f"Could not read first frame from video: {video_path}")

    height, width = frame.shape[:2]
    frame_path = os.path.join(FRAME_STORAGE_DIR, f"match_{match_id}_first_frame.jpg")
    cv2.imwrite(frame_path, frame)
    return frame_path, width, height
