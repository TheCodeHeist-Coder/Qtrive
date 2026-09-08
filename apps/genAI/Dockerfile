FROM python:3.11-slim

WORKDIR /app/apps/genAI

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/models \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10

# build deps for faiss / sentence-transformers wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/genAI/requirements.txt ./requirements.txt

# cache mount keeps already-downloaded wheels across retries, so a dropped
# connection does not restart the whole (multi-GB) download
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install --resume-retries 10 -r requirements.txt

COPY apps/genAI/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
