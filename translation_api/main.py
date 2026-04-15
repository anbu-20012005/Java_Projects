from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import requests
import json
from typing import Optional
import os

# Initialize FastAPI app
app = FastAPI(
    title="Translation API Service",
    description="API service to communicate with Hugging Face Gradio translation app",
    version="1.0.0"
)

# Add CORS middleware for browser extension compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your extension's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported languages mapping
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

# Pydantic models for request/response validation
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('source_language', 'target_language')
    def language_must_be_supported(cls, v):
        if v not in LANGUAGES:
            raise ValueError(f'Language {v} not supported. Available languages: {list(LANGUAGES.keys())}')
        return v

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    success: bool

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Configuration - Set your Hugging Face Gradio app URL here
GRADIO_APP_URL = os.getenv("GRADIO_APP_URL", "https://your-username-your-space-name.hf.space")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Translation API Service",
        "version": "1.0.0",
        "endpoints": {
            "translate": "/translate",
            "languages": "/languages",
            "health": "/health"
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
        "supported_languages": list(LANGUAGES.keys()),
        "total_count": len(LANGUAGES)
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text using the Hugging Face Gradio app
    """
    try:
        # Prepare the payload for Gradio API
        payload = {
            "data": [
                request.text,
                request.source_language,
                request.target_language
            ]
        }
        
        # Make request to Gradio app
        gradio_url = f"{GRADIO_APP_URL}/api/predict"
        
        response = requests.post(
            gradio_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30 second timeout
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Gradio app returned status {response.status_code}"
            )
        
        result = response.json()
        
        # Extract translated text from Gradio response
        if "data" in result and len(result["data"]) > 0:
            translated_text = result["data"][0]
        else:
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from Gradio app"
            )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            success=True
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Translation service timeout. Please try again."
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to translation service. Please check if the Gradio app is running."
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with translation service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/batch-translate")
async def batch_translate(requests_list: list[TranslationRequest]):
    """
    Translate multiple texts in batch
    """
    if len(requests_list) > 10:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Batch size cannot exceed 10 translations"
        )
    
    results = []
    for req in requests_list:
        try:
            result = await translate_text(req)
            results.append(result)
        except Exception as e:
            results.append({
                "original_text": req.text,
                "translated_text": "",
                "source_language": req.source_language,
                "target_language": req.target_language,
                "success": False,
                "error": str(e)
            })
    
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)