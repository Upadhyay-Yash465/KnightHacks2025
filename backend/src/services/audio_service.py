"""
audio_service.py
Low-level audio utilities using Librosa for pitch, pace, and volume analysis.
"""

import librosa
import numpy as np
import logging


class AudioService:
    """Provides reusable Librosa-based analysis utilities."""

    @staticmethod
    def analyze_audio(audio_path: str) -> dict:
        """Extract basic tempo, pitch, and loudness metrics."""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            pitch = np.mean(librosa.yin(y, fmin=80, fmax=300))
            rms = np.mean(librosa.feature.rms(y=y))
            return {
                "duration_sec": round(duration, 2),
                "tempo_bpm": round(float(tempo), 2),
                "avg_pitch_hz": round(float(pitch), 2),
                "avg_volume_rms": round(float(rms), 4),
            }
        except Exception as e:
            logging.error(f"AudioService error: {e}")
            return {"error": str(e)}
