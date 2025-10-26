#!/usr/bin/env python3
"""
test_gemini_integration.py
Test the Gemini-powered speech analysis
"""

import os
import sys
import tempfile
import numpy as np
import wave
import requests

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def test_gemini_agent_directly():
    """Test the Gemini voice agent directly"""
    print("🧪 Testing Gemini Voice Agent Directly")
    print("=" * 50)
    
    try:
        from agents.gemini_voice_agent import GeminiVoiceAgent
        
        # Create test audio
        audio_file = create_test_speech_audio()
        print(f"📁 Created test audio: {audio_file}")
        
        # Test the agent
        print("\n🎤 Testing GeminiVoiceAgent...")
        agent = GeminiVoiceAgent()
        
        print("📊 Running analysis...")
        result = agent.analyze(audio_file)
        
        print("\n📋 Gemini Analysis Results:")
        print(f"   Transcript: '{result.get('transcript', 'N/A')}'")
        print(f"   Clarity: {result.get('clarity', 'N/A')}")
        print(f"   Filler Words: {result.get('filler_words', 'N/A')}")
        print(f"   Feedback: {result.get('feedback', 'N/A')}")
        
        # Show detailed analysis
        detailed = result.get('detailed_analysis', {})
        if detailed:
            print(f"\n🔍 Detailed Analysis:")
            print(f"   Speech Clarity: {detailed.get('speech_clarity', 'N/A')}")
            print(f"   Pace Analysis: {detailed.get('pace_analysis', 'N/A')}")
            print(f"   Pitch Analysis: {detailed.get('pitch_analysis', 'N/A')}")
            print(f"   Fluency Score: {detailed.get('fluency_score', 'N/A')}")
            print(f"   Confidence Score: {detailed.get('confidence_score', 'N/A')}")
            print(f"   Improvement Areas: {detailed.get('improvement_areas', [])}")
            print(f"   Strengths: {detailed.get('strengths', [])}")
            print(f"   Recommendations: {detailed.get('recommendations', [])}")
        
        # Check if we got meaningful feedback
        if "N/A" not in str(result.get('clarity', '')) and result.get('clarity', '') != 'N/A - No speech detected':
            print("\n✅ SUCCESS: Gemini is providing real analysis!")
        else:
            print("\n⚠️ Gemini analysis may need real speech audio")
            
    except Exception as e:
        print(f"\n❌ Error testing Gemini agent: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'audio_file' in locals():
            os.unlink(audio_file)

def test_api_with_gemini():
    """Test the API with Gemini integration"""
    print("\n🌐 Testing API with Gemini Integration")
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
            
            # Show results
            voice = result.get('voice', {})
            transcript = voice.get('transcript', '')
            clarity = voice.get('clarity', 'N/A')
            feedback = voice.get('feedback', 'N/A')
            
            print(f"\n📋 API Results with Gemini:")
            print(f"   Transcript: '{transcript}'")
            print(f"   Clarity: {clarity}")
            print(f"   Feedback: {feedback}")
            
            # Check if we're getting real Gemini feedback
            if clarity != "N/A" and "N/A - No speech detected" not in clarity:
                print("\n🎉 SUCCESS: API is using Gemini for real analysis!")
            else:
                print("\n⚠️ API may still be using fallback analysis")
                
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    finally:
        os.unlink(audio_file)

def show_gemini_benefits():
    """Show the benefits of Gemini integration"""
    print("\n🚀 GEMINI INTEGRATION BENEFITS")
    print("=" * 50)
    print("✅ Real AI-powered speech analysis")
    print("✅ Comprehensive feedback on:")
    print("   - Speech clarity and fluency")
    print("   - Speaking pace and rhythm")
    print("   - Vocal pitch and tone")
    print("   - Volume and projection")
    print("   - Confidence assessment")
    print("   - Specific improvement areas")
    print("   - Personalized recommendations")
    print("\n🎯 For BEST RESULTS:")
    print("1. Record yourself speaking clearly")
    print("2. Say: 'Hello, this is a test of my speech analysis skills'")
    print("3. Upload through http://localhost:3000")
    print("4. Get comprehensive Gemini-powered feedback!")

if __name__ == "__main__":
    test_gemini_agent_directly()
    test_api_with_gemini()
    show_gemini_benefits()
