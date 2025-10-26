#!/usr/bin/env python3
"""
Test script for reorganized backend
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from src.api.main import app
        print("✅ API main imported successfully")
        
        from src.agents.multimodal_orchestrator import MultimodalOrchestrator
        print("✅ Multimodal orchestrator imported successfully")
        
        from src.config.settings import config
        print("✅ Config imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🧪 Testing FastAPI app...")
    
    try:
        from src.api.main import app
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ['/', '/analyze']
        
        all_routes_present = all(route in routes for route in expected_routes)
        print(f"✅ Routes present: {routes}")
        
        return all_routes_present
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False

def test_orchestrator():
    """Test orchestrator creation"""
    print("\n🧪 Testing orchestrator...")
    
    try:
        from src.agents.multimodal_orchestrator import MultimodalOrchestrator
        
        orchestrator = MultimodalOrchestrator()
        print("✅ Orchestrator created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Reorganized Backend")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("FastAPI App", test_fastapi_app),
        ("Orchestrator", test_orchestrator),
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
    print("\n📊 TEST SUMMARY")
    print("=" * 40)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Reorganized backend is working!")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
