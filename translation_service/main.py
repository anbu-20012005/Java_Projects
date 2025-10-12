from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from typing import Optional

app = FastAPI(
    title="Translation Service API",
    description="FastAPI service to communicate with Gradio translation app",
    version="1.0.0"
)

# Add CORS middleware to allow requests from browser extensions and web pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    original_text: str

# Language mapping (same as your Gradio app)
LANGUAGES = {
    "English": "eng_Latn",
    "Tamil": "tam_Taml",
    "Hindi": "hin_Deva",
    "French": "fra_Latn",
    "Spanish": "spa_Latn",
    "German": "deu_Latn",
    "Chinese": "zho_Hans",
    "Japanese": "jpn_Jpan",
    "Korean": "kor_Hang",
    "Malayalam": "mal_Mlym"
}

# Configuration - Replace with your actual Gradio app URL
GRADIO_APP_URL = "https://your-huggingface-space-url/api/predict"  # Update this!

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Translation Service API",
        "description": "FastAPI service for text translation using Gradio backend",
        "endpoints": {
            "translate": "/translate - POST request with text and languages",
            "languages": "/languages - GET supported languages",
            "health": "/health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "translation-api"}

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": list(LANGUAGES.keys()),
        "total_count": len(LANGUAGES)
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text using the Gradio backend
    
    Args:
        request: TranslationRequest containing text and language preferences
    
    Returns:
        TranslationResponse with translated text
    """
    
    # Validate input
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if request.source_language not in LANGUAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Source language '{request.source_language}' not supported. Supported: {list(LANGUAGES.keys())}"
        )
    
    if request.target_language not in LANGUAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Target language '{request.target_language}' not supported. Supported: {list(LANGUAGES.keys())}"
        )
    
    try:
        # Prepare payload for Gradio API
        payload = {
            "data": [
                request.text,
                request.source_language,
                request.target_language
            ]
        }
        
        # Make request to Gradio app
        response = requests.post(
            GRADIO_APP_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30 second timeout
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Gradio service error: {response.status_code}"
            )
        
        # Parse response
        gradio_response = response.json()
        translated_text = gradio_response.get("data", [None])[0]
        
        if not translated_text:
            raise HTTPException(
                status_code=502,
                detail="Invalid response from translation service"
            )
        
        return TranslationResponse(
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            original_text=request.text
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Translation service timeout"
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Cannot connect to translation service"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Alternative endpoint for batch translation (if needed for extension)
@app.post("/translate/batch")
async def translate_batch(requests_list: list[TranslationRequest]):
    """
    Translate multiple texts in batch
    
    Args:
        requests_list: List of TranslationRequest objects
    
    Returns:
        List of TranslationResponse objects
    """
    if len(requests_list) > 10:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Batch size cannot exceed 10 items"
        )
    
    results = []
    for req in requests_list:
        try:
            result = await translate_text(req)
            results.append(result)
        except HTTPException as e:
            results.append({
                "error": e.detail,
                "original_text": req.text,
                "source_language": req.source_language,
                "target_language": req.target_language
            })
    
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)