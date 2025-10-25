"""
Simple test script for the Public Speaking Coach API.
Tests the main endpoints to verify functionality.
"""

import requests
import json


BASE_URL = "http://localhost:8000"


def test_root():
    """Test root endpoint."""
    print("Testing GET /")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_health():
    """Test health endpoint."""
    print("Testing GET /health")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_analyze_text():
    """Test text analysis endpoint."""
    print("Testing POST /analyze-text")
    
    test_transcript = (
        "Um, so I think that, like, you know, public speaking is really important. "
        "And, uh, basically, what we need to do is, like, practice more often. "
        "You know, so that we can, um, improve our skills."
    )
    
    payload = {
        "transcript": test_transcript,
        "user_id": "test_user"
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-text",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_history():
    """Test history endpoint."""
    print("Testing GET /history/test_user")
    response = requests.get(f"{BASE_URL}/history/test_user")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Public Speaking Coach API Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_root()
        test_health()
        test_analyze_text()
        test_history()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

