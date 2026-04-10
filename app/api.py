from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import os
from app.chatbot_engine import AcademicChatbot

app = FastAPI(title="LifePathBot AI API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = AcademicChatbot()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"status": "online", "message": "LifePathBot AI API is running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF and save it to MongoDB after parsing"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        result = chatbot.process_document(temp_path, file.filename)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/chat")
async def chat(request: QuestionRequest):
    """Ask a question to the AI based on uploaded context"""
    result = chatbot.answer_question(request.question)
    return result

@app.get("/health")
async def health():
    return {
        "mongodb": chatbot.db_connected,
        "ollama_url": "http://localhost:11434"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
