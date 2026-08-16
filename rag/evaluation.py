import time
from typing import List, Dict, Any, Optional
import numpy as np

from rag.models import DatasetRecord, EvaluationMetrics
from rag.retrieval import RetrievalService


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate the given percentile (0 to 100) of a list of float values.
    Returns 0.0 for empty list.
    """
    if not values:
        return 0.0
    return float(np.percentile(values, percentile))


class RetrievalEvaluator:
    """
    Reproducible retrieval evaluator for measuring Recall@K (K=1, 3, 5, 10),
    P50/P70/P100 latency percentiles, and per-language metrics.
    """

    def __init__(self, retrieval_service: RetrievalService):
        self.retrieval_service = retrieval_service

    def evaluate(
        self,
        records: List[DatasetRecord],
        ks: List[int] = [1, 3, 5, 10],
    ) -> EvaluationMetrics:
        """
        Evaluate the retrieval service across a set of DatasetRecords.
        """
        if not records:
            return EvaluationMetrics(
                total_queries=0,
                recall_at_1=0.0,
                recall_at_3=0.0,
                recall_at_5=0.0,
                recall_at_10=0.0,
                embedding_p50=0.0,
                embedding_p70=0.0,
                embedding_p100=0.0,
                retrieval_p50=0.0,
                retrieval_p70=0.0,
                retrieval_p100=0.0,
                total_p50=0.0,
                total_p70=0.0,
                total_p100=0.0,
                language_breakdown={},
            )

        max_k = max(ks)
        evaluable_records = [
            r for r in records
            if any(p.is_selected for p in r.passages)
        ]

        if not evaluable_records:
            evaluable_records = records

        hits_at_k: Dict[int, int] = {k: 0 for k in ks}

        embedding_latencies: List[float] = []
        retrieval_latencies: List[float] = []
        total_latencies: List[float] = []

        # Per-language tracking
        lang_data: Dict[str, Dict[str, Any]] = {}

        for record in evaluable_records:
            query_text = record.query if record.query and record.query.strip() else record.english_query
            if not query_text or not query_text.strip():
                continue

            target_lang = record.target_lang or "unknown"
            if target_lang not in lang_data:
                lang_data[target_lang] = {
                    "total": 0,
                    "hits_5": 0,
                    "latencies": [],
                }

            # Retrieve top max_k
            response = self.retrieval_service.retrieve(
                query=query_text,
                top_k=max_k,
                target_lang=target_lang,
            )

            # Record latencies
            embedding_latencies.append(response.timing.embedding_ms)
            retrieval_latencies.append(response.timing.retrieval_ms)
            total_latencies.append(response.timing.total_ms)

            lang_data[target_lang]["latencies"].append(response.timing.total_ms)
            lang_data[target_lang]["total"] += 1

            # Determine ground truth selected passage indices for this query_id
            ground_truth_passages = {
                p.passage_index for p in record.passages if p.is_selected
            }

            # Check top-K hits
            # A result is a hit if query_id matches AND passage_index is in ground truth selected
            retrieved_passage_indices = [
                res.passage_index
                for res in response.results
                if res.query_id == record.query_id
            ]

            # Check hits for each K
            for k in ks:
                top_k_passages = retrieved_passage_indices[:k]
                if any(idx in ground_truth_passages for idx in top_k_passages):
                    hits_at_k[k] += 1
                    if k == 5:
                        lang_data[target_lang]["hits_5"] += 1

        total_q = len(evaluable_records) if evaluable_records else 1

        recall_at_1 = hits_at_k.get(1, 0) / total_q
        recall_at_3 = hits_at_k.get(3, 0) / total_q
        recall_at_5 = hits_at_k.get(5, 0) / total_q
        recall_at_10 = hits_at_k.get(10, 0) / total_q

        # Language breakdown metrics
        language_breakdown = {}
        for lang, d in lang_data.items():
            tot = d["total"] if d["total"] > 0 else 1
            lats = d["latencies"]
            language_breakdown[lang] = {
                "total_queries": d["total"],
                "recall_at_5": round(d["hits_5"] / tot, 4),
                "p50_ms": round(calculate_percentile(lats, 50), 3),
                "p70_ms": round(calculate_percentile(lats, 70), 3),
                "p100_ms": round(calculate_percentile(lats, 100), 3),
            }

        return EvaluationMetrics(
            total_queries=len(evaluable_records),
            recall_at_1=round(recall_at_1, 4),
            recall_at_3=round(recall_at_3, 4),
            recall_at_5=round(recall_at_5, 4),
            recall_at_10=round(recall_at_10, 4),
            embedding_p50=round(calculate_percentile(embedding_latencies, 50), 3),
            embedding_p70=round(calculate_percentile(embedding_latencies, 70), 3),
            embedding_p100=round(calculate_percentile(embedding_latencies, 100), 3),
            retrieval_p50=round(calculate_percentile(retrieval_latencies, 50), 3),
            retrieval_p70=round(calculate_percentile(retrieval_latencies, 70), 3),
            retrieval_p100=round(calculate_percentile(retrieval_latencies, 100), 3),
            total_p50=round(calculate_percentile(total_latencies, 50), 3),
            total_p70=round(calculate_percentile(total_latencies, 70), 3),
            total_p100=round(calculate_percentile(total_latencies, 100), 3),
            language_breakdown=language_breakdown,
        )
