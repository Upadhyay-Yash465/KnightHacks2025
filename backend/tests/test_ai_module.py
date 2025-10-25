#!/usr/bin/env python3
"""
Test Script for Public Speaking Coach AI/ML Module

This script demonstrates how to use the AI/ML services for speech analysis.
Run this script to test the integration without needing a full FastAPI server.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.systran_whisper_service import SystranWhisperService
from backend.services.nlp_adk_service import NLPAnalysisService


async def test_speech_analysis_pipeline():
    """
    Test the complete speech analysis pipeline:
    1. Transcribe audio (if available)
    2. Analyze transcript for clarity and filler words
    3. Display results
    """
    print("🎤 Public Speaking Coach AI/ML Module Test")
    print("=" * 50)
    
    # Test transcripts (simulating different speech patterns)
    test_transcripts = [
        {
            "name": "High Filler Usage",
            "text": "So, um, I think that, like, the main point is that, you know, we should probably, uh, consider the options and, like, make a decision, you know?"
        },
        {
            "name": "Good Clarity",
            "text": "The presentation was excellent. We achieved all our goals and exceeded expectations. The team worked hard and delivered outstanding results."
        },
        {
            "name": "Moderate Issues",
            "text": "Well, basically, I mean, it's like, you know, sort of complicated, right? So anyway, um, what do you think we should do about this situation?"
        }
    ]
    
    # Initialize services
    print("\n🔧 Initializing AI/ML Services...")
    
    # Check for Google API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not set. NLP analysis will use fallback suggestions.")
        print("   Set your API key: export GOOGLE_API_KEY=your_key_here")
    
    whisper_service = SystranWhisperService()
    nlp_service = NLPAnalysisService(api_key)
    
    print(f"✅ Whisper Service: {whisper_service.get_model_info()}")
    print(f"✅ NLP Service: API configured = {api_key is not None}")
    
    # Test each transcript
    for i, test_case in enumerate(test_transcripts, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        print(f"Text: {test_case['text']}")
        
        try:
            # Analyze the transcript
            print("\n🔍 Analyzing transcript...")
            analysis_result = await nlp_service.analyze_transcript(test_case['text'])
            
            if analysis_result['success']:
                print(f"\n📊 Analysis Results:")
                print(f"   Filler Count: {analysis_result['filler_count']}")
                print(f"   Clarity Score: {analysis_result['clarity_score']}/10")
                print(f"   Filler Density: {analysis_result['filler_density']}%")
                print(f"   Total Words: {analysis_result['total_words']}")
                print(f"   Summary: {analysis_result['summary']}")
                
                print(f"\n💡 Suggestions:")
                for j, suggestion in enumerate(analysis_result['suggestions'], 1):
                    print(f"   {j}. {suggestion}")
                
                if analysis_result.get('filler_words'):
                    print(f"\n🔍 Filler Words Found:")
                    for filler in analysis_result['filler_words'][:5]:  # Show first 5
                        print(f"   - '{filler['word']}' (position {filler['position']})")
            else:
                print(f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
    
    # Test audio transcription (if sample file exists)
    print(f"\n🎵 Testing Audio Transcription...")
    sample_audio_files = [
        "sample_audio.wav",
        "test_audio.mp3",
        "speech_sample.m4a"
    ]
    
    audio_found = False
    for audio_file in sample_audio_files:
        if Path(audio_file).exists():
            print(f"📁 Found audio file: {audio_file}")
            try:
                print("🔄 Transcribing audio...")
                transcription_result = await whisper_service.transcribe_audio(audio_file)
                
                if transcription_result['success']:
                    print(f"\n📝 Transcription Results:")
                    print(f"   Language: {transcription_result['language']}")
                    print(f"   Duration: {transcription_result['duration']}s")
                    print(f"   Confidence: {transcription_result['confidence']}")
                    print(f"   Transcription Time: {transcription_result['transcription_time']}s")
                    print(f"\n   Transcript:")
                    print(f"   {transcription_result['transcript']}")
                    
                    # Analyze the transcribed text
                    print(f"\n🔍 Analyzing transcribed speech...")
                    analysis_result = await nlp_service.analyze_transcript(transcription_result['transcript'])
                    
                    if analysis_result['success']:
                        print(f"\n📊 Speech Analysis:")
                        print(f"   Clarity Score: {analysis_result['clarity_score']}/10")
                        print(f"   Filler Count: {analysis_result['filler_count']}")
                        print(f"   Summary: {analysis_result['summary']}")
                else:
                    print(f"❌ Transcription failed: {transcription_result.get('error', 'Unknown error')}")
                
                audio_found = True
                break
                
            except Exception as e:
                print(f"❌ Error during audio processing: {str(e)}")
    
    if not audio_found:
        print("ℹ️  No sample audio files found. Place a .wav, .mp3, or .m4a file in the project root to test audio transcription.")
    
    print(f"\n✅ Test completed!")
    print(f"\n🚀 To run the full FastAPI server:")
    print(f"   python main.py")
    print(f"\n📚 To test individual services:")
    print(f"   python backend/services/systran_whisper_service.py")
    print(f"   python backend/services/nlp_adk_service.py")


async def test_api_endpoints():
    """
    Test the API endpoints (requires the FastAPI server to be running).
    """
    print(f"\n🌐 Testing API Endpoints...")
    print("Make sure to run 'python main.py' in another terminal first!")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test text analysis endpoint
        test_text = "So, um, I think that, like, the main point is..."
        response = requests.post(
            "http://localhost:8000/analyze-text",
            json={"text": test_text}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Text analysis endpoint working")
            print(f"   Clarity Score: {result['analysis']['clarity_score']}/10")
            print(f"   Filler Count: {result['analysis']['filler_count']}")
        else:
            print(f"❌ Text analysis failed: {response.status_code}")
            
    except ImportError:
        print("ℹ️  Install 'requests' to test API endpoints: pip install requests")
    except Exception as e:
        print(f"ℹ️  API server not running or not accessible: {str(e)}")


if __name__ == "__main__":
    print("Starting Public Speaking Coach AI/ML Module Test...")
    
    # Run the main test
    asyncio.run(test_speech_analysis_pipeline())
    
    # Optionally test API endpoints
    try:
        asyncio.run(test_api_endpoints())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n⚠️  Additional test failed: {str(e)}")
    
    print("\n🎉 All tests completed!")
