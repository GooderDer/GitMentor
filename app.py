"""Phase 7：GitMentor 的 FastAPI HTTP 接口。"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from analyzer import analyze_repository
from demo_rag import build_chunks
from rag import RetrievalQA, Retriever
from vectorstore import ChromaVectorStore, LocalEmbedder

app = FastAPI(title="GitMentor API", version="0.1.0")


class AnalyzeRequest(BaseModel):
    repo_path: str = Field(default=".", description="本地仓库路径")


class AskRequest(BaseModel):
    repo_path: str = Field(default=".", description="本地仓库路径")
    question: str = Field(min_length=1, description="要询问的问题")
    top_k: int = Field(default=3, ge=1, le=20)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    try:
        return asdict(analyze_repository(Path(request.repo_path)))
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/ask")
def ask(request: AskRequest) -> dict:
    try:
        repo_path = Path(request.repo_path).resolve()
        _, chunks = build_chunks(repo_path)
        if not chunks:
            raise HTTPException(status_code=400, detail="没有找到可检索的 README 或代码 Chunk。")
        store = ChromaVectorStore(LocalEmbedder(), collection_name="gitmentor_api")
        store.add_chunks(chunks)
        result = RetrievalQA(Retriever(store, top_k=request.top_k)).ask(
            request.question,
            top_k=request.top_k,
        )
        return asdict(result)
    except HTTPException:
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
