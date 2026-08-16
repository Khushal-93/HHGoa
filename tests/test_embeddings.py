import numpy as np
import pytest
from rag.embeddings import MultilingualEmbeddingModel


@pytest.fixture
def embedder():
    return MultilingualEmbeddingModel()


def test_embed_query(embedder):
    query = "What is a corporation?"
    vector = embedder.embed_query(query)

    assert isinstance(vector, np.ndarray)
    assert vector.dtype == np.float32
    assert vector.ndim == 1
    assert vector.shape[0] == embedder.get_dimension()

    # Check normalization (L2 norm approx 1.0)
    norm = np.linalg.norm(vector)
    assert pytest.approx(norm, abs=1e-3) == 1.0


def test_embed_documents(embedder):
    docs = [
        "A corporation is a legal entity created by individuals.",
        "यह एक परीक्षण वाक्य है।",
    ]
    vectors = embedder.embed_documents(docs, batch_size=2)

    assert isinstance(vectors, np.ndarray)
    assert vectors.shape == (2, embedder.get_dimension())

    for row in vectors:
        norm = np.linalg.norm(row)
        assert pytest.approx(norm, abs=1e-3) == 1.0


def test_embed_empty(embedder):
    empty_queries = embedder.embed_queries([])
    assert empty_queries.shape == (0, embedder.get_dimension())

    empty_docs = embedder.embed_documents([])
    assert empty_docs.shape == (0, embedder.get_dimension())
