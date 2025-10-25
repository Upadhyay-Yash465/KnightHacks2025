#!/usr/bin/env python3
"""
Enhanced test server with AI functionality for SpeechCoach
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import tempfile
import os
import logging
from typing import Dict, Any
import asyncio

# Import our AI services
from backend.services.systran_whisper_service import transcribe_audio
from backend.services.nlp_adk_service import analyze_transcript

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SpeechCoach AI API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user dependency for testing
async def get_current_user_mock() -> Dict[str, Any]:
    """Mock user for testing purposes"""
    return {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SpeechCoach AI API is running!", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Server is running",
        "ai_services": {
            "whisper": "available",
            "nlp": "available"
        }
    }

@app.post("/analyze-text")
async def analyze_text_only(
    request: dict,
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Analyze speech from text transcript only (no audio upload).
    
    This endpoint analyzes a provided transcript using Google ADK.
    """
    try:
        text = request.get("text", "")
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text transcript is required")
        
        logger.info("Analyzing provided transcript...")
        analysis_result = await analyze_transcript(text)
        
        if not analysis_result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"Analysis failed: {analysis_result.get('error', 'Unknown error')}"
            )
        
        result = {
            "analysis": {
                "filler_count": analysis_result["filler_count"],
                "clarity_score": analysis_result["clarity_score"],
                "suggestions": analysis_result["suggestions"],
                "summary": analysis_result["summary"],
                "filler_density": analysis_result["filler_density"],
                "total_words": analysis_result["total_words"],
                "filler_words": analysis_result.get("filler_words", [])
            },
            "metadata": {
                "text_length": len(text),
                "analysis_type": "text_only",
                "user_id": current_user["uid"]
            }
        }
        
        logger.info("Text analysis completed successfully")
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during text analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze-speech")
async def analyze_speech(
    audio_file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Analyze speech from uploaded audio file.
    
    This endpoint:
    1. Transcribes the audio using SYSTRAN Faster-Whisper
    2. Analyzes the transcript using Google ADK
    3. Returns structured feedback
    """
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Transcribe audio
            logger.info(f"Transcribing audio file: {audio_file.filename}")
            transcription_result = await transcribe_audio(temp_file_path)
            
            if not transcription_result["success"]:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
                )
            
            # Step 2: Analyze transcript
            logger.info("Analyzing transcript for speech clarity...")
            analysis_result = await analyze_transcript(transcription_result["transcript"])
            
            if not analysis_result["success"]:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Analysis failed: {analysis_result.get('error', 'Unknown error')}"
                )
            
            # Combine results
            result = {
                "transcription": {
                    "transcript": transcription_result["transcript"],
                    "language": transcription_result["language"],
                    "duration": transcription_result["duration"],
                    "confidence": transcription_result["confidence"],
                    "segments": transcription_result["segments"]
                },
                "analysis": {
                    "filler_count": analysis_result["filler_count"],
                    "clarity_score": analysis_result["clarity_score"],
                    "suggestions": analysis_result["suggestions"],
                    "summary": analysis_result["summary"],
                    "filler_density": analysis_result["filler_density"],
                    "total_words": analysis_result["total_words"],
                    "filler_words": analysis_result.get("filler_words", [])
                },
                "metadata": {
                    "filename": audio_file.filename,
                    "file_size": len(content),
                    "analysis_type": "audio_analysis",
                    "user_id": current_user["uid"]
                }
            }
            
            logger.info("Speech analysis completed successfully")
            return JSONResponse(content=result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during speech analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/test-ai")
async def test_ai_functionality():
    """Test endpoint to verify AI functionality"""
    try:
        # Test NLP analysis with sample text
        test_transcript = "Hello everyone, um, thank you for joining us today. I'm excited to, uh, share with you our latest findings."
        
        analysis_result = await analyze_transcript(test_transcript)
        
        return {
            "status": "success",
            "test_transcript": test_transcript,
            "analysis_result": analysis_result,
            "ai_services": {
                "nlp_analysis": "working" if analysis_result.get("success") else "failed",
                "whisper_transcription": "available"
            }
        }
        
    except Exception as e:
        logger.error(f"AI functionality test failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "ai_services": {
                "nlp_analysis": "failed",
                "whisper_transcription": "unknown"
            }
        }

if __name__ == "__main__":
    print("🚀 Starting SpeechCoach AI Server...")
    print("📡 Server will be available at: http://localhost:8003")
    print("🔧 AI Services: Whisper + Google ADK")
    uvicorn.run("enhanced_ai_server:app", host="0.0.0.0", port=8003, reload=True)
