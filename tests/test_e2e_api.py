import pytest
from fastapi.testclient import TestClient
from rag.api import app
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.models import Chunk
from rag.orchestrator import RAGOrchestrator
from rag.retrieval import RetrievalService


@pytest.fixture
def client():
    embedder = MultilingualEmbeddingModel()
    dim = embedder.get_dimension()
    index = VectorIndex(dimension=dim)

    chunks = [
        Chunk(
            chunk_id="301:0:0",
            query_id=301,
            passage_index=0,
            text="Corporate taxes are levied on business income.",
            english_text="Corporate taxes are levied on business income.",
            is_selected=True,
            strategy="passage_preserving",
            chunk_index=0,
        )
    ]
    embeddings = embedder.embed_documents([c.text for c in chunks])
    index.add_embeddings(embeddings, chunks)

    ret_service = RetrievalService(embedding_model=embedder, index=index)
    test_orchestrator = RAGOrchestrator(retrieval_service=ret_service)

    with TestClient(app) as test_client:
        import rag.api
        rag.api.retrieval_service = ret_service
        rag.api.orchestrator = test_orchestrator
        yield test_client


def test_api_text_query(client):
    payload = {"query": "Tell me about corporate taxes"}
    res = client.post("/api/query", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert "answer" in data
    assert "sources" in data
    assert "timing" in data
    assert data["grounded"] is True
    assert data["timing"]["total_pipeline_ms"] > 0


def test_api_voice_ask(client):
    files = {"file": ("test.wav", b"Tell me about corporate taxes", "audio/wav")}
    res = client.post("/api/voice/ask", files=files, data={"language": "hin_Deva"})
    assert res.status_code == 200

    data = res.json()
    assert "transcript" in data
    assert "answer" in data
    assert data["grounded"] is True
    assert data["timing"]["stt_ms"] >= 0.0
