"""
Test script for the Translation Service API
Run this after starting the FastAPI server to test the endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Root endpoint working\n")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}\n")

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Health endpoint working\n")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}\n")

def test_languages():
    """Test languages endpoint"""
    print("Testing languages endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/languages")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Languages endpoint working\n")
    except Exception as e:
        print(f"❌ Languages endpoint failed: {e}\n")

def test_translation():
    """Test translation endpoint (will fail without actual Gradio URL)"""
    print("Testing translation endpoint...")
    try:
        payload = {
            "text": "Hello, how are you?",
            "source_language": "English",
            "target_language": "Tamil"
        }
        
        response = requests.post(
            f"{BASE_URL}/translate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Translation endpoint working\n")
        else:
            print("⚠️ Translation endpoint returned error (expected without valid Gradio URL)\n")
            
    except Exception as e:
        print(f"❌ Translation endpoint failed: {e}\n")

def test_validation():
    """Test input validation"""
    print("Testing input validation...")
    
    # Test empty text
    try:
        payload = {
            "text": "",
            "source_language": "English", 
            "target_language": "Tamil"
        }
        response = requests.post(f"{BASE_URL}/translate", json=payload)
        print(f"Empty text - Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Empty text validation working")
        else:
            print("❌ Empty text validation failed")
    except Exception as e:
        print(f"❌ Empty text test failed: {e}")
    
    # Test invalid language
    try:
        payload = {
            "text": "Hello",
            "source_language": "InvalidLanguage",
            "target_language": "Tamil"
        }
        response = requests.post(f"{BASE_URL}/translate", json=payload)
        print(f"Invalid language - Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Invalid language validation working")
        else:
            print("❌ Invalid language validation failed")
    except Exception as e:
        print(f"❌ Invalid language test failed: {e}")
    
    print()

if __name__ == "__main__":
    print("🚀 Starting Translation Service API Tests\n")
    print("Make sure the FastAPI server is running on localhost:8000")
    print("Start server with: python main.py\n")
    
    test_root()
    test_health()
    test_languages()
    test_validation()
    test_translation()
    
    print("📋 Test Summary:")
    print("- Root, health, and languages endpoints should work immediately")
    print("- Translation endpoint will fail until you update GRADIO_APP_URL in main.py")
    print("- Validation tests should show proper error handling")
    print("\n🔧 Next steps:")
    print("1. Update GRADIO_APP_URL in main.py with your actual Hugging Face space URL")
    print("2. Test translation endpoint again")
    print("3. Integrate with your browser extension")