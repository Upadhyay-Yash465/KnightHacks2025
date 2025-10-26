#!/usr/bin/env python3
"""
quick_start.py
Quick start guide and server management for AI Speech Coach
"""

import subprocess
import sys
import os

def show_help():
    """Show help information"""
    print("🎤 AI Speech Coach - Quick Start Guide")
    print("=" * 50)
    print()
    print("📋 Available Commands:")
    print("  python quick_start.py start     - Start the server")
    print("  python quick_start.py stop      - Stop the server")
    print("  python quick_start.py restart   - Restart the server")
    print("  python quick_start.py status    - Check server status")
    print("  python quick_start.py test      - Test with sample audio")
    print("  python quick_start.py help      - Show this help")
    print()
    print("🔧 Manual Commands:")
    print("  # Start server manually")
    print("  source ../venv/bin/activate && python main.py")
    print()
    print("  # Test API")
    print("  curl http://localhost:8080/")
    print()
    print("  # Upload audio file")
    print("  curl -X POST 'http://localhost:8080/analyze' -F 'audio=@your_file.wav'")
    print()
    print("📁 File Testing:")
    print("  python test_with_file.py your_audio.wav")
    print("  python test_api.py")
    print()
    print("🚨 Troubleshooting:")
    print("  # If 'Address already in use' error:")
    print("  python server_manager.py stop")
    print("  python server_manager.py start")
    print()
    print("  # If virtual environment issues:")
    print("  cd .. && source venv/bin/activate && cd ai-speech-coach")

def start_server():
    """Start the server"""
    print("🚀 Starting AI Speech Coach server...")
    try:
        subprocess.run([sys.executable, 'server_manager.py', 'start'], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start server")
        print("   Try manually: source ../venv/bin/activate && python main.py")

def stop_server():
    """Stop the server"""
    print("🛑 Stopping AI Speech Coach server...")
    try:
        subprocess.run([sys.executable, 'server_manager.py', 'stop'], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to stop server")

def restart_server():
    """Restart the server"""
    print("🔄 Restarting AI Speech Coach server...")
    try:
        subprocess.run([sys.executable, 'server_manager.py', 'restart'], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to restart server")

def check_status():
    """Check server status"""
    print("📊 Checking server status...")
    try:
        subprocess.run([sys.executable, 'server_manager.py', 'status'], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to check status")

def run_test():
    """Run API test"""
    print("🧪 Running API test...")
    try:
        subprocess.run([sys.executable, 'test_api.py'], check=True)
    except subprocess.CalledProcessError:
        print("❌ Test failed")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_server()
    elif command == "stop":
        stop_server()
    elif command == "restart":
        restart_server()
    elif command == "status":
        check_status()
    elif command == "test":
        run_test()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
