# Translation API Service

A FastAPI service that acts as a bridge between your browser extension and your Hugging Face Gradio translation app.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Gradio app URL as an environment variable:
```bash
export GRADIO_APP_URL="https://your-username-your-space-name.hf.space"
```

3. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET `/`
Returns basic API information and available endpoints.

### GET `/health`
Health check endpoint to verify the service is running.

### GET `/languages`
Returns the list of supported languages.

### POST `/translate`
Translates text using your Gradio app.

**Request Body:**
```json
{
    "text": "Hello world",
    "source_language": "English",
    "target_language": "Spanish"
}
```

**Response:**
```json
{
    "original_text": "Hello world",
    "translated_text": "Hola mundo",
    "source_language": "English",
    "target_language": "Spanish",
    "success": true
}
```

### POST `/batch-translate`
Translates multiple texts in a single request (max 10).

**Request Body:**
```json
[
    {
        "text": "Hello",
        "source_language": "English",
        "target_language": "Spanish"
    },
    {
        "text": "World",
        "source_language": "English",
        "target_language": "French"
    }
]
```

## Supported Languages

- English
- Tamil
- Hindi
- French
- Spanish
- German
- Chinese
- Japanese
- Korean
- Malayalam

## Browser Extension Usage

In your browser extension's content script or background script, you can make requests like this:

```javascript
// Simple translation
async function translateText(text, sourceLang, targetLang) {
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
        throw new Error('Translation failed');
    }
    
    return await response.json();
}

// Usage example
translateText("Hello world", "English", "Spanish")
    .then(result => {
        console.log('Translated:', result.translated_text);
    })
    .catch(error => {
        console.error('Translation error:', error);
    });
```

## Configuration

- **GRADIO_APP_URL**: Set this environment variable to your Hugging Face Gradio app URL
- **Port**: The server runs on port 8000 by default
- **CORS**: Currently configured to allow all origins for development. In production, update the CORS settings in `main.py` to only allow your extension's origin.

## Production Deployment

For production deployment:

1. Update CORS settings to be more restrictive
2. Add proper logging
3. Consider rate limiting
4. Use a production ASGI server like Gunicorn
5. Set up proper environment variable management