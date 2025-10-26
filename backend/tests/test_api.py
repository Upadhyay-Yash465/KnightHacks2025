#!/usr/bin/env python3
"""
test_api.py
Test script for the AI Speech Coach API
"""

import requests
import os
import tempfile
import wave
import numpy as np

def create_sample_audio():
    """Create a simple test audio file"""
    # Create a simple sine wave audio file
    sample_rate = 44100
    duration = 2  # seconds
    frequency = 440  # A4 note
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
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

def test_api():
    """Test the AI Speech Coach API"""
    print("🧪 Testing AI Speech Coach API")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get("http://localhost:8080/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Start it with: source ../venv/bin/activate && python main.py")
        return
    
    # Test 2: File upload (with sample audio)
    print("\n2. Testing file upload...")
    try:
        # Create sample audio file
        audio_file = create_sample_audio()
        print(f"   Created sample audio: {audio_file}")
        
        # Upload to API
        with open(audio_file, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            response = requests.post("http://localhost:8080/analyze", files=files)
        
        if response.status_code == 200:
            print("✅ File upload successful")
            result = response.json()
            print(f"   Analysis result: {result}")
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
        
        # Clean up
        os.unlink(audio_file)
        
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
    
    print("\n🎉 API testing complete!")

if __name__ == "__main__":
    test_api()
