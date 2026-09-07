from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from prompts.rag_Qna_generate_prompt import QUESTION_GENERATION_PROMPT
from utils.llm import Groq_llm




embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)


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

    response = Groq_llm.invoke(prompt)

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
        embedding=embeddings
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

    response = Groq_llm.invoke(prompt)

    return response.content