"""
AI Speech Coach - Agents Package
Includes modular sub-agents for handling speech, context, and visual analysis.
"""
from .voice_agent import VoiceAgent
from .context_agent import ContextAgent
from .video_agent import VideoAgent
from .orchestrator_agent import OrchestratorAgent

__all__ = [
    "VoiceAgent",
    "ContextAgent",
    "VideoAgent",
    "OrchestratorAgent"
]
