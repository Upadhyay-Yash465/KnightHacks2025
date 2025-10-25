"""
Simplified FastAPI Main Application for Public Speaking Coach Web App
This version works without Firebase credentials for testing purposes.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import logging
from pathlib import Path
import tempfile
import os
from typing import Optional, Dict, Any
import json

# Import our AI/ML services
from backend.services.systran_whisper_service import transcribe_audio
from backend.services.nlp_adk_service import analyze_transcript

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Public Speaking Coach API",
    description="AI-powered speech analysis and feedback",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer(auto_error=False)

# Mock user data for testing
MOCK_USERS = {
    "test-user-123": {
        "uid": "test-user-123",
        "email": "test@example.com",
        "display_name": "Test User",
        "email_verified": True,
        "disabled": False,
    }
}

async def get_current_user_mock(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Mock authentication for testing purposes"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For testing, accept any token and return mock user
    return MOCK_USERS["test-user-123"]

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Public Speaking Coach API is running!", "status": "healthy"}


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
                    "text": transcription_result["transcript"],
                    "language": transcription_result["language"],
                    "duration": transcription_result["duration"],
                    "confidence": transcription_result["confidence"]
                },
                "analysis": {
                    "filler_count": analysis_result["filler_count"],
                    "clarity_score": analysis_result["clarity_score"],
                    "suggestions": analysis_result["suggestions"],
                    "summary": analysis_result["summary"],
                    "filler_density": analysis_result["filler_density"],
                    "total_words": analysis_result["total_words"]
                },
                "metadata": {
                    "filename": audio_file.filename,
                    "file_size": len(content),
                    "transcription_time": transcription_result["transcription_time"],
                    "model_used": transcription_result["model_used"],
                    "user_id": current_user["uid"],
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            }
            
            logger.info(f"Analysis completed successfully for {audio_file.filename}")
            return JSONResponse(content=result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
                "total_words": analysis_result["total_words"]
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


@app.get("/user/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user_mock)):
    """Get user profile information"""
    return JSONResponse(content=current_user)


@app.get("/user/sessions")
async def get_user_sessions(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """Get user's speech analysis sessions"""
    # Return mock sessions for testing
    mock_sessions = [
        {
            "id": "session-1",
            "type": "audio_analysis",
            "analysis": {
                "clarity_score": 8.5,
                "filler_count": 3,
                "total_words": 150
            },
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "session-2", 
            "type": "text_analysis",
            "analysis": {
                "clarity_score": 7.2,
                "filler_count": 5,
                "total_words": 200
            },
            "created_at": "2024-01-02T00:00:00Z"
        }
    ]
    return JSONResponse(content={"sessions": mock_sessions[:limit]})


@app.get("/user/stats")
async def get_user_stats(current_user: Dict[str, Any] = Depends(get_current_user_mock)):
    """Get user's speech analysis statistics"""
    mock_stats = {
        "total_sessions": 15,
        "average_clarity_score": 7.8,
        "total_filler_words": 45,
        "improvement_trend": 0.5,
    }
    return JSONResponse(content=mock_stats)


@app.post("/user/save-session")
async def save_session(
    session_data: dict,
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """Save a speech analysis session"""
    logger.info(f"Session saved for user {current_user['uid']}")
    return JSONResponse(content={"message": "Session saved successfully"})


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    try:
        # Check if services can be imported
        from backend.services.systran_whisper_service import SystranWhisperService
        from backend.services.nlp_adk_service import NLPAnalysisService
        
        whisper_service = SystranWhisperService()
        nlp_service = NLPAnalysisService()
        
        return {
            "status": "healthy",
            "services": {
                "whisper_service": whisper_service.get_model_info(),
                "nlp_service": {
                    "model_loaded": nlp_service._model_loaded,
                    "api_configured": nlp_service.api_key is not None
                }
            },
            "version": "1.0.0",
            "firebase_status": "mock_mode"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": "1.0.0",
            "firebase_status": "mock_mode"
        }


if __name__ == "__main__":
    import uvicorn
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )

