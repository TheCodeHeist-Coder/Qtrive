from fastapi import FastAPI, UploadFile, File, HTTPException,Form, Request
from fastapi.responses import JSONResponse
from app.agent.Qnagent import chat
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path
import os
import shutil
from app.rag.rag_system import generate_questions,ask_pdf
from app.utils.config import MissingAPIKey


app = FastAPI(title="Rexial GenAI Service")

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(MissingAPIKey)
async def missing_api_key_handler(request: Request, exc: MissingAPIKey):
    """Return a clear 503 instead of an opaque 500 when a key is absent."""

    return JSONResponse(
        status_code=503,
        content={"detail": str(exc)},
    )


UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ChatRequest(BaseModel):
    user_query: str


def save_upload(file: UploadFile) -> Path:
    """Persist an uploaded PDF under UPLOAD_DIR using a safe filename."""

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # strip any directory components a client may have sent
    safe_name = Path(file.filename or "upload.pdf").name

    if not safe_name:
        raise HTTPException(
            status_code=400,
            detail="Invalid file name."
        )

    file_path = UPLOAD_DIR / safe_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


@app.get("/")
def home():
    return {"message": "AI Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


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

    file_path = save_upload(file)

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

    file_path = save_upload(file)

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