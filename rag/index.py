import os
import pickle
from pathlib import Path
from typing import List, Tuple, Union
import faiss
import numpy as np

from rag.config import EMBEDDING_DIM, FAISS_INDEX_PATH, METADATA_PATH
from rag.models import Chunk


class VectorIndex:
    """
    In-process FAISS vector index manager using IndexFlatIP (dot product cosine search on normalized vectors).
    Maintains synchronized list of Chunk metadata objects for sub-millisecond retrieval.
    """

    def __init__(self, dimension: int = EMBEDDING_DIM):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks: List[Chunk] = []

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        chunks: List[Chunk],
    ) -> None:
        """
        Add normalized embeddings and corresponding Chunk objects to the index.
        """
        if len(embeddings) != len(chunks):
            raise ValueError(
                f"Mismatch: {len(embeddings)} embeddings vs {len(chunks)} chunks"
            )

        if len(embeddings) == 0:
            return

        embeddings_f32 = np.ascontiguousarray(embeddings, dtype=np.float32)

        # Normalize if not already unit length
        faiss.normalize_L2(embeddings_f32)

        self.index.add(embeddings_f32)
        self.chunks.extend(chunks)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> Tuple[List[float], List[Chunk]]:
        """
        Search top_k nearest vectors for a given query embedding.
        query_embedding shape can be (dim,) or (1, dim).
        Returns tuple of (scores, chunks).
        """
        if self.index.ntotal == 0:
            return [], []

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        q_f32 = np.ascontiguousarray(query_embedding, dtype=np.float32)
        faiss.normalize_L2(q_f32)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q_f32, k)

        retrieved_scores = []
        retrieved_chunks = []

        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.chunks):
                retrieved_scores.append(float(score))
                retrieved_chunks.append(self.chunks[idx])

        return retrieved_scores, retrieved_chunks

    def save(
        self,
        index_path: Union[str, Path] = FAISS_INDEX_PATH,
        metadata_path: Union[str, Path] = METADATA_PATH,
    ) -> None:
        """
        Persist the FAISS index and metadata store to disk.
        """
        index_path = Path(index_path)
        metadata_path = Path(metadata_path)

        index_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_path))

        with open(metadata_path, "wb") as f:
            pickle.dump(self.chunks, f)

    @classmethod
    def load(
        cls,
        index_path: Union[str, Path] = FAISS_INDEX_PATH,
        metadata_path: Union[str, Path] = METADATA_PATH,
    ) -> "VectorIndex":
        """
        Load a persisted FAISS index and metadata store from disk.
        """
        index_path = Path(index_path)
        metadata_path = Path(metadata_path)

        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"Index or metadata path does not exist: {index_path}, {metadata_path}"
            )

        faiss_idx = faiss.read_index(str(index_path))
        dimension = faiss_idx.d

        if hasattr(faiss_idx, "hnsw"):
            faiss_idx.hnsw.efSearch = 128

        obj = cls(dimension=dimension)
        obj.index = faiss_idx

        with open(metadata_path, "rb") as f:
            obj.chunks = pickle.load(f)

        return obj

    def __len__(self) -> int:
        return self.index.ntotal
