import json
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.prompts.quiz_json_prompt import QUIZ_JSON_PROMPT
from app.prompts.rag_Qna_generate_prompt import QUESTION_GENERATION_PROMPT
from app.utils.llm import get_groq_llm

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

_embeddings = None


def get_embeddings():
    """Load the embedding model on first use.

    Loading at import time would block application startup (and the
    /health endpoint) while the model is fetched, which makes the
    container fail its healthcheck on a cold start.
    """

    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

    return _embeddings


def generate_questions(pdf_path: str, user_query: str):

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300
    )

    chunks = splitter.split_documents(documents)

    context = "\n\n".join(
        doc.page_content
        for doc in chunks
    )

    prompt = QUESTION_GENERATION_PROMPT.format(
        context=context,
        user_query=user_query
    )

    response = get_groq_llm().invoke(prompt)

    return response.content


def create_pdf_vectorstore(pdf_path: str):

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    vectorstore = InMemoryVectorStore.from_documents(
        chunks,
        embedding=get_embeddings()
    )

    return vectorstore


def ask_pdf(pdf_path: str, user_query: str):

    vectorstore = create_pdf_vectorstore(pdf_path)

    docs = vectorstore.similarity_search(
        user_query,
        k=5
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""
You are a PDF question-answering assistant.

Answer the user's question using ONLY the information
provided in the PDF context.

If the answer is not available in the context,
say that the information is not available in the PDF.

PDF Context:
{context}

User Question:
{user_query}

Give a clear and accurate answer.
"""

    response = get_groq_llm().invoke(prompt)

    return response.content

def _extract_json(raw: str) -> dict:
    """Pull a JSON object out of an LLM response.

    Models often wrap JSON in markdown fences or add a sentence around it
    despite being told not to, so fall back to the outermost braces.
    """

    text = raw.strip()

    if text.startswith("```"):
        # drop the opening fence (which may be ```json) and closing fence
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response did not contain a JSON object.")

    return json.loads(text[start:end + 1])


def generate_quiz(pdf_path: str, user_query: str) -> list[dict]:
    """Generate multiple-choice questions as structured data.

    Returns a list of questions, each with exactly four options and
    exactly one correct answer. Malformed questions are dropped rather
    than failing the whole request.
    """

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300
    )

    chunks = splitter.split_documents(documents)

    context = "\n\n".join(doc.page_content for doc in chunks)

    prompt = QUIZ_JSON_PROMPT.format(
        context=context,
        user_query=user_query
    )

    response = get_groq_llm().invoke(prompt)

    payload = _extract_json(str(response.content))

    questions = []

    for item in payload.get("questions", []):
        text = str(item.get("text", "")).strip()
        options = item.get("options", [])

        if not text or not isinstance(options, list):
            continue

        cleaned = [
            {
                "text": str(o.get("text", "")).strip(),
                "isCorrect": bool(o.get("isCorrect", False)),
            }
            for o in options
            if isinstance(o, dict) and str(o.get("text", "")).strip()
        ]

        # the UI and the quiz schema both assume four options with a
        # single correct answer, so discard anything else
        if len(cleaned) != 4:
            continue

        if sum(o["isCorrect"] for o in cleaned) != 1:
            continue

        difficulty = str(item.get("difficulty", "Medium")).capitalize()

        if difficulty not in ("Low", "Medium", "High"):
            difficulty = "Medium"

        questions.append({
            "text": text,
            "difficulty": difficulty,
            "options": cleaned,
        })

    return questions
