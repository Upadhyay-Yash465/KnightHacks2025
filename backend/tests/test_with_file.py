#!/usr/bin/env python3
"""
test_with_file.py
Test the API with a real audio file
"""

import requests
import os
import sys

def test_with_file(audio_file_path):
    """Test the API with a real audio file"""
    if not os.path.exists(audio_file_path):
        print(f"❌ File not found: {audio_file_path}")
        return False
    
    print(f"🎤 Testing with audio file: {audio_file_path}")
    print("=" * 50)
    
    try:
        # Upload file to API
        with open(audio_file_path, 'rb') as f:
            files = {'audio': (os.path.basename(audio_file_path), f, 'audio/wav')}
            response = requests.post('http://localhost:8080/analyze', files=files)
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            result = response.json()
            
            # Display key results
            print(f"\n📊 Analysis Results:")
            print(f"   Duration: {result['voice']['metrics']['duration_sec']}s")
            print(f"   Speech Rate: {result['voice']['metrics']['speech_rate_wpm']} WPM")
            print(f"   Average Pitch: {result['voice']['metrics']['avg_pitch_hz']} Hz")
            print(f"   Filler Words: {result['voice']['filler_words']}")
            
            if 'context' in result and 'clarity_score' in result['context']:
                print(f"   Clarity Score: {result['context']['clarity_score']}/10")
            
            print(f"\n💬 Summary:")
            print(f"   {result['summary']}")
            
            print(f"\n⏱️ Processing Time: {result['execution_time_sec']}s")
            
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("   Make sure the server is running: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("🎤 AI Speech Coach - File Tester")
        print("=" * 40)
        print("Usage: python test_with_file.py <audio_file_path>")
        print("\nExample:")
        print("  python test_with_file.py speech.wav")
        print("  python test_with_file.py /path/to/audio.mp3")
        return
    
    audio_file = sys.argv[1]
    test_with_file(audio_file)

if __name__ == "__main__":
    main()
