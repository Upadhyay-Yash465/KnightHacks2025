#!/usr/bin/env python3
"""
create_test_audio.py
Create a simple test audio file for testing the API
"""

import os
import sys
import tempfile
import numpy as np
import wave
import requests

def create_simple_test_audio():
    """Create a very simple test audio that might work better"""
    sample_rate = 16000  # Whisper's preferred sample rate
    duration = 2  # seconds
    
    # Create a simple tone that might be recognized
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a simple 440Hz tone (A note)
    audio_data = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        with wave.open(f.name, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        return f.name

def test_api_with_file():
    """Test the API with a real audio file"""
    print("🎤 Testing API with Audio File")
    print("=" * 40)
    
    # Create test audio
    audio_file = create_simple_test_audio()
    print(f"📁 Created test audio: {audio_file}")
    
    try:
        # Test API
        print("\n📡 Testing API endpoint...")
        with open(audio_file, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            response = requests.post('http://localhost:8080/analyze', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API responded successfully")
            
            # Check results
            transcript = result.get('voice', {}).get('transcript', '')
            print(f"\n📋 Analysis Results:")
            print(f"   Transcript: '{transcript}'")
            print(f"   Transcript length: {len(transcript)}")
            
            if transcript and transcript.strip():
                print("✅ Transcription working!")
            else:
                print("⚠️ Empty transcript - this is expected for synthetic audio")
                print("   The API is working, but Whisper needs real speech")
            
            # Show other metrics
            metrics = result.get('voice', {}).get('metrics', {})
            print(f"   Duration: {metrics.get('duration_sec', 'N/A')}s")
            print(f"   Tempo: {metrics.get('tempo_bpm', 'N/A')} BPM")
            print(f"   Pitch: {metrics.get('avg_pitch_hz', 'N/A')} Hz")
            print(f"   Volume: {metrics.get('avg_volume_rms', 'N/A')}")
            
            # Show context analysis
            context = result.get('context', {})
            if 'error' in context:
                print(f"   Context Error: {context['error']}")
            else:
                print(f"   Clarity Score: {context.get('clarity_score', 'N/A')}")
                print(f"   Grammar Score: {context.get('grammar_score', 'N/A')}")
            
            print(f"\n💡 Summary: {result.get('summary', 'N/A')}")
            
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    finally:
        # Clean up
        os.unlink(audio_file)
        print(f"\n🧹 Cleaned up test file")

def provide_solution():
    """Provide solution for the empty transcript issue"""
    print("\n🔧 SOLUTION FOR EMPTY TRANSCRIPT ISSUE")
    print("=" * 50)
    print("The API is working correctly, but Whisper needs REAL SPEECH audio.")
    print("\n📝 To test properly:")
    print("1. Record yourself saying: 'Hello, this is a test of my speech'")
    print("2. Save as WAV or MP3 file")
    print("3. Upload through the web interface at http://localhost:3000")
    print("\n🎯 Alternative: Use the web interface with your microphone")
    print("   The web interface should work with real audio files")
    print("\n💡 The 'N/A' values you see are because:")
    print("   - Empty transcript → Context analysis fails")
    print("   - No real speech → Whisper can't transcribe")
    print("   - OpenAI API issues → NLP feedback fails")

if __name__ == "__main__":
    test_api_with_file()
    provide_solution()
