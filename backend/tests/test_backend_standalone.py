#!/usr/bin/env python3
"""
Backend Standalone Test Script
=============================
This script tests the core backend functionality after frontend removal.
It verifies:
1. All imports work correctly
2. FastAPI app starts successfully
3. API endpoints respond correctly
4. Core analysis functionality works
5. Error handling works properly
"""

import os
import sys
import asyncio
import tempfile
import requests
import subprocess
import time
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def create_test_audio():
    """Create a simple test audio file"""
    try:
        import numpy as np
        import soundfile as sf
        
        # Create a simple sine wave audio
        sample_rate = 16000
        duration = 2  # seconds
        frequency = 440  # Hz (A note)
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        sf.write(temp_file.name, audio_data, sample_rate)
        temp_file.close()
        
        return temp_file.name
    except ImportError:
        print("   ⚠️  numpy/soundfile not available, skipping audio creation")
        return None
    except Exception as e:
        print(f"   ⚠️  Error creating test audio: {e}")
        return None

def test_imports():
    """Test that all required modules can be imported"""
    print_header("TESTING IMPORTS")
    
    tests = [
        ("FastAPI", "from fastapi import FastAPI"),
        ("Main Module", "import main"),
        ("Config", "from config import config"),
        ("Multimodal Orchestrator", "from agents.multimodal_orchestrator import MultimodalOrchestrator"),
        ("Context Agent", "from agents.context_agent import ContextAgent"),
        ("Gemini Voice Agent", "from agents.gemini_voice_agent import GeminiVoiceAgent"),
        ("Video Agent", "from agents.video_agent import VideoAgent"),
    ]
    
    all_passed = True
    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print_test_result(test_name, True)
        except Exception as e:
            print_test_result(test_name, False, str(e))
            all_passed = False
    
    return all_passed

def test_fastapi_app():
    """Test FastAPI app creation and routes"""
    print_header("TESTING FASTAPI APP")
    
    try:
        from main import app
        
        # Check if app was created
        print_test_result("App Creation", True)
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ['/', '/analyze']
        
        all_routes_present = all(route in routes for route in expected_routes)
        print_test_result("Expected Routes Present", all_routes_present, f"Found: {routes}")
        
        # Check CORS middleware
        has_cors = any('CORSMiddleware' in str(middleware) for middleware in app.user_middleware)
        print_test_result("CORS Middleware", has_cors)
        
        return all_routes_present and has_cors
        
    except Exception as e:
        print_test_result("FastAPI App", False, str(e))
        return False

def test_environment():
    """Test environment configuration"""
    print_header("TESTING ENVIRONMENT")
    
    try:
        from config import config
        
        # Check if API keys are set (config is a dictionary)
        google_key_set = bool(config.get("google_api_key"))
        openai_key_set = bool(config.get("openai_api_key"))
        
        print_test_result("Google API Key", google_key_set)
        print_test_result("OpenAI API Key", openai_key_set)
        
        return google_key_set and openai_key_set
        
    except Exception as e:
        print_test_result("Environment Config", False, str(e))
        return False

def test_orchestrator():
    """Test the multimodal orchestrator"""
    print_header("TESTING ORCHESTRATOR")
    
    try:
        from agents.multimodal_orchestrator import MultimodalOrchestrator
        
        orchestrator = MultimodalOrchestrator()
        print_test_result("Orchestrator Creation", True)
        
        # Test with no files (should handle gracefully)
        result = asyncio.run(orchestrator.run())
        
        # Check if result has expected structure
        expected_keys = ['text_analysis', 'audio_analysis', 'visual_analysis', 'summary']
        has_structure = all(key in result for key in expected_keys)
        
        print_test_result("Result Structure", has_structure, f"Keys: {list(result.keys())}")
        
        return has_structure
        
    except Exception as e:
        print_test_result("Orchestrator", False, str(e))
        return False

def test_api_server():
    """Test if the API server can start"""
    print_header("TESTING API SERVER")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, 'main.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print_test_result("Server Process", True)
            
            # Test health endpoint
            try:
                response = requests.get('http://localhost:8080/', timeout=5)
                if response.status_code == 200:
                    print_test_result("Health Endpoint", True, f"Response: {response.json()}")
                    server_working = True
                else:
                    print_test_result("Health Endpoint", False, f"Status: {response.status_code}")
                    server_working = False
            except Exception as e:
                print_test_result("Health Endpoint", False, str(e))
                server_working = False
            
            # Clean up
            process.terminate()
            process.wait()
            
            return server_working
        else:
            stdout, stderr = process.communicate()
            print_test_result("Server Process", False, f"Server exited: {stderr}")
            return False
            
    except Exception as e:
        print_test_result("API Server", False, str(e))
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint with test data"""
    print_header("TESTING ANALYZE ENDPOINT")
    
    try:
        # Create test audio
        audio_file = create_test_audio()
        if not audio_file:
            print_test_result("Test Audio Creation", False, "Could not create test audio")
            return False
        
        print_test_result("Test Audio Creation", True)
        
        # Start server
        process = subprocess.Popen([
            sys.executable, 'main.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for server to start
        time.sleep(5)
        
        if process.poll() is None:
            try:
                # Test analyze endpoint
                with open(audio_file, 'rb') as f:
                    files = {'audio': ('test.wav', f, 'audio/wav')}
                    response = requests.post('http://localhost:8080/analyze', files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    print_test_result("Analyze Endpoint", True, f"Got result with keys: {list(result.keys())}")
                    
                    # Check result structure
                    expected_keys = ['text_analysis', 'audio_analysis', 'visual_analysis', 'summary']
                    has_structure = all(key in result for key in expected_keys)
                    print_test_result("Result Structure", has_structure)
                    
                    analyze_working = has_structure
                else:
                    print_test_result("Analyze Endpoint", False, f"Status: {response.status_code}, Response: {response.text}")
                    analyze_working = False
                    
            except Exception as e:
                print_test_result("Analyze Endpoint", False, str(e))
                analyze_working = False
            
            # Clean up
            process.terminate()
            process.wait()
            
            # Clean up test file
            os.unlink(audio_file)
            
            return analyze_working
        else:
            stdout, stderr = process.communicate()
            print_test_result("Server Start", False, f"Server failed to start: {stderr}")
            os.unlink(audio_file)
            return False
            
    except Exception as e:
        print_test_result("Analyze Endpoint Test", False, str(e))
        return False

def main():
    """Run all tests"""
    print_header("BACKEND STANDALONE TESTING")
    print("Testing core backend functionality after frontend removal...")
    
    tests = [
        ("Imports", test_imports),
        ("FastAPI App", test_fastapi_app),
        ("Environment", test_environment),
        ("Orchestrator", test_orchestrator),
        ("API Server", test_api_server),
        ("Analyze Endpoint", test_analyze_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ FAIL {test_name} - Exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Backend is ready for integration.")
        return True
    else:
        print("⚠️  Some tests failed. Backend may need fixes before integration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
