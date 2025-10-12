# Translation Service API

A FastAPI service that acts as a bridge between your browser extension and your Gradio translation app hosted on Hugging Face.

## Features

- RESTful API endpoints for text translation
- CORS enabled for browser extension compatibility
- Support for 10+ languages including English, Tamil, Hindi, French, Spanish, German, Chinese, Japanese, Korean, and Malayalam
- Batch translation support
- Error handling and validation
- Health check endpoint

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update Gradio URL:**
   Edit `main.py` and replace `GRADIO_APP_URL` with your actual Hugging Face Gradio app URL:
   ```python
   GRADIO_APP_URL = "https://your-username-your-space-name.hf.space/api/predict"
   ```

3. **Run the service:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### GET `/`
Root endpoint with API information.

### GET `/health`
Health check endpoint.

### GET `/languages`
Returns list of supported languages.

### POST `/translate`
Translate text between languages.

**Request Body:**
```json
{
  "text": "Hello, how are you?",
  "source_language": "English",
  "target_language": "Tamil"
}
```

**Response:**
```json
{
  "translated_text": "வணக்கம், எப்படி இருக்கிறீர்கள்?",
  "source_language": "English",
  "target_language": "Tamil",
  "original_text": "Hello, how are you?"
}
```

### POST `/translate/batch`
Translate multiple texts in a single request (max 10 items).

**Request Body:**
```json
[
  {
    "text": "Hello",
    "source_language": "English",
    "target_language": "Tamil"
  },
  {
    "text": "Good morning",
    "source_language": "English", 
    "target_language": "Hindi"
  }
]
```

## Browser Extension Integration

For your browser extension, you can make requests like this:

```javascript
// Example fetch request from your extension
async function translateText(text, sourceLang, targetLang) {
  try {
    const response = await fetch('http://localhost:8000/translate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        source_language: sourceLang,
        target_language: targetLang
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result.translated_text;
  } catch (error) {
    console.error('Translation error:', error);
    throw error;
  }
}

// Usage in your extension
translateText("Hello world", "English", "Tamil")
  .then(translation => console.log(translation))
  .catch(error => console.error(error));
```

## Supported Languages

- English (eng_Latn)
- Tamil (tam_Taml)  
- Hindi (hin_Deva)
- French (fra_Latn)
- Spanish (spa_Latn)
- German (deu_Latn)
- Chinese (zho_Hans)
- Japanese (jpn_Jpan)
- Korean (kor_Hang)
- Malayalam (mal_Mlym)

## Error Handling

The API provides detailed error messages for:
- Empty text input
- Unsupported languages
- Gradio service errors
- Timeout issues
- Connection problems

## Production Deployment

For production deployment:

1. Update CORS origins in `main.py` to specific domains
2. Add authentication if needed
3. Use environment variables for configuration
4. Deploy on cloud platforms like Heroku, Railway, or DigitalOcean

## Notes

- Make sure your Gradio app is publicly accessible
- The API endpoint URL should end with `/api/predict`
- Test your Gradio app independently before integrating