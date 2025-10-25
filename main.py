from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from agent.orchestrator_agent import run_orchestrator
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Aesop.AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze (POST) - Upload video/audio for analysis",
            "docs": "/docs - API documentation",
            "health": "/health - Health check"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Aesop.AI Backend"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Analyze uploaded video/audio file using the Orchestrator Agent
    
    The Orchestrator Agent coordinates:
    - Context analysis (Gemini)
    - Voice analysis (Transcriber, Pitch/Pace/Volume with Librosa, Cross-checker)
    - Video analysis (Facial-emotion with Cloud Vision, Hand-gesture with MediaPipe)
    - Generates TTS Summary
    """
    try:
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Use Orchestrator Agent for comprehensive analysis
        results = run_orchestrator(audio_path=file_path, video_path=file_path)

        return {
            "transcript": results.get("context", {}).get("transcript", ""),
            "feedback": {
                "voice": results.get("voice", {}),
                "transcript": results.get("context", {}),
                "body": results.get("video", {}),
                "summary": results.get("summary", {})
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to analyze file"
        }
