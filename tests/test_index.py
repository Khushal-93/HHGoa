import numpy as np
import pytest
from rag.index import VectorIndex
from rag.models import Chunk


def make_sample_chunk(chunk_id="123:0:0", text="Sample passage"):
    return Chunk(
        chunk_id=chunk_id,
        query_id=123,
        passage_index=0,
        text=text,
        english_text="English text",
        is_selected=True,
        strategy="passage_preserving",
        chunk_index=0,
    )


def test_index_build_and_search():
    dim = 384
    index = VectorIndex(dimension=dim)

    # 3 random normalized vectors
    vecs = np.random.randn(3, dim).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)

    chunks = [
        make_sample_chunk(f"chunk_{i}", f"Text {i}")
        for i in range(3)
    ]

    index.add_embeddings(vecs, chunks)
    assert len(index) == 3

    # Search using first vector as query
    scores, retrieved_chunks = index.search(vecs[0], top_k=2)

    assert len(scores) == 2
    assert len(retrieved_chunks) == 2
    assert retrieved_chunks[0].chunk_id == "chunk_0"
    assert pytest.approx(scores[0], abs=1e-3) == 1.0


def test_index_save_and_load(tmp_path):
    dim = 384
    index = VectorIndex(dimension=dim)

    vecs = np.random.randn(2, dim).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    chunks = [make_sample_chunk("c1", "Text 1"), make_sample_chunk("c2", "Text 2")]

    index.add_embeddings(vecs, chunks)

    idx_file = tmp_path / "test.faiss"
    meta_file = tmp_path / "test.pkl"

    index.save(idx_file, meta_file)

    loaded_index = VectorIndex.load(idx_file, meta_file)
    assert len(loaded_index) == 2

    scores, res_chunks = loaded_index.search(vecs[1], top_k=1)
    assert res_chunks[0].chunk_id == "c2"
