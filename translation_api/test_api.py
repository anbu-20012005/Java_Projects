#!/usr/bin/env python3
"""
Test script for the Translation API
Run this after starting the FastAPI server to test all endpoints
"""

import requests
import json
import sys
from time import sleep

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
            return True
        else:
            print("❌ Health check failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Health check failed:", str(e))
        return False

def test_languages():
    """Test the languages endpoint"""
    print("\n🔍 Testing languages endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/languages")
        if response.status_code == 200:
            data = response.json()
            print("✅ Languages endpoint working:", data['total_count'], "languages supported")
            return True
        else:
            print("❌ Languages endpoint failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Languages endpoint failed:", str(e))
        return False

def test_translation():
    """Test the translation endpoint"""
    print("\n🔍 Testing translation endpoint...")
    
    # Test data
    test_cases = [
        {
            "text": "Hello world",
            "source_language": "English",
            "target_language": "Spanish",
            "description": "English to Spanish"
        },
        {
            "text": "Good morning",
            "source_language": "English", 
            "target_language": "French",
            "description": "English to French"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {test_case['description']}")
        print(f"    Input: '{test_case['text']}'")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/translate",
                json={
                    "text": test_case["text"],
                    "source_language": test_case["source_language"],
                    "target_language": test_case["target_language"]
                },
                timeout=60  # Extended timeout for translation
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Output: '{result['translated_text']}'")
                print(f"    ✅ Translation successful")
                success_count += 1
            else:
                print(f"    ❌ Translation failed: HTTP {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_detail = response.json()
                    print(f"    Error: {error_detail}")
                
        except requests.exceptions.Timeout:
            print(f"    ⏰ Translation timed out (this may be normal if Gradio app is cold starting)")
        except Exception as e:
            print(f"    ❌ Translation failed: {str(e)}")
    
    return success_count > 0

def test_validation():
    """Test input validation"""
    print("\n🔍 Testing input validation...")
    
    # Test empty text
    try:
        response = requests.post(
            f"{API_BASE_URL}/translate",
            json={
                "text": "",
                "source_language": "English",
                "target_language": "Spanish"
            }
        )
        if response.status_code == 422:
            print("✅ Empty text validation working")
        else:
            print("❌ Empty text validation failed")
    except Exception as e:
        print("❌ Empty text validation test failed:", str(e))
    
    # Test invalid language
    try:
        response = requests.post(
            f"{API_BASE_URL}/translate",
            json={
                "text": "Hello",
                "source_language": "InvalidLanguage",
                "target_language": "Spanish"
            }
        )
        if response.status_code == 422:
            print("✅ Invalid language validation working")
        else:
            print("❌ Invalid language validation failed")
    except Exception as e:
        print("❌ Invalid language validation test failed:", str(e))

def main():
    print("🧪 Translation API Test Suite")
    print("=" * 40)
    
    # Check if server is running
    if not test_health():
        print("\n❌ Server is not running. Please start the FastAPI server first:")
        print("   python main.py")
        sys.exit(1)
    
    # Run all tests
    test_languages()
    test_validation()
    
    print("\n" + "=" * 40)
    print("🔄 Testing translation functionality...")
    print("⚠️  Note: Translation tests require your Gradio app to be running.")
    print("   If tests fail, make sure:")
    print("   1. Your Gradio app is deployed and accessible")
    print("   2. GRADIO_APP_URL environment variable is set correctly")
    print("   3. The Gradio app is not in 'sleeping' state (first request may be slow)")
    
    translation_success = test_translation()
    
    print("\n" + "=" * 40)
    if translation_success:
        print("🎉 Translation API is working! Your extension should work correctly.")
    else:
        print("⚠️  Translation tests failed. Check your Gradio app configuration.")
    
    print("\n📖 Next steps:")
    print("   1. Load the extension from the 'extension_example' folder into Chrome")
    print("   2. Visit any webpage and select text to translate")
    print("   3. Configure your Gradio app URL in the environment variable GRADIO_APP_URL")

if __name__ == "__main__":
    main()