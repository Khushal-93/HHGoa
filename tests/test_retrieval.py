import numpy as np
import pytest

from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.models import Chunk
from rag.retrieval import RetrievalService


@pytest.fixture
def mock_retrieval_service():
    embedder = MultilingualEmbeddingModel()
    dim = embedder.get_dimension()

    index = VectorIndex(dimension=dim)
    chunks = [
        Chunk(
            chunk_id="101:0:0",
            query_id=101,
            passage_index=0,
            text="Corporations operate under state law.",
            english_text="Corporations operate under state law.",
            is_selected=True,
            strategy="passage_preserving",
            chunk_index=0,
        ),
        Chunk(
            chunk_id="102:0:0",
            query_id=102,
            passage_index=0,
            text="Photosynthesis converts light into chemical energy.",
            english_text="Photosynthesis converts light into chemical energy.",
            is_selected=True,
            strategy="passage_preserving",
            chunk_index=0,
        ),
    ]

    embeddings = embedder.embed_documents([c.text for c in chunks])
    index.add_embeddings(embeddings, chunks)

    return RetrievalService(embedding_model=embedder, index=index)


def test_retrieval_service_flow(mock_retrieval_service):
    response = mock_retrieval_service.retrieve("What is a corporation?", top_k=2)

    assert len(response.results) == 2
    assert response.results[0].chunk_id == "101:0:0"
    assert response.results[0].score > response.results[1].score

    # Verify timing info
    timing = response.timing
    assert timing.embedding_ms > 0
    assert timing.retrieval_ms >= 0
    assert timing.total_ms > 0


def test_empty_index_retrieval():
    service = RetrievalService()
    response = service.retrieve("Query test")

    assert response.results == []
    assert response.timing.total_ms == 0.0
