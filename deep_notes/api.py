import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from deep_notes.components.vector_store import clear_collection
from deep_notes.config import get_settings
from deep_notes.ingest import run_ingest
from deep_notes.query import retrieve, stream_answer

app = FastAPI(title="Deep Notes API")
settings = get_settings()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_key(creds: HTTPAuthorizationCredentials = Security(security)):
    if not settings.api_key:
        raise HTTPException(500, "API_KEY not configured on server")
    if creds.credentials != settings.api_key:
        raise HTTPException(401, "Invalid API key")


# --- Models ---

class QueryRequest(BaseModel):
    question: str
    chat_history: list[dict] = []


class IndexRequest(BaseModel):
    vault_path: str | None = None


# --- Endpoints ---

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/query")
def query(req: QueryRequest, _=Security(verify_key)):
    retrieval = retrieve(req.question, settings)
    tokens = list(stream_answer(
        question=req.question,
        context_str=retrieval.context_str,
        chat_history=req.chat_history,
        config=settings,
    ))
    answer = "".join(tokens)
    return {
        "answer": answer,
        "sources": [
            {
                "file_name": s.file_name,
                "file_path": s.file_path,
                "text": s.text,
                "score": s.score,
            }
            for s in retrieval.sources
        ],
    }


@app.post("/api/index")
def index(req: IndexRequest, _=Security(verify_key)):
    config = get_settings(**({"vault_path": req.vault_path} if req.vault_path else {}))
    count = run_ingest(config)
    return {"count": count}


@app.post("/api/clear-index")
def clear_index(_=Security(verify_key)):
    clear_collection(settings)
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("deep_notes.api:app", host="127.0.0.1", port=settings.api_port, reload=True)
