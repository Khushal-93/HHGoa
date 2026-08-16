import pytest
from rag.evaluation import calculate_percentile, RetrievalEvaluator
from rag.models import DatasetRecord, Passage, Chunk
from rag.index import VectorIndex
from rag.embeddings import MultilingualEmbeddingModel
from rag.retrieval import RetrievalService


def test_calculate_percentile():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    p50 = calculate_percentile(values, 50)
    assert p50 == 30.0

    p100 = calculate_percentile(values, 100)
    assert p100 == 50.0

    assert calculate_percentile([], 50) == 0.0


def test_evaluator_flow():
    embedder = MultilingualEmbeddingModel()
    dim = embedder.get_dimension()
    index = VectorIndex(dimension=dim)

    chunks = [
        Chunk(
            chunk_id="500:0:0",
            query_id=500,
            passage_index=0,
            text="Python is a programming language.",
            english_text="Python is a programming language.",
            is_selected=True,
            strategy="passage_preserving",
            chunk_index=0,
        )
    ]
    vecs = embedder.embed_documents([c.text for c in chunks])
    index.add_embeddings(vecs, chunks)

    service = RetrievalService(embedding_model=embedder, index=index)
    evaluator = RetrievalEvaluator(service)

    records = [
        DatasetRecord(
            query_id=500,
            query="What is Python?",
            english_query="What is Python?",
            answer="A programming language.",
            english_answer="A programming language.",
            query_type="DESCRIPTION",
            source_lang="eng_Latn",
            target_lang="eng_Latn",
            passages=[
                Passage(
                    passage_index=0,
                    text="Python is a programming language.",
                    english_text="Python is a programming language.",
                    is_selected=True,
                )
            ],
        )
    ]

    metrics = evaluator.evaluate(records, ks=[1, 3, 5, 10])

    assert metrics.total_queries == 1
    assert metrics.recall_at_1 == 1.0
    assert metrics.recall_at_5 == 1.0
    assert metrics.total_p50 > 0
    assert "eng_Latn" in metrics.language_breakdown
