#!/usr/bin/env python3
"""
Demo script for SpeechCoach AI Frontend
This script creates sample data and demonstrates the frontend features
"""

import json
import os
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample session data for demonstration"""
    
    # Sample analysis results
    sample_results = {
        "transcription": {
            "text": "So, um, I think that, like, the main point is that, you know, we should probably, uh, consider the options. Well, basically, I mean, it's like, you know, sort of complicated, right? So anyway, um, what do you think?",
            "language": "en",
            "duration": 15.5,
            "confidence": 0.89
        },
        "analysis": {
            "filler_count": 8,
            "clarity_score": 6.5,
            "suggestions": [
                "Practice pausing instead of using filler words like 'um' and 'uh'",
                "Slow down your speech pace for better clarity",
                "Record yourself speaking to identify filler word patterns"
            ],
            "summary": "Moderate clarity with several filler words that can be reduced.",
            "filler_density": 12.5,
            "total_words": 64
        },
        "metadata": {
            "filename": "sample_speech.wav",
            "file_size": 248576,
            "transcription_time": 2.3,
            "model_used": "systran/faster-whisper-base"
        }
    }
    
    # Create sample sessions for progress tracking
    sessions = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(10):
        session_date = base_date + timedelta(days=i*3)
        clarity_score = 5.0 + (i * 0.4) + (0.1 if i % 2 == 0 else -0.1)
        filler_count = max(1, 15 - i)
        
        session = {
            "timestamp": session_date.isoformat(),
            "clarityScore": round(clarity_score, 1),
            "fillerCount": filler_count,
            "wordCount": 50 + (i * 5)
        }
        sessions.append(session)
    
    return sample_results, sessions

def create_demo_files():
    """Create demo files for testing"""
    
    # Create sample data
    sample_results, sessions = create_sample_data()
    
    # Save sample data to localStorage format
    demo_data = {
        "sample_results": sample_results,
        "sessions": sessions,
        "created_at": datetime.now().isoformat()
    }
    
    # Write to a demo file
    with open('demo_data.json', 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print("✅ Demo data created successfully!")
    print(f"📊 Sample sessions: {len(sessions)}")
    print(f"🎯 Latest clarity score: {sessions[-1]['clarityScore']}/10")
    print(f"📈 Filler count trend: {sessions[0]['fillerCount']} → {sessions[-1]['fillerCount']}")
    
    return demo_data

def print_usage_instructions():
    """Print usage instructions"""
    
    print("\n" + "="*60)
    print("🎤 SpeechCoach AI Frontend Demo")
    print("="*60)
    print("\n📋 To test the frontend:")
    print("1. Start the backend server:")
    print("   cd /Users/yug/Desktop/HACKATHON2\\ copy")
    print("   python main.py")
    print("\n2. Start the frontend server:")
    print("   cd frontend")
    print("   python serve.py")
    print("\n3. Open your browser to: http://localhost:3000")
    print("\n🎯 Features to test:")
    print("• Upload an audio file (drag & drop or browse)")
    print("• Record live audio (click microphone button)")
    print("• Analyze text directly (paste transcript)")
    print("• View interactive charts and metrics")
    print("• Check progress tracking")
    print("• Try keyboard shortcuts (Space, Ctrl+Enter, Escape)")
    print("\n⌨️  Keyboard Shortcuts:")
    print("• Space: Start/stop recording")
    print("• Ctrl+Enter: Analyze text")
    print("• Escape: Stop recording")
    print("\n📱 The frontend is fully responsive!")
    print("Try it on different screen sizes.")

if __name__ == "__main__":
    print("🚀 Creating SpeechCoach AI Frontend Demo...")
    
    # Create demo data
    demo_data = create_demo_files()
    
    # Print instructions
    print_usage_instructions()
    
    print("\n✨ Demo setup complete! Happy testing!")

