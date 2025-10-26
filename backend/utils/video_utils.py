"""
Utilities for extracting audio and frames from video files.
"""
import os
import tempfile
import cv2
import numpy as np
from pathlib import Path


def extract_audio_from_video(video_path: str, output_audio_path: str = None) -> str:
    """
    Extract audio from video file using OpenCV and save as WAV.
    Returns the path to the extracted audio file.
    """
    if output_audio_path is None:
        # Create temp file for audio
        temp_dir = tempfile.gettempdir()
        output_audio_path = os.path.join(temp_dir, f"audio_{os.getpid()}.wav")
    
    # Use ffmpeg via os.system for audio extraction (more reliable than OpenCV for audio)
    cmd = f'ffmpeg -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{output_audio_path}" -y -loglevel error'
    result = os.system(cmd)
    
    if result != 0:
        raise RuntimeError(f"Failed to extract audio from video: {video_path}")
    
    return output_audio_path


def extract_frames_at_interval(video_path: str, interval_seconds: float = 5.0) -> list:
    """
    Extract frames from video at specified intervals.
    Returns list of tuples: [(timestamp_string, frame_image), ...]
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30  # Default fallback
    
    frame_interval = int(fps * interval_seconds)
    frames = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Extract frame at intervals
        if frame_count % frame_interval == 0:
            timestamp_seconds = frame_count / fps
            minutes = int(timestamp_seconds // 60)
            seconds = int(timestamp_seconds % 60)
            timestamp_str = f"{minutes}:{seconds:02d}"
            
            # Convert BGR to RGB for processing
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append((timestamp_str, frame_rgb))
        
        frame_count += 1
    
    cap.release()
    
    return frames


def save_frame_to_temp(frame: np.ndarray, prefix: str = "frame") -> str:
    """
    Save a frame to a temporary file and return the path.
    """
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{prefix}_{os.getpid()}_{id(frame)}.jpg")
    
    # Convert RGB to BGR for OpenCV
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(temp_path, frame_bgr)
    
    return temp_path


def cleanup_temp_file(file_path: str):
    """
    Remove a temporary file if it exists.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Failed to remove temp file {file_path}: {e}")


