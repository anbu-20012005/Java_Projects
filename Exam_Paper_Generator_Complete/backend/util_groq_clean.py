import requests
import docx
from pdfminer.high_level import extract_text
import re
import os

# === CONFIGURATION ===
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# === FILE TEXT EXTRACTOR ===
def extract_text_from_file(filepath):
    if filepath.endswith(".pdf"):
        return extract_text(filepath)
    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif filepath.endswith(".docx"):
        doc = docx.Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format")

# === CHUNKING WITHOUT NLTK ===
def split_text_into_chunks(text, words_per_chunk=100):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks = []
    current_chunk = ""
    word_count = 0
    for sentence in sentences:
        current_chunk += sentence + " "
        word_count += len(sentence.split())
        if word_count >= words_per_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = ""
            word_count = 0
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# === QUESTION GENERATION ===
def generate_question(text):
    prompt = f"Generate a meaningful exam question based on this content: {text} and the question must be in a single or two lines"
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are an educational assistant that creates exam questions."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    else:
        return f"Error: {response.status_code} - {response.text}"

# === QUESTION CATEGORIZATION ===
def categorize_questions(questions, total_marks):
    if not questions:
        return []
    marks_per_question = total_marks // len(questions)
    categorized = []
    for q in questions:
        if marks_per_question <= 2:
            level = "Easy"
        elif marks_per_question <= 5:
            level = "Medium"
        else:
            level = "Hard"
        categorized.append((q, marks_per_question, level))
    return categorized
