"""
SYSTRAN Faster-Whisper service for audio transcription.
Uses the faster-whisper library for fast, accurate speech-to-text.
"""

import os
from typing import Optional, Dict, Any
from faster_whisper import WhisperModel


# Initialize the Whisper model
_model_instance: Optional[WhisperModel] = None


def get_model() -> WhisperModel:
    """Get or initialize the Whisper model instance."""
    global _model_instance
    
    if _model_instance is None:
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        device = os.getenv("WHISPER_DEVICE", "cpu")
        compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        
        _model_instance = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
    
    return _model_instance


async def transcribe_audio(audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Transcribe audio file using Faster-Whisper.
    
    Args:
        audio_path: Path to the audio file
        language: Optional language code (e.g., 'en', 'es'). Auto-detected if None.
        
    Returns:
        Dictionary containing transcript, segments, and metadata
    """
    model = get_model()
    
    # Transcribe the audio
    segments, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=5,
        vad_filter=True
    )
    
    # Collect segments
    segment_list = []
    full_transcript = []
    
    for segment in segments:
        segment_data = {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        }
        segment_list.append(segment_data)
        full_transcript.append(segment.text.strip())
    
    # Combine into full transcript
    transcript = " ".join(full_transcript)
    
    return {
        "transcript": transcript,
        "segments": segment_list,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration
    }

