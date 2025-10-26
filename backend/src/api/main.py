"""
main.py
FastAPI entrypoint for the AI Speech Coach system.
Handles:
 - File uploads (audio/video)
 - Orchestrator pipeline execution
 - JSON feedback response
"""

import os
import json
import asyncio
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile

# Load environment configuration
from src.config.settings import config

from src.agents.multimodal_orchestrator import MultimodalOrchestrator as OrchestratorAgent

# -------------------------------
# Setup FastAPI
# -------------------------------
app = FastAPI(title="AI Speech Coach API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OrchestratorAgent()

# -------------------------------
# Health check route
# -------------------------------
@app.get("/")
async def root():
    return {"status": "✅ API is live", "message": "AI Speech Coach backend running."}

# -------------------------------
# Upload + Analyze Route
# -------------------------------
@app.post("/analyze")
async def analyze(
    audio: UploadFile = File(None),
    video: UploadFile = File(None)
):
    """
    Accepts uploaded audio/video files, runs the orchestrator pipeline,
    and returns structured JSON feedback.
    """
    try:
        # Save temporary files
        audio_path = None
        video_path = None
        
        if audio:
            with NamedTemporaryFile(delete=False, suffix=".wav") as audio_temp:
                audio_temp.write(await audio.read())
                audio_path = audio_temp.name

        if video:
            # Determine file extension based on content type or filename
            video_extension = ".webm"  # Default to webm since that's what frontend sends
            if video.filename:
                if video.filename.endswith('.mp4'):
                    video_extension = ".mp4"
                elif video.filename.endswith('.webm'):
                    video_extension = ".webm"
                elif video.filename.endswith('.mov'):
                    video_extension = ".mov"
            
            with NamedTemporaryFile(delete=False, suffix=video_extension) as video_temp:
                video_temp.write(await video.read())
                video_path = video_temp.name

        # Check if at least one file is provided
        if not audio_path and not video_path:
            raise HTTPException(status_code=400, detail="No audio or video file provided")

        # Run orchestrator asynchronously
        result = await orchestrator.run(audio_path, video_path)

        # Clean up temporary files
        if audio_path:
            os.remove(audio_path)
        if video_path:
            os.remove(video_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

# -------------------------------
# Local Development Entrypoint
# -------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
