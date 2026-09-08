# GenAI Service

FastAPI service powering Rexial's AI features: PDF-grounded question
generation, PDF Q&A (RAG), and a chat agent with web search.

## Structure

```
apps/genAI/
├── app/
│   ├── main.py       # FastAPI app and routes
│   ├── agent/        # chat agent (router + Tavily web search)
│   ├── rag/          # PDF loading, chunking, embeddings, retrieval
│   ├── prompts/      # prompt templates
│   └── utils/        # config and LLM clients
├── requirements.txt
├── Dockerfile        # dev (hot reload)
└── Dockerfile.prod   # production (venv, baked model, non-root)
```

## Setup

```bash
cp .env.example .env    # then fill in your API keys
pnpm run setup          # creates .venv, installs requirements
pnpm run dev            # http://localhost:8000
```

Interactive API docs: http://localhost:8000/docs

## Environment

| Variable          | Description                                  |
| ----------------- | -------------------------------------------- |
| `GROQ_API_KEY`    | Groq key, used for RAG and question generation |
| `GOOGLE_API_KEY`  | Gemini key, used by the chat agent            |
| `TAVILY_API_KEY`  | Tavily key, used for web search               |
| `GENAI_PORT`      | Port to listen on (default `8000`)            |
| `UPLOAD_DIR`      | Where uploaded PDFs are stored                |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins, or `*`          |

## Endpoints

| Method | Path                  | Body                        |
| ------ | --------------------- | --------------------------- |
| GET    | `/health`             | –                           |
| POST   | `/chat`               | JSON `{ user_query }`       |
| POST   | `/generate-questions` | multipart `file`, `user_query` |
| POST   | `/ask-pdf`            | multipart `file`, `user_query` |

## Docker

Both compose files include this service (`genai`). Built from the repo root:

```bash
docker compose up --build genai
```

The production image bakes the `all-mpnet-base-v2` embedding model in at
build time, so containers don't download it on cold start.

## Deployment notes

In production the service runs on the `rexial-network` and is exposed through
nginx-proxy-manager, the same way `frontend` / `backend` / `ws-server` are.

Add a proxy host in nginx-proxy-manager (port `81`):

| Field           | Value          |
| --------------- | -------------- |
| Domain          | `ai.rexial.in` |
| Forward hostname | `genai`        |
| Forward port    | `8000`         |

Then set these in `.env.prod` on the server:

```bash
GROQ_API_KEY=...
GOOGLE_API_KEY=...
TAVILY_API_KEY=...
ALLOWED_ORIGINS=https://rexial.in
```

`ALLOWED_ORIGINS` should be the real frontend origin in production — the
`*` default is only for local development.

Note: PDF uploads are written to the `genai_uploads` volume and are never
cleaned up automatically. Consider a retention job if usage grows.
