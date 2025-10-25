import librosa
import numpy as np

def analyze_voice(file_path: str) -> dict:
    """
    Analyze audio tone, pace, and filler sounds.
    """
    y, sr = librosa.load(file_path)
    duration = librosa.get_duration(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    pitch_mean = np.mean(librosa.yin(y, fmin=50, fmax=300))
    rms = np.mean(librosa.feature.rms(y=y))
    
    # Simulated emotion detection
    emotion = "confident" if rms > 0.03 else "neutral"
    
    return {
        "duration_sec": round(duration, 2),
        "tempo_bpm": round(tempo, 2),
        "pitch_mean": round(pitch_mean, 2),
        "volume_rms": round(rms, 4),
        "emotion": emotion,
        "voice_feedback": f"Your tone sounds {emotion}. Try varying pitch for emphasis."
    }
