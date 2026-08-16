from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag.config import DEFAULT_TOP_K, FAISS_INDEX_PATH, METADATA_PATH
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.retrieval import RetrievalService

# Global service instance
retrieval_service: Optional[RetrievalService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retrieval_service
    embedding_model = MultilingualEmbeddingModel()

    if FAISS_INDEX_PATH.exists() and METADATA_PATH.exists():
        index = VectorIndex.load(FAISS_INDEX_PATH, METADATA_PATH)
    else:
        index = VectorIndex(dimension=embedding_model.get_dimension())

    retrieval_service = RetrievalService(
        embedding_model=embedding_model,
        index=index,
    )
    yield


app = FastAPI(
    title="HHGoa High-Performance RAG Retrieval API",
    description="Low-latency vector retrieval service for HHGoa Voice RAG System",
    version="0.1.0",
    lifespan=lifespan,
)


class RetrievalRequest(BaseModel):
    query: str = Field(..., description="User query text", json_schema_extra={"example": "What is a corporation?"})
    top_k: int = Field(DEFAULT_TOP_K, description="Number of passages to retrieve", ge=1, le=50)


class ResultItem(BaseModel):
    chunk_id: str
    text: str
    score: float
    language: str
    metadata: Dict[str, Any] = {}


class TimingItem(BaseModel):
    embedding_ms: float
    retrieval_ms: float
    total_ms: float


class RetrievalApiResponse(BaseModel):
    results: List[ResultItem]
    timing: TimingItem


@app.get("/health")
def health_check():
    index_loaded = (
        retrieval_service is not None
        and retrieval_service.index is not None
        and len(retrieval_service.index) > 0
    )
    return {
        "status": "healthy",
        "index_loaded": index_loaded,
        "indexed_chunks": len(retrieval_service.index) if retrieval_service and retrieval_service.index else 0,
    }


@app.post("/api/retrieve", response_model=RetrievalApiResponse)
def retrieve(request: RetrievalRequest):
    if retrieval_service is None:
        raise HTTPException(status_code=503, detail="Retrieval service not initialized")

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")

    response = retrieval_service.retrieve(
        query=request.query,
        top_k=request.top_k,
    )

    results = [
        ResultItem(
            chunk_id=r.chunk_id,
            text=r.text,
            score=r.score,
            language=r.language,
            metadata=r.metadata,
        )
        for r in response.results
    ]

    timing = TimingItem(
        embedding_ms=response.timing.embedding_ms,
        retrieval_ms=response.timing.retrieval_ms,
        total_ms=response.timing.total_ms,
    )

    return RetrievalApiResponse(results=results, timing=timing)
