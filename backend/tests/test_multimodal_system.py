#!/usr/bin/env python3
"""
test_multimodal_system.py
Test the complete multimodal analysis system
"""

import requests
import os
import tempfile
import numpy as np
import wave
import json

def create_test_speech_audio():
    """Create a more realistic speech-like audio for testing"""
    sample_rate = 16000
    duration = 3  # seconds
    
    # Create a more complex waveform that might be recognized as speech
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create speech-like formants (vowel sounds)
    f1, f2, f3 = 800, 1200, 2500  # Formant frequencies for "ah" sound
    
    audio_data = (
        0.4 * np.sin(2 * np.pi * f1 * t) +
        0.3 * np.sin(2 * np.pi * f2 * t) +
        0.2 * np.sin(2 * np.pi * f3 * t)
    )
    
    # Add some modulation to make it more speech-like
    modulation = 0.7 + 0.3 * np.sin(2 * np.pi * 3 * t)  # 3 Hz modulation
    audio_data *= modulation
    
    # Add some noise
    noise = 0.05 * np.random.normal(0, 1, len(t))
    audio_data += noise
    
    # Normalize
    audio_data = audio_data / np.max(np.abs(audio_data))
    
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

def test_multimodal_api():
    """Test the multimodal API structure"""
    print("🧪 Testing Multimodal Analysis System")
    print("=" * 50)
    
    # Create test audio
    audio_file = create_test_speech_audio()
    print(f"📁 Created test audio: {audio_file}")
    
    try:
        # Test API
        with open(audio_file, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            response = requests.post('http://localhost:8080/analyze', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API responded successfully")
            
            # Check if we have the new multimodal structure
            print(f"\n📋 Checking Multimodal Structure:")
            
            # Check for new structure
            has_text_analysis = 'text_analysis' in result
            has_audio_analysis = 'audio_analysis' in result
            has_visual_analysis = 'visual_analysis' in result
            has_summary = 'summary' in result
            
            print(f"   Text Analysis: {'✅' if has_text_analysis else '❌'}")
            print(f"   Audio Analysis: {'✅' if has_audio_analysis else '❌'}")
            print(f"   Visual Analysis: {'✅' if has_visual_analysis else '❌'}")
            print(f"   Summary: {'✅' if has_summary else '❌'}")
            
            if has_text_analysis and has_audio_analysis and has_visual_analysis and has_summary:
                print("\n🎉 SUCCESS: New multimodal structure is working!")
                
                # Show sample data
                print(f"\n📊 Sample Analysis Results:")
                
                # Text Analysis
                text = result.get('text_analysis', {})
                print(f"   📝 Text Analysis:")
                print(f"      Transcript: '{text.get('transcript', 'N/A')[:50]}...'")
                print(f"      Clarity Score: {text.get('clarity_score', 'N/A')}")
                print(f"      Grammar Score: {text.get('grammar_score', 'N/A')}")
                print(f"      Filler Words: {text.get('filler_words', 'N/A')}")
                
                # Audio Analysis
                audio = result.get('audio_analysis', {})
                print(f"   🎵 Audio Analysis:")
                print(f"      Prosody: {audio.get('prosody', {}).get('score', 'N/A')}")
                print(f"      Tone: {audio.get('tone', {}).get('score', 'N/A')}")
                print(f"      Pitch: {audio.get('pitch', {}).get('score', 'N/A')}")
                print(f"      Pace: {audio.get('pace', {}).get('score', 'N/A')}")
                print(f"      Volume: {audio.get('volume', {}).get('score', 'N/A')}")
                
                # Visual Analysis
                visual = result.get('visual_analysis', {})
                print(f"   👁️ Visual Analysis:")
                print(f"      Facial Landmarks: {visual.get('facial_landmarks', {}).get('detected', 'N/A')}")
                print(f"      Gestures: {visual.get('gestures', {}).get('detected', 'N/A')}")
                print(f"      Eye Contact: {visual.get('eye_contact', {}).get('percentage', 'N/A')}%")
                print(f"      Confidence: {visual.get('confidence', {}).get('score', 'N/A')}")
                
                # Summary
                summary = result.get('summary', {})
                print(f"   📊 Summary:")
                print(f"      Overall Score: {summary.get('overall_score', 'N/A')}")
                print(f"      Text Score: {summary.get('text_score', 'N/A')}")
                print(f"      Audio Score: {summary.get('audio_score', 'N/A')}")
                print(f"      Visual Score: {summary.get('visual_score', 'N/A')}")
                
                recommendations = summary.get('recommendations', [])
                if recommendations:
                    print(f"      Recommendations: {recommendations[:2]}...")
                
                strengths = summary.get('strengths', [])
                if strengths:
                    print(f"      Strengths: {strengths[:2]}...")
                
            else:
                print("\n⚠️ API is still using old structure")
                print("   This means the multimodal orchestrator isn't being used")
                
                # Show old structure
                print(f"\n📋 Old Structure Detected:")
                print(f"   Voice: {'✅' if 'voice' in result else '❌'}")
                print(f"   Context: {'✅' if 'context' in result else '❌'}")
                print(f"   Video: {'✅' if 'video' in result else '❌'}")
                
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    finally:
        os.unlink(audio_file)

def show_expected_structure():
    """Show the expected multimodal structure"""
    print("\n📋 EXPECTED MULTIMODAL STRUCTURE")
    print("=" * 50)
    print("The API should return:")
    print("""
{
  "text_analysis": {
    "transcript": "Hello, this is a test...",
    "clarity_score": 8.5,
    "grammar_score": 9.0,
    "structure_score": 7.5,
    "filler_words": 2,
    "word_count": 15
  },
  "audio_analysis": {
    "prosody": {"score": 8.0, "analysis": "Good rhythm"},
    "tone": {"score": 7.5, "analysis": "Clear tone"},
    "pitch": {"score": 8.5, "analysis": "Good pitch range"},
    "pace": {"score": 7.0, "analysis": "Normal pace"},
    "volume": {"score": 8.0, "analysis": "Good volume"}
  },
  "visual_analysis": {
    "facial_landmarks": {"detected": true, "analysis": "Emotion: Happy"},
    "gestures": {"detected": true, "analysis": "Moderate gestures"},
    "eye_contact": {"percentage": 75, "analysis": "Good eye contact"},
    "confidence": {"score": 8.5, "analysis": "Confident delivery"}
  },
  "summary": {
    "overall_score": 8.2,
    "text_score": 8.3,
    "audio_score": 7.8,
    "visual_score": 8.5,
    "recommendations": ["Practice more", "Reduce filler words"],
    "strengths": ["Clear speech", "Good confidence"]
  }
}
""")

if __name__ == "__main__":
    test_multimodal_api()
    show_expected_structure()
