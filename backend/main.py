#!/usr/bin/env python3
"""
AI Speech Coach Backend - Main Entry Point
==========================================
Clean, organized backend for AI-powered speech analysis.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the FastAPI application
from api.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AI Speech Coach Backend...")
    print("📊 API Documentation: http://localhost:8080/docs")
    print("🔗 Health Check: http://localhost:8080/")
    print("=" * 50)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_dirs=[str(src_path)]
    )
