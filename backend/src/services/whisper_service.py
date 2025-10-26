"""
whisper_service.py
Wrapper for SYSTRAN Faster-Whisper transcription.
"""

from faster_whisper import WhisperModel
import logging


class WhisperService:
    def __init__(self, model_size="base"):
        self.model = WhisperModel(f"systran/faster-whisper-{model_size}")

    def transcribe(self, audio_path: str) -> str:
        """Return plain transcript string."""
        try:
            segments, _ = self.model.transcribe(audio_path)
            return " ".join([s.text.strip() for s in segments])
        except Exception as e:
            logging.error(f"WhisperService error: {e}")
            return ""
