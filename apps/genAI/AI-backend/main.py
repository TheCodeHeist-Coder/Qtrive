from fastapi import FastAPI, UploadFile, File, HTTPException,Form
from agent.Qnagent import chat
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path
import shutil
from rag.rag_system import generate_questions,ask_pdf


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class ChatRequest(BaseModel):
    user_query: str


@app.get("/")
def home():
    return {"message": "AI Backend is running"}


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    response = chat(request.user_query)

    return {
        "response": response
    }


@app.post("/generate-questions")
async def generate_pdf_questions(
    file: UploadFile = File(...),
    user_query: str = Form(...)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    questions = generate_questions(
        str(file_path),
        user_query
    )

    return {
        "message": "Questions generated successfully",
        "filename": file.filename,
        "questions": questions
    }



@app.post("/ask-pdf")
async def ask_pdf_question(
    file: UploadFile = File(...),
    user_query: str = Form(...)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    answer = ask_pdf(
        str(file_path),
        user_query
    )

    return {
        "message": "Answer generated successfully",
        "filename": file.filename,
        "question": user_query,
        "answer": answer
    }