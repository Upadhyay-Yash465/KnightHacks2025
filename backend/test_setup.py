"""
Quick test to verify backend setup is working.
"""
import os
import sys


def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    
    tests = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("faster_whisper", "faster-whisper"),
        ("librosa", "librosa"),
        ("cv2", "opencv-python"),
        ("google.generativeai", "google-generativeai"),
        ("dotenv", "python-dotenv"),
    ]
    
    failed = []
    
    for module, package in tests:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed.append(package)
    
    if failed:
        print(f"\n⚠️  Missing packages: {', '.join(failed)}")
        print("Run: pip install -r ../requirements.txt")
        return False
    
    print("\n✅ All packages installed!")
    return True


def test_env():
    """Test that .env file exists and has API key."""
    print("\nTesting environment...")
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("⚠️  .env file not found")
        print("Run: python setup.py")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  GEMINI_API_KEY not set in .env")
        return False
    
    print(f"✅ GEMINI_API_KEY configured ({api_key[:10]}...)")
    return True


def test_ffmpeg():
    """Test that ffmpeg is installed."""
    print("\nTesting ffmpeg...")
    
    result = os.system("ffmpeg -version > /dev/null 2>&1")
    
    if result == 0:
        print("✅ ffmpeg installed")
        return True
    else:
        print("⚠️  ffmpeg not found")
        print("Install:")
        print("  - macOS: brew install ffmpeg")
        print("  - Ubuntu: sudo apt-get install ffmpeg")
        return False


def main():
    print("=" * 60)
    print("Aesop AI Backend - Setup Test")
    print("=" * 60 + "\n")
    
    results = [
        test_imports(),
        test_env(),
        test_ffmpeg(),
    ]
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("✅ All tests passed! You're ready to run the server.")
        print("\nStart server with: python main.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

