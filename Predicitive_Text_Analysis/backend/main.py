from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq

# python -m uvicorn main:app --reload --port 8080

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt template
PROMPT_TEMPLATE = """
You are an AI system trained for predictive text generation.
Given an input text, continue writing naturally and intelligently.
Avoid repeating the input and generate a meaningful continuation.

### Input Text:
{text_input}

### Output:
Only the continuation text. Do not include the input again.
"""

# Request model
class PromptRequest(BaseModel):
    prompt: str

@app.post("/api/predict")
async def predict_text(req: PromptRequest):
    if not GROQ_API_KEY:
        return {"error": "GROQ_API_KEY is missing."}

    client = Groq(api_key=GROQ_API_KEY)

    try:
        formatted_prompt = PROMPT_TEMPLATE.format(text_input=req.prompt)

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a predictive text AI trained to extend user input meaningfully."},
                {"role": "user", "content": formatted_prompt}
            ],
            model="llama3-8b-8192"
        )

        generated_text = response.choices[0].message.content.strip()
        return {"completion": generated_text}

    except Exception as e:
        return {"error": str(e)}
