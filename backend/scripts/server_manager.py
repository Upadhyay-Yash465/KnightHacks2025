#!/usr/bin/env python3
"""
server_manager.py
Simple script to manage the AI Speech Coach server
"""

import subprocess
import sys
import signal
import os
import time

def kill_existing_servers():
    """Kill any existing servers on port 8080"""
    try:
        result = subprocess.run(['lsof', '-ti:8080'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔪 Killing existing processes on port 8080: {pids}")
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already dead
            time.sleep(1)
            print("✅ Existing servers killed")
        else:
            print("✅ No existing servers found")
    except Exception as e:
        print(f"⚠️ Error checking existing servers: {e}")

def start_server():
    """Start the AI Speech Coach server"""
    print("🚀 Starting AI Speech Coach server...")
    
    # Kill existing servers first
    kill_existing_servers()
    
    # Start the server with virtual environment
    try:
        subprocess.run([
            "bash", "-c", "source ../venv/bin/activate && python main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def check_server():
    """Check if server is running"""
    try:
        result = subprocess.run(['lsof', '-ti:8080'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"✅ Server is running on port 8080 (PIDs: {pids})")
            return True
        else:
            print("❌ No server running on port 8080")
            return False
    except Exception as e:
        print(f"⚠️ Error checking server: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🎤 AI Speech Coach Server Manager")
        print("=" * 40)
        print("Usage:")
        print("  python server_manager.py start    - Start the server")
        print("  python server_manager.py stop     - Stop the server")
        print("  python server_manager.py restart  - Restart the server")
        print("  python server_manager.py status   - Check server status")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_server()
    elif command == "stop":
        kill_existing_servers()
    elif command == "restart":
        kill_existing_servers()
        time.sleep(1)
        start_server()
    elif command == "status":
        check_server()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: start, stop, restart, status")

if __name__ == "__main__":
    main()
