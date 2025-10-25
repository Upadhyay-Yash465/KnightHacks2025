#!/usr/bin/env python3
"""
Setup Script for Public Speaking Coach AI/ML Module

This script helps configure the environment and test the AI/ML services.
"""

import os
import sys
import asyncio
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'faster_whisper',
        'google.generativeai', 
        'fastapi',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_api_key():
    """Check if Google API key is configured."""
    print("\n🔑 Checking API configuration...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"✅ Google API key is set (length: {len(api_key)})")
        return True
    else:
        print("⚠️  Google API key not found")
        print("\n📝 To set up Google API key:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Set environment variable:")
        print("   export GOOGLE_API_KEY=your_api_key_here")
        print("3. Or create a .env file with:")
        print("   GOOGLE_API_KEY=your_api_key_here")
        return False

async def test_services():
    """Test the AI/ML services."""
    print("\n🧪 Testing AI/ML services...")
    
    try:
        # Test NLP service
        from backend.services.nlp_adk_service import NLPAnalysisService
        
        nlp_service = NLPAnalysisService()
        test_text = "So, um, I think that, like, the main point is that we should probably consider the options."
        
        print("📝 Testing NLP Analysis...")
        result = await nlp_service.analyze_transcript(test_text)
        
        print(f"✅ NLP Analysis Results:")
        print(f"   Filler Count: {result['filler_count']}")
        print(f"   Clarity Score: {result['clarity_score']}/10")
        print(f"   Suggestions: {len(result['suggestions'])} suggestions generated")
        
        # Test Whisper service
        from backend.services.systran_whisper_service import SystranWhisperService
        
        whisper_service = SystranWhisperService()
        print(f"✅ Whisper Service: {whisper_service.get_model_info()}")
        
        print("🎉 All services are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        return False

def show_usage():
    """Show usage instructions."""
    print("\n🚀 Usage Instructions:")
    print("1. Start the FastAPI server:")
    print("   python3 main.py")
    print("\n2. Test the API endpoints:")
    print("   curl http://localhost:8002/")
    print("   curl http://localhost:8002/health")
    print("\n3. Analyze text:")
    print('   curl -X POST "http://localhost:8002/analyze-text" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"text": "Your speech transcript here"}\'')
    print("\n4. View API documentation:")
    print("   http://localhost:8002/docs")

async def main():
    """Main setup function."""
    print("🎤 Public Speaking Coach AI/ML Module Setup")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check API key
    api_ok = check_api_key()
    
    # Test services
    services_ok = await test_services()
    
    # Show results
    print("\n📊 Setup Summary:")
    print(f"   Dependencies: {'✅ OK' if deps_ok else '❌ Missing'}")
    print(f"   API Key: {'✅ OK' if api_ok else '⚠️  Not set'}")
    print(f"   Services: {'✅ OK' if services_ok else '❌ Failed'}")
    
    if deps_ok and services_ok:
        print("\n🎉 Setup completed successfully!")
        show_usage()
    else:
        print("\n⚠️  Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
