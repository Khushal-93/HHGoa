import argparse
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path and stdout is utf-8
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from rag.config import FAISS_INDEX_PATH, METADATA_PATH
from rag.dataset import get_dataset_path, stream_dataset_records
from rag.embeddings import MultilingualEmbeddingModel
from rag.evaluation import RetrievalEvaluator
from rag.index import VectorIndex
from rag.retrieval import RetrievalService


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate RAG retrieval accuracy and query-time latency"
    )
    parser.add_argument(
        "--eval-records",
        type=int,
        default=500,
        help="Number of records to evaluate (default: 500)",
    )
    parser.add_argument(
        "--index-path",
        type=str,
        default=str(FAISS_INDEX_PATH),
        help="Path to FAISS index",
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default=str(METADATA_PATH),
        help="Path to metadata store",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("HHGOA — RETRIEVAL EVALUATION & BENCHMARKING")
    print("=" * 80)
    print(f"Eval Records Target : {args.eval_records}")
    print(f"Index Path          : {args.index_path}")
    print(f"Metadata Path       : {args.metadata_path}")
    print("=" * 80)

    print("\n[1/3] Loading persisted index and metadata...")
    if not Path(args.index_path).exists() or not Path(args.metadata_path).exists():
        print(f"ERROR: Index or metadata not found at {args.index_path}, {args.metadata_path}")
        print("Please run `python scripts/build_index.py` first.")
        sys.exit(1)

    t_load_start = time.perf_counter()
    index = VectorIndex.load(args.index_path, args.metadata_path)
    t_load_end = time.perf_counter()
    print(f"Index loaded in {(t_load_end - t_load_start)*1000:.2f} ms ({len(index):,} vectors).")

    print("\n[2/3] Initializing retrieval service...")
    embedder = MultilingualEmbeddingModel()
    retrieval_service = RetrievalService(embedding_model=embedder, index=index)
    evaluator = RetrievalEvaluator(retrieval_service=retrieval_service)

    print(f"\n[3/3] Streaming {args.eval_records} evaluation records and evaluating...")
    dataset_path = get_dataset_path()
    records = list(stream_dataset_records(dataset_path, max_records=args.eval_records))

    metrics = evaluator.evaluate(records, ks=[1, 3, 5, 10])

    print("\n" + "=" * 80)
    print("RETRIEVAL ACCURACY (RECALL@K)")
    print("=" * 80)
    print(f"Evaluated Queries  : {metrics.total_queries:,}")
    print(f"Recall@1           : {metrics.recall_at_1 * 100:.2f}%")
    print(f"Recall@3           : {metrics.recall_at_3 * 100:.2f}%")
    print(f"Recall@5           : {metrics.recall_at_5 * 100:.2f}%")
    print(f"Recall@10          : {metrics.recall_at_10 * 100:.2f}%")

    print("\n" + "=" * 80)
    print("LATENCY BREAKDOWN (MILLISECONDS)")
    print("=" * 80)
    print(f"{'Component':<20} | {'P50 (ms)':<10} | {'P70 (ms)':<10} | {'P100 (ms)':<10}")
    print("-" * 60)
    print(f"{'Query Embedding':<20} | {metrics.embedding_p50:<10.2f} | {metrics.embedding_p70:<10.2f} | {metrics.embedding_p100:<10.2f}")
    print(f"{'ANN Vector Search':<20} | {metrics.retrieval_p50:<10.2f} | {metrics.retrieval_p70:<10.2f} | {metrics.retrieval_p100:<10.2f}")
    print(f"{'Total Retrieval':<20} | {metrics.total_p50:<10.2f} | {metrics.total_p70:<10.2f} | {metrics.total_p100:<10.2f}")

    if metrics.language_breakdown:
        print("\n" + "=" * 80)
        print("LANGUAGE-AWARE BREAKDOWN")
        print("=" * 80)
        print(f"{'Language':<15} | {'Queries':<8} | {'Recall@5':<10} | {'P50 (ms)':<10} | {'P70 (ms)':<10} | {'P100 (ms)':<10}")
        print("-" * 75)
        for lang, l_metrics in metrics.language_breakdown.items():
            r5_pct = l_metrics['recall_at_5'] * 100
            print(f"{lang:<15} | {l_metrics['total_queries']:<8} | {r5_pct:<9.2f}% | {l_metrics['p50_ms']:<10.2f} | {l_metrics['p70_ms']:<10.2f} | {l_metrics['p100_ms']:<10.2f}")

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
