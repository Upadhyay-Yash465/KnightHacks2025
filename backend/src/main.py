"""
FastAPI backend for Public Speaking Coach.
Main entry point for the application.
"""

import os
import uuid
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiofiles

from services.systran_whisper_service import transcribe_audio
from agent.main_agent import run_agent
from utils.firebase_utils import save_to_firestore, upload_to_storage, get_analysis_history


# Initialize FastAPI app
app = FastAPI(
    title="Public Speaking Coach API",
    description="Backend API for speech analysis and coaching",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AnalysisRequest(BaseModel):
    """Request model for direct analysis."""
    transcript: str
    user_id: Optional[str] = "default"


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    transcript: str
    filler_count: int
    clarity_score: float
    suggestions: list
    summary: str
    firestore_id: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Public Speaking Coach API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "analyze": "/analyze",
            "analyze-text": "/analyze-text",
            "history": "/history/{user_id}"
        }
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload audio file to Firebase Storage.
    
    Args:
        file: Audio file to upload
        
    Returns:
        Upload information including Firebase URL
    """
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file locally
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Upload to Firebase Storage
        firebase_url = upload_to_storage(file_path, unique_filename)
        
        # Clean up local file
        os.remove(file_path)
        
        return {
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "firebase_url": firebase_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...), user_id: str = "default"):
    """
    Analyze audio file: transcribe + NLP analysis + save to Firestore.
    
    Full workflow:
    1. Save uploaded file locally
    2. Transcribe with SYSTRAN Faster-Whisper
    3. Analyze with Google ADK via AMD Agent
    4. Save results to Firestore
    5. Return combined results
    
    Args:
        file: Audio file to analyze
        user_id: User identifier for saving results
        
    Returns:
        Combined analysis results
    """
    try:
        # Save uploaded file locally
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Step 1: Transcribe audio
        transcription_result = await transcribe_audio(file_path)
        transcript = transcription_result["transcript"]
        
        if not transcript:
            raise HTTPException(status_code=400, detail="No transcript generated from audio")
        
        # Step 2: Run ADK NLP analysis via AMD Agent
        analysis_result = await run_agent(transcript, tool_name="adk_nlp_analysis")
        
        # Step 3: Save to Firestore
        firestore_id = save_to_firestore(transcript, analysis_result, user_id)
        
        # Step 4: Upload audio to Firebase Storage
        firebase_url = upload_to_storage(file_path, unique_filename)
        
        # Clean up local file
        os.remove(file_path)
        
        # Return combined results
        return AnalysisResponse(
            transcript=transcript,
            filler_count=analysis_result["filler_count"],
            clarity_score=analysis_result["clarity_score"],
            suggestions=analysis_result["suggestions"],
            summary=analysis_result["summary"],
            firestore_id=firestore_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    """
    Analyze text directly without audio upload.
    
    Args:
        request: Analysis request with transcript
        
    Returns:
        Analysis results
    """
    try:
        # Run ADK NLP analysis via AMD Agent
        analysis_result = await run_agent(request.transcript, tool_name="adk_nlp_analysis")
        
        # Save to Firestore
        firestore_id = save_to_firestore(request.transcript, analysis_result, request.user_id)
        
        return AnalysisResponse(
            transcript=request.transcript,
            filler_count=analysis_result["filler_count"],
            clarity_score=analysis_result["clarity_score"],
            suggestions=analysis_result["suggestions"],
            summary=analysis_result["summary"],
            firestore_id=firestore_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 10):
    """
    Get analysis history for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of records to retrieve
        
    Returns:
        List of historical analysis records
    """
    try:
        history = get_analysis_history(user_id, limit)
        return {
            "user_id": user_id,
            "count": len(history),
            "records": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Public Speaking Coach API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

