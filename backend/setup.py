"""
Setup script for Aesop AI Backend
"""
import os
import sys


def setup():
    """Initial setup for backend."""
    print("=" * 60)
    print("Aesop AI Backend Setup")
    print("=" * 60)
    
    # Check for .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("\n⚠️  .env file not found!")
        print("\nPlease create a .env file in the backend/ directory with:")
        print("\nGEMINI_API_KEY=your_api_key_here")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        print("\n" + "=" * 60)
        
        api_key = input("\nEnter your Gemini API key (or press Enter to skip): ").strip()
        
        if api_key:
            with open(env_path, 'w') as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
            print("✅ .env file created!")
        else:
            print("\n⚠️  Skipped. You'll need to create .env manually before running.")
    else:
        print("✅ .env file found!")
    
    # Check for ffmpeg
    print("\nChecking for ffmpeg...")
    result = os.system("ffmpeg -version > /dev/null 2>&1")
    
    if result == 0:
        print("✅ ffmpeg is installed!")
    else:
        print("⚠️  ffmpeg not found!")
        print("\nPlease install ffmpeg:")
        print("  - macOS: brew install ffmpeg")
        print("  - Ubuntu: sudo apt-get install ffmpeg")
        print("  - Windows: Download from https://ffmpeg.org/")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("\nTo start the server, run:")
    print("  python main.py")
    print("=" * 60)


if __name__ == "__main__":
    setup()

