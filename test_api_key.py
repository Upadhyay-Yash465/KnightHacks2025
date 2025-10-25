#!/usr/bin/env python3
"""
Google API Key Tester

This script tests your Google API key and shows available models.
"""

import os
import sys

def test_api_key():
    """Test the Google API key and show available models."""
    print("🔑 Testing Google API Key...")
    
    # Check if API key is set
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No API key found!")
        print("Set it with: export GOOGLE_API_KEY=your_key_here")
        return False
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    try:
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
        
        # List available models
        print("\n📋 Available Models:")
        try:
            models = list(genai.list_models())
            if models:
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        print(f"✅ {model.name}")
                    else:
                        print(f"⚠️  {model.name} (no generateContent)")
            else:
                print("❌ No models found")
        except Exception as e:
            print(f"❌ Error listing models: {str(e)}")
            return False
        
        # Test a simple generation
        print("\n🧪 Testing Model Generation...")
        try:
            # Try different model names
            test_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
            
            for model_name in test_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Hello, this is a test.")
                    print(f"✅ {model_name}: Working!")
                    print(f"   Response: {response.text[:50]}...")
                    return True
                except Exception as e:
                    print(f"❌ {model_name}: {str(e)}")
                    continue
            
            print("❌ No working models found")
            return False
            
        except Exception as e:
            print(f"❌ Generation test failed: {str(e)}")
            return False
            
    except ImportError:
        print("❌ google-generativeai not installed")
        print("Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def show_troubleshooting():
    """Show troubleshooting steps."""
    print("\n🔧 Troubleshooting Steps:")
    print("1. Check API key permissions:")
    print("   https://console.cloud.google.com/apis/credentials")
    print("\n2. Enable required APIs:")
    print("   https://console.cloud.google.com/apis/library")
    print("   - Generative Language API")
    print("   - AI Platform API")
    print("\n3. Check billing:")
    print("   https://console.cloud.google.com/billing")
    print("\n4. Check quotas:")
    print("   https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas")
    print("\n5. Try creating a new API key:")
    print("   https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    print("🎤 Google API Key Tester")
    print("=" * 30)
    
    success = test_api_key()
    
    if not success:
        show_troubleshooting()
        sys.exit(1)
    else:
        print("\n🎉 API key is working correctly!")
        print("Your AI/ML module should work with Google ADK suggestions.")
