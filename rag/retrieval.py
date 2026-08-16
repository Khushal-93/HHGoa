import time
from typing import List, Optional

from rag.config import DEFAULT_TOP_K
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.models import (
    RetrievalResponse,
    RetrievalResult,
    TimingInfo,
)


class RetrievalService:
    """
    High-performance vector retrieval engine with high-resolution monotonic latency tracking.
    """

    def __init__(
        self,
        embedding_model: Optional[MultilingualEmbeddingModel] = None,
        index: Optional[VectorIndex] = None,
    ):
        self.embedding_model = (
            embedding_model if embedding_model is not None else MultilingualEmbeddingModel()
        )
        self.index = index

    def set_index(self, index: VectorIndex) -> None:
        self.index = index

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        target_lang: str = "hin_Deva",
    ) -> RetrievalResponse:
        """
        Execute query-time retrieval:
        query -> query embedding -> ANN search -> candidate metadata lookup -> response with timing metrics.
        """
        if self.index is None or len(self.index) == 0:
            return RetrievalResponse(
                results=[],
                timing=TimingInfo(
                    embedding_ms=0.0,
                    retrieval_ms=0.0,
                    metadata_lookup_ms=0.0,
                    total_ms=0.0,
                ),
            )

        t_total_start = time.perf_counter()

        # Step 1: Query Embedding
        t_emb_start = time.perf_counter()
        query_vector = self.embedding_model.embed_query(query)
        t_emb_end = time.perf_counter()
        embedding_ms = (t_emb_end - t_emb_start) * 1000.0

        # Step 2: Vector Search
        t_search_start = time.perf_counter()
        scores, chunks = self.index.search(query_vector, top_k=top_k)
        t_search_end = time.perf_counter()
        retrieval_ms = (t_search_end - t_search_start) * 1000.0

        # Step 3: Metadata Resolution
        t_meta_start = time.perf_counter()
        results: List[RetrievalResult] = []

        for score, chunk in zip(scores, chunks):
            results.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=float(score),
                    language=target_lang,
                    query_id=chunk.query_id,
                    passage_index=chunk.passage_index,
                    is_selected=chunk.is_selected,
                    strategy=chunk.strategy,
                    metadata=chunk.metadata,
                )
            )

        t_meta_end = time.perf_counter()
        metadata_lookup_ms = (t_meta_end - t_meta_start) * 1000.0

        t_total_end = time.perf_counter()
        total_ms = (t_total_end - t_total_start) * 1000.0

        return RetrievalResponse(
            results=results,
            timing=TimingInfo(
                embedding_ms=round(embedding_ms, 3),
                retrieval_ms=round(retrieval_ms, 3),
                metadata_lookup_ms=round(metadata_lookup_ms, 3),
                total_ms=round(total_ms, 3),
            ),
        )
