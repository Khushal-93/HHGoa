from typing import List, Tuple, Dict, Any, Optional

from rag.config import CONFIDENCE_THRESHOLD
from rag.models import Chunk, RetrievalResult, SourceCitation

REFUSAL_MESSAGE = "I couldn't find sufficient information in the provided dataset."


class AnswerabilityGate:
    """
    Calibrated evidence confidence gate.
    Evaluates top vector similarity score against threshold before calling LLM.
    Prevents hallucinations and saves latency on unanswerable/unknown queries.
    """

    def __init__(self, threshold: float = CONFIDENCE_THRESHOLD):
        self.threshold = threshold

    def evaluate(
        self,
        retrieval_results: List[RetrievalResult],
    ) -> Tuple[bool, float, str]:
        """
        Returns (is_answerable, top_score, refusal_reason).
        """
        if not retrieval_results:
            return False, 0.0, "No passages retrieved."

        top_score = retrieval_results[0].score

        if top_score < self.threshold:
            return False, top_score, f"Top confidence score ({top_score:.3f}) below threshold ({self.threshold:.3f})."

        return True, top_score, "Sufficient evidence found."


class CitationValidator:
    """
    Validates returned source chunk IDs against the retrieved context set.
    Prevents hallucinated or fabricated citations.
    """

    @staticmethod
    def validate_and_build(
        returned_source_ids: List[str],
        retrieved_results: List[RetrievalResult],
    ) -> List[SourceCitation]:
        """
        Map returned_source_ids back to valid retrieved chunks.
        If returned_source_ids is empty, default to all retrieved_results.
        Strips any hallucinated chunk IDs.
        """
        chunk_map: Dict[str, RetrievalResult] = {
            r.chunk_id: r for r in retrieved_results
        }

        citations: List[SourceCitation] = []

        if returned_source_ids:
            for cid in returned_source_ids:
                if cid in chunk_map:
                    res = chunk_map[cid]
                    citations.append(
                        SourceCitation(
                            chunk_id=res.chunk_id,
                            text=res.text,
                            score=res.score,
                            language=res.language,
                            query_id=res.query_id,
                            passage_index=res.passage_index,
                            metadata=res.metadata,
                        )
                    )
        
        # If no valid IDs found in model response, return all retrieved context
        if not citations:
            for res in retrieved_results:
                citations.append(
                    SourceCitation(
                        chunk_id=res.chunk_id,
                        text=res.text,
                        score=res.score,
                        language=res.language,
                        query_id=res.query_id,
                        passage_index=res.passage_index,
                        metadata=res.metadata,
                    )
                )

        return citations
