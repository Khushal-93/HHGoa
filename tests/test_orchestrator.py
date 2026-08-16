import numpy as np
import pytest

from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.models import Chunk
from rag.orchestrator import RAGOrchestrator
from rag.retrieval import RetrievalService


@pytest.fixture
def orchestrator():
    embedder = MultilingualEmbeddingModel()
    dim = embedder.get_dimension()
    index = VectorIndex(dimension=dim)

    chunks = [
        Chunk(
            chunk_id="201:0:0",
            query_id=201,
            passage_index=0,
            text="A corporation is a legal entity separate from its owners.",
            english_text="A corporation is a legal entity separate from its owners.",
            is_selected=True,
            strategy="passage_preserving",
            chunk_index=0,
        )
    ]
    embeddings = embedder.embed_documents([c.text for c in chunks])
    index.add_embeddings(embeddings, chunks)

    ret_service = RetrievalService(embedding_model=embedder, index=index)
    return RAGOrchestrator(retrieval_service=ret_service)


def test_text_pipeline_answerable(orchestrator):
    res = orchestrator.run_text_pipeline("What is a corporation?")

    assert res.grounded is True
    assert len(res.answer) > 0
    assert len(res.sources) == 1
    assert res.sources[0].chunk_id == "201:0:0"

    t = res.timing
    assert t.query_embedding_ms > 0
    assert t.total_pipeline_ms > 0


def test_text_pipeline_unanswerable(orchestrator):
    res = orchestrator.run_text_pipeline("Random unrelated astronomy query about black holes")

    assert res.grounded is False
    assert "couldn't find" in res.answer.lower()
    assert res.sources == []


def test_voice_pipeline(orchestrator):
    audio_bytes = "What is a corporation?".encode("utf-8")
    res = orchestrator.run_voice_pipeline(audio_bytes, allow_mock=True)

    assert res.transcript == "What is a corporation?"
    assert res.grounded is True
    assert res.timing.stt_ms >= 0.0
    assert res.timing.total_pipeline_ms > 0
