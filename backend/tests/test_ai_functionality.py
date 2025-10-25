#!/usr/bin/env python3
"""
Test script to diagnose AI transcript recognition issues
"""

import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.systran_whisper_service import SystranWhisperService, transcribe_audio
from backend.services.nlp_adk_service import NLPAnalysisService, analyze_transcript

async def test_whisper_service():
    """Test the Whisper transcription service"""
    print("🎤 Testing Whisper Service...")
    
    try:
        # Test with a simple text file (simulating audio)
        test_text = "Hello everyone, thank you for joining us today. I'm excited to share with you our latest findings. Let me start by explaining the key concepts."
        
        # Create a temporary text file to simulate audio input
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_text)
            temp_file_path = temp_file.name
        
        print(f"📝 Created test file: {temp_file_path}")
        
        # Test transcription (this will fail for text files, but we can see the error)
        try:
            result = await transcribe_audio(temp_file_path)
            print(f"✅ Transcription result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Transcription failed (expected for text file): {str(e)}")
        
        # Clean up
        os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"❌ Whisper service test failed: {str(e)}")

async def test_nlp_service():
    """Test the NLP analysis service"""
    print("\n🧠 Testing NLP Analysis Service...")
    
    try:
        # Test transcript analysis
        test_transcript = "Hello everyone, um, thank you for joining us today. I'm excited to, uh, share with you our latest findings. So, let me start by, uh, explaining the key concepts."
        
        print(f"📝 Testing with transcript: '{test_transcript}'")
        
        # Test NLP analysis
        result = await analyze_transcript(test_transcript)
        print(f"✅ NLP Analysis result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"📊 Clarity Score: {result.get('clarity_score', 'N/A')}")
            print(f"🗣️ Filler Count: {result.get('filler_count', 'N/A')}")
            print(f"💡 Suggestions: {len(result.get('suggestions', []))} suggestions")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ NLP service test failed: {str(e)}")

async def test_model_loading():
    """Test model loading capabilities"""
    print("\n🔄 Testing Model Loading...")
    
    try:
        # Test Whisper model loading
        whisper_service = SystranWhisperService()
        print(f"📋 Whisper model info: {whisper_service.get_model_info()}")
        
        # Test NLP model loading
        nlp_service = NLPAnalysisService()
        print(f"📋 NLP service initialized: {nlp_service is not None}")
        
    except Exception as e:
        print(f"❌ Model loading test failed: {str(e)}")

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import requests
        
        # Test basic endpoint
        response = requests.get("http://localhost:8003/")
        if response.status_code == 200:
            print(f"✅ Basic endpoint working: {response.json()}")
        else:
            print(f"❌ Basic endpoint failed: {response.status_code}")
            
        # Test text analysis endpoint
        test_data = {
            "text": "Hello everyone, um, thank you for joining us today. I'm excited to, uh, share with you our latest findings."
        }
        
        response = requests.post(
            "http://localhost:8003/analyze-text",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Text analysis endpoint working: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Text analysis endpoint failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 Starting AI Functionality Tests...")
    print("=" * 50)
    
    await test_model_loading()
    await test_nlp_service()
    await test_whisper_service()
    await test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
