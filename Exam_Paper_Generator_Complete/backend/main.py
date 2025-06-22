from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil, os, json
from util_groq_clean import (extract_text_from_file, split_text_into_chunks,
                             generate_question)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/generate")
async def generate(file: UploadFile, config: str = Form(...)):
    """
    `config` arrives as JSON:
        [ {"mark":2, "count":3}, {"mark":5, "count":2}, ... ]
    """
    cfg = json.loads(config)

    # 1. Save the uploaded file temporarily
    os.makedirs("temp", exist_ok=True)
    tmp_path = f"temp/{file.filename}"
    with open(tmp_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    # 2. Extract & chunk text
    text    = extract_text_from_file(tmp_path)
    chunks  = split_text_into_chunks(text, words_per_chunk=120)

    # 3. Generate questions
    questions = []
    chunk_idx = 0
    for entry in cfg:
        mark, count = entry["mark"], entry["count"]
        for _ in range(count):
            # cycle through chunks if we run out
            source = chunks[chunk_idx % len(chunks)]
            chunk_idx += 1
            q_text = generate_question(source)
            level  = "Easy" if mark <= 2 else "Medium" if mark <= 5 else "Hard"
            questions.append({"text": q_text, "marks": mark, "level": level})

    os.remove(tmp_path)
    return JSONResponse({"questions": questions})
