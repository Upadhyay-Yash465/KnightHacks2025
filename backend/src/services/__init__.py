"""
services/__init__.py
Dynamic runtime initializer for AI Speech Coach services.
Detects available APIs (Gemini, OpenAI) and hardware (GPU/CPU)
to auto-configure optimal model execution for Whisper, Gemini, and CV tasks.
"""

import os
import logging
import torch

def detect_environment():
    """Detects GPU availability and environment configuration."""
    has_gpu = torch.cuda.is_available()
    google_api = bool(os.getenv("GOOGLE_API_KEY"))
    openai_api = bool(os.getenv("OPENAI_API_KEY"))

    if has_gpu:
        device = torch.cuda.get_device_name(0)
    else:
        device = "CPU"

    logging.info("🧠 Runtime environment check:")
    logging.info(f" - GPU Available: {has_gpu}")
    logging.info(f" - Device: {device}")
    logging.info(f" - Gemini API: {'✅' if google_api else '❌'}")
    logging.info(f" - OpenAI API: {'✅' if openai_api else '❌'}")

    return {
        "device": device,
        "has_gpu": has_gpu,
        "gemini_enabled": google_api,
        "openai_enabled": openai_api
    }

# Run environment detection on module import
RUNTIME = detect_environment()

# Export service layer components
from .audio_service import AudioService
from .nlp_service import NLPService
from .vision_service import VisionService
from .whisper_service import WhisperService

__all__ = [
    "RUNTIME",
    "AudioService",
    "NLPService",
    "VisionService",
    "WhisperService"
]
