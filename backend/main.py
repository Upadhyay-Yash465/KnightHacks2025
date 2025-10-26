"""
Main FastAPI application for Aesop AI backend.
"""
import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import json
from dotenv import load_dotenv

# Import agents
from agents.transcriber import TranscriberAgent
from agents.voice_analyzer import VoiceAnalyzerAgent
from agents.emotion_analyzer import EmotionAnalyzerAgent
from agents.action_agent import ActionAgent

# Import utilities
from utils.video_utils import (
    extract_audio_from_video,
    extract_frames_at_interval,
    cleanup_temp_file
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Aesop AI Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents (lazy loading for faster startup)
transcriber_agent = None
voice_agent = None
emotion_agent = None
action_agent = None


def get_transcriber():
    global transcriber_agent
    if transcriber_agent is None:
        transcriber_agent = TranscriberAgent(model_size="base")
    return transcriber_agent


def get_voice_analyzer():
    global voice_agent
    if voice_agent is None:
        voice_agent = VoiceAnalyzerAgent()
    return voice_agent


def get_emotion_analyzer():
    global emotion_agent
    if emotion_agent is None:
        api_key = os.getenv("GEMINI_API_KEY")
        emotion_agent = EmotionAnalyzerAgent(api_key=api_key)
    return emotion_agent


def get_action_agent():
    global action_agent
    if action_agent is None:
        api_key = os.getenv("GEMINI_API_KEY")
        action_agent = ActionAgent(api_key=api_key)
    return action_agent


class ActionableAdviceRequest(BaseModel):
    agent_type: str
    analysis_data: Dict[str, Any]
    context: str = ""


@app.get("/")
def read_root():
    return {
        "message": "Aesop AI Backend API",
        "version": "1.0.0",
        "endpoints": ["/analyze", "/actionable-advice"]
    }


@app.post("/analyze")
async def analyze_speech(
    video: UploadFile = File(...),
    context: str = Form("")
):
    """
    Analyze uploaded video for speech quality.
    Returns transcription, voice analysis, and emotion analysis.
    """
    temp_video_path = None
    temp_audio_path = None
    
    try:
        # Save uploaded video to temp file
        temp_video_path = os.path.join(tempfile.gettempdir(), f"video_{os.getpid()}.webm")
        with open(temp_video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        print(f"Video saved to: {temp_video_path}")
        
        # Extract audio from video
        print("Extracting audio...")
        temp_audio_path = extract_audio_from_video(temp_video_path)
        print(f"Audio extracted to: {temp_audio_path}")
        
        # Extract frames from video (every 5 seconds)
        print("Extracting frames...")
        frames = extract_frames_at_interval(temp_video_path, interval_seconds=5.0)
        print(f"Extracted {len(frames)} frames")
        
        # Run Data Agents in parallel (or sequentially for simplicity)
        results = {}
        
        # 1. Transcriber Agent
        print("Running transcription...")
        transcriber = get_transcriber()
        transcription_result = transcriber.transcribe(temp_audio_path)
        results['transcription'] = transcription_result
        print(f"Transcription complete: {transcription_result['quality_score']}/10")
        
        # 2. Voice Analyzer Agent
        print("Running voice analysis...")
        voice_analyzer = get_voice_analyzer()
        voice_result = voice_analyzer.analyze(temp_audio_path)
        results['voice'] = voice_result
        print(f"Voice analysis complete")
        
        # 3. Emotion Analyzer Agent
        print("Running emotion analysis...")
        emotion_analyzer = get_emotion_analyzer()
        emotion_result = emotion_analyzer.analyze(frames)
        results['emotions'] = emotion_result
        print(f"Emotion analysis complete: {emotion_result['overall_rating']}/10")
        
        return results
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
    finally:
        # Cleanup temp files
        if temp_video_path:
            cleanup_temp_file(temp_video_path)
        if temp_audio_path:
            cleanup_temp_file(temp_audio_path)


@app.post("/actionable-advice")
async def get_actionable_advice(request: ActionableAdviceRequest):
    """
    Generate actionable advice based on analysis results.
    """
    try:
        action_agent = get_action_agent()
        
        advice = action_agent.generate_advice(
            agent_type=request.agent_type,
            analysis_data=request.analysis_data,
            context=request.context
        )
        
        return advice
        
    except Exception as e:
        print(f"Error generating advice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate advice: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Aesop AI Backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


