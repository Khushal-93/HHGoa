from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from rag.config import (
    EMBEDDING_MODEL_NAME,
    QUERY_PREFIX,
    PASSAGE_PREFIX,
    DEVICE,
    BATCH_SIZE,
)


class MultilingualEmbeddingModel:
    """
    Wrapper around SentenceTransformers for low-latency multilingual retrieval.
    Prepend query: and passage: prefixes required for E5-style models.
    Returns L2-normalized embeddings for cosine similarity.
    """

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL_NAME,
        device: str = DEVICE,
    ):
        self.model_name = model_name
        self.device = device
        self.query_prefix = QUERY_PREFIX
        self.passage_prefix = PASSAGE_PREFIX
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )
        return self._model

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single text query with the query prefix.
        Returns a 1D float32 numpy array of shape (dim,).
        """
        text = f"{self.query_prefix}{query}" if query else self.query_prefix
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embedding.astype(np.float32)

    def embed_queries(
        self,
        queries: List[str],
        batch_size: int = BATCH_SIZE,
    ) -> np.ndarray:
        """
        Embed a list of text queries in batches.
        Returns a 2D float32 numpy array of shape (N, dim).
        """
        if not queries:
            return np.empty((0, self.get_dimension()), dtype=np.float32)

        prefixed_queries = [
            f"{self.query_prefix}{q}" if q else self.query_prefix for q in queries
        ]
        embeddings = self.model.encode(
            prefixed_queries,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def embed_documents(
        self,
        documents: List[str],
        batch_size: int = BATCH_SIZE,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """
        Embed a list of document passages in batches with passage prefix.
        Returns a 2D float32 numpy array of shape (N, dim).
        """
        if not documents:
            return np.empty((0, self.get_dimension()), dtype=np.float32)

        prefixed_docs = [
            f"{self.passage_prefix}{doc}" if doc else self.passage_prefix
            for doc in documents
        ]
        embeddings = self.model.encode(
            prefixed_docs,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def get_dimension(self) -> int:
        """
        Return the embedding dimension without triggering a tokenizer download.
        SentenceTransformers v5+ lazy-loads the tokenizer on first encode();
        reading the transformer config attribute is instant.
        """
        # Fast path: read directly from the underlying transformer config
        try:
            first = self.model._first_module()
            if hasattr(first, "config") and hasattr(first.config, "hidden_size"):
                return first.config.hidden_size
        except Exception:
            pass

        # Use the ST API if available (may trigger tokenizer load in older versions)
        if hasattr(self.model, "get_embedding_dimension"):
            return self.model.get_embedding_dimension()
        return self.model.get_sentence_embedding_dimension()
