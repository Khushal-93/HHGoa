import pytest
from fastapi.testclient import TestClient
from rag.api import app, retrieval_service
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.models import Chunk
from rag.retrieval import RetrievalService


@pytest.fixture
def client():
    # Setup mock index for API testing
    embedder = MultilingualEmbeddingModel()
    dim = embedder.get_dimension()
    index = VectorIndex(dimension=dim)

    chunks = [
        Chunk(
            chunk_id="999:0:0",
            query_id=999,
            passage_index=0,
            text="FastAPI is a modern web framework for Python.",
            english_text="FastAPI is a modern web framework for Python.",
            is_selected=True,
            strategy="passage_preserving",
            chunk_index=0,
        )
    ]
    embeddings = embedder.embed_documents([c.text for c in chunks])
    index.add_embeddings(embeddings, chunks)
    test_service = RetrievalService(embedding_model=embedder, index=index)

    # Enter context (lifespan runs and sets global retrieval_service)
    with TestClient(app) as test_client:
        # Override AFTER lifespan has run so we have a pre-loaded test index
        import rag.api
        rag.api.retrieval_service = test_service
        yield test_client


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["index_loaded"] is True
    assert data["indexed_chunks"] == 1


def test_retrieve_endpoint(client):
    payload = {"query": "Tell me about FastAPI framework", "top_k": 1}
    res = client.post("/api/retrieve", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert "results" in data
    assert "timing" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["chunk_id"] == "999:0:0"
    assert data["timing"]["total_ms"] > 0


def test_retrieve_empty_query(client):
    payload = {"query": "   ", "top_k": 1}
    res = client.post("/api/retrieve", json=payload)
    assert res.status_code == 400
