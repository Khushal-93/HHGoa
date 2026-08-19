from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag.config import DEFAULT_TOP_K, FAISS_INDEX_PATH, METADATA_PATH
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.orchestrator import RAGOrchestrator
from rag.retrieval import RetrievalService

# Global service and orchestrator instances
retrieval_service: Optional[RetrievalService] = None
orchestrator: Optional[RAGOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retrieval_service, orchestrator
    embedding_model = MultilingualEmbeddingModel()

    if FAISS_INDEX_PATH.exists() and METADATA_PATH.exists():
        index = VectorIndex.load(FAISS_INDEX_PATH, METADATA_PATH)
    else:
        index = VectorIndex(dimension=embedding_model.get_dimension())

    retrieval_service = RetrievalService(
        embedding_model=embedding_model,
        index=index,
    )
    orchestrator = RAGOrchestrator(
        retrieval_service=retrieval_service,
    )
    yield


app = FastAPI(
    title="HHGoa Ultra-Low-Latency Grounded RAG & Voice API",
    description="Full grounded RAG pipeline and voice retrieval service for HHGoa Voice RAG System",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


class RetrievalTimingItem(BaseModel):
    embedding_ms: float
    retrieval_ms: float
    total_ms: float


class RetrievalApiResponse(BaseModel):
    results: List[ResultItem]
    timing: RetrievalTimingItem


class GroundedQueryApiRequest(BaseModel):
    query: str = Field(..., description="User question string", json_schema_extra={"example": "What is a corporation?"})


class SourceItem(BaseModel):
    chunk_id: str
    text: str
    score: float
    language: str = "hin_Deva"
    metadata: Dict[str, Any] = {}


class PipelineTimingApiResponse(BaseModel):
    stt_ms: float = 0.0
    query_preprocessing_ms: float = 0.0
    query_embedding_ms: float = 0.0
    vector_search_ms: float = 0.0
    metadata_lookup_ms: float = 0.0
    retrieval_total_ms: float = 0.0
    answerability_check_ms: float = 0.0
    context_build_ms: float = 0.0
    llm_generation_ms: float = 0.0
    grounding_validation_ms: float = 0.0
    api_overhead_ms: float = 0.0
    total_pipeline_ms: float = 0.0


class GroundedQueryApiResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    timing: PipelineTimingApiResponse
    grounded: bool
    confidence_score: float


class VoiceQueryApiResponse(BaseModel):
    transcript: str
    answer: str
    sources: List[SourceItem]
    timing: PipelineTimingApiResponse
    grounded: bool
    confidence_score: float


@app.get("/health")
def health_check():
    index_loaded = (
        retrieval_service is not None
        and retrieval_service.index is not None
        and len(retrieval_service.index) > 0
    )
    idx_obj = retrieval_service.index if index_loaded else None
    idx_type = idx_obj.index.__class__.__name__ if idx_obj and idx_obj.index else "None"
    ef_search = getattr(idx_obj.index.hnsw, "efSearch", None) if idx_obj and hasattr(idx_obj.index, "hnsw") else None
    dim = idx_obj.dimension if idx_obj else 0

    return {
        "status": "healthy",
        "index_loaded": index_loaded,
        "indexed_chunks": len(idx_obj) if idx_obj else 0,
        "vector_count": len(idx_obj) if idx_obj else 0,
        "dimension": dim,
        "index_type": idx_type,
        "ef_search": ef_search,
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

    timing = RetrievalTimingItem(
        embedding_ms=response.timing.embedding_ms,
        retrieval_ms=response.timing.retrieval_ms,
        total_ms=response.timing.total_ms,
    )

    return RetrievalApiResponse(results=results, timing=timing)


@app.post("/api/query", response_model=GroundedQueryApiResponse)
def query_rag(request: GroundedQueryApiRequest):
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="RAG Orchestrator not initialized")

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")

    res = orchestrator.run_text_pipeline(query=request.query)

    sources = [
        SourceItem(
            chunk_id=s.chunk_id,
            text=s.text,
            score=s.score,
            language=s.language,
            metadata=s.metadata,
        )
        for s in res.sources
    ]

    t = res.timing
    timing = PipelineTimingApiResponse(
        stt_ms=t.stt_ms,
        query_preprocessing_ms=t.query_preprocessing_ms,
        query_embedding_ms=t.query_embedding_ms,
        vector_search_ms=t.vector_search_ms,
        metadata_lookup_ms=t.metadata_lookup_ms,
        retrieval_total_ms=t.retrieval_total_ms,
        answerability_check_ms=t.answerability_check_ms,
        context_build_ms=t.context_build_ms,
        llm_generation_ms=t.llm_generation_ms,
        grounding_validation_ms=t.grounding_validation_ms,
        api_overhead_ms=t.api_overhead_ms,
        total_pipeline_ms=t.total_pipeline_ms,
    )

    return GroundedQueryApiResponse(
        answer=res.answer,
        sources=sources,
        timing=timing,
        grounded=res.grounded,
        confidence_score=res.confidence_score,
    )


@app.post("/api/voice/ask", response_model=VoiceQueryApiResponse)
async def ask_voice(file: UploadFile = File(...), language: str = Form("hin_Deva")):
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="RAG Orchestrator not initialized")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio payload provided")

    res = orchestrator.run_voice_pipeline(audio_bytes=audio_bytes, language=language)

    sources = [
        SourceItem(
            chunk_id=s.chunk_id,
            text=s.text,
            score=s.score,
            language=s.language,
            metadata=s.metadata,
        )
        for s in res.sources
    ]

    t = res.timing
    timing = PipelineTimingApiResponse(
        stt_ms=t.stt_ms,
        query_preprocessing_ms=t.query_preprocessing_ms,
        query_embedding_ms=t.query_embedding_ms,
        vector_search_ms=t.vector_search_ms,
        metadata_lookup_ms=t.metadata_lookup_ms,
        retrieval_total_ms=t.retrieval_total_ms,
        answerability_check_ms=t.answerability_check_ms,
        context_build_ms=t.context_build_ms,
        llm_generation_ms=t.llm_generation_ms,
        grounding_validation_ms=t.grounding_validation_ms,
        api_overhead_ms=t.api_overhead_ms,
        total_pipeline_ms=t.total_pipeline_ms,
    )

    return VoiceQueryApiResponse(
        transcript=res.transcript,
        answer=res.answer,
        sources=sources,
        timing=timing,
        grounded=res.grounded,
        confidence_score=res.confidence_score,
    )
