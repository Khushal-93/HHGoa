"""
HHGoa — Owner-Style Retrieval Latency Benchmark
Adapted reference benchmark methodology for HHGoa RAG architecture.

Measures:
  query -> query embedding -> FAISS retrieval -> total retrieval latency

Usage:
  python scripts/benchmark_owner_style.py [n_queries] [--budget-ms 50] [--top-k 5]
"""
import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import List

# Ensure project root in sys.path and configure utf-8 encoding
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from rag.config import PROCESSED_DATA_DIR, EMBEDDING_DIM
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.retrieval import RetrievalService

# Full 360,967-vector index default paths
DEFAULT_INDEX_PATH = PROCESSED_DATA_DIR / "faiss_index_full.faiss"
DEFAULT_META_PATH = PROCESSED_DATA_DIR / "metadata_full.pkl"
DEFAULT_OUT_JSON = PROCESSED_DATA_DIR / "owner_style_benchmark.json"

# Owner reference queries + bilingual MSMARCO-XI representative queries
REFERENCE_QUERIES = [
    # Owner reference queries
    "What is FAISS used for?",
    "How does HNSW indexing work?",
    "What is retrieval augmented generation?",
    "Which embedding model is fast on CPU?",
    "How do you reduce RAG latency?",
    "What does efSearch control?",
    "Why normalize embeddings before indexing?",
    "What are the stages of a RAG pipeline?",
    # Representative Hindi domain queries
    "कॉर्पोरेशन क्या है?",
    "कंपनी कानून के अंतर्गत कॉर्पोरेशन की क्या परिभाषा है?",
    "निगम के अधिकार और जिम्मेदारियां क्या हैं?",
    "व्यापार और व्यापारिक निगम क्या है?",
]


def percentile(values: List[float], pct: float) -> float:
    """Calculate percentile with linear interpolation matching reference benchmark."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f, c = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    return float(sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f]))


def run_benchmark(
    index_path: Path,
    meta_path: Path,
    n_queries: int = 50,
    top_k: int = 5,
    budget_ms: float = 50.0,
    warmup_passes: int = 5,
    out_json: Path = None,
) -> dict:
    print("=" * 80)
    print("HHGOA — OWNER-STYLE RETRIEVAL LATENCY BENCHMARK (ADAPTED)")
    print("=" * 80)

    # 1. Verification of Index Files
    if not index_path.exists() or not meta_path.exists():
        raise FileNotFoundError(
            f"Index or metadata file not found at:\n  Index: {index_path}\n  Meta: {meta_path}"
        )

    print(f"  Index File   : {index_path.name} ({index_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  Meta File    : {meta_path.name} ({meta_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  Query Count  : {n_queries}")
    print(f"  Top-K        : {top_k}")
    print(f"  Budget (Ref) : {budget_ms} ms")
    print(f"  Task 2 Req   : <200 ms (Post-STT)")

    # 2. Loading Engine (excluded from query measurements)
    print("\n[1/3] Loading Embedding Model & Vector Index (Excluded from timing)...")
    t_load_start = time.perf_counter()
    embedder = MultilingualEmbeddingModel()
    index = VectorIndex.load(str(index_path), str(meta_path))
    retrieval_service = RetrievalService(embedding_model=embedder, index=index)
    t_load_end = time.perf_counter()

    vector_count = len(index)
    meta_count = len(index.chunks)
    print(f"  Embedding Backend  : {'ONNX Runtime (Fast)' if embedder.using_onnx else 'PyTorch'}")
    print(f"  Indexed Vectors    : {vector_count:,}")
    print(f"  Metadata Chunks    : {meta_count:,}")
    print(f"  Embedding Dim      : {index.index.d} (expected {EMBEDDING_DIM})")
    print(f"  Cold Load Duration : {(t_load_end - t_load_start):.2f} s")

    # 3. Warm-up (excluded from timing)
    print(f"\n[2/3] Warming up ({warmup_passes} passes, excluded from timing)...")
    for i in range(warmup_passes):
        warmup_q = REFERENCE_QUERIES[i % len(REFERENCE_QUERIES)]
        retrieval_service.retrieve(warmup_q, top_k=top_k)
    print("  Warm-up complete.")

    # 4. Latency Measurements
    print(f"\n[3/3] Running {n_queries} retrieval queries...")
    embed_ms_list: List[float] = []
    search_ms_list: List[float] = []
    total_ms_list: List[float] = []

    for i in range(n_queries):
        query = REFERENCE_QUERIES[i % len(REFERENCE_QUERIES)]
        resp = retrieval_service.retrieve(query=query, top_k=top_k)
        embed_ms_list.append(resp.timing.embedding_ms)
        search_ms_list.append(resp.timing.retrieval_ms)
        total_ms_list.append(resp.timing.total_ms)

    # 5. Summary Statistics
    results = {
        "embed": {
            "avg": round(statistics.mean(embed_ms_list), 2),
            "p50": round(percentile(embed_ms_list, 50), 2),
            "p95": round(percentile(embed_ms_list, 95), 2),
            "p99": round(percentile(embed_ms_list, 99), 2),
        },
        "search": {
            "avg": round(statistics.mean(search_ms_list), 2),
            "p50": round(percentile(search_ms_list, 50), 2),
            "p95": round(percentile(search_ms_list, 95), 2),
            "p99": round(percentile(search_ms_list, 99), 2),
        },
        "total": {
            "avg": round(statistics.mean(total_ms_list), 2),
            "p50": round(percentile(total_ms_list, 50), 2),
            "p95": round(percentile(total_ms_list, 95), 2),
            "p99": round(percentile(total_ms_list, 99), 2),
            "max": round(max(total_ms_list), 2),
        },
    }

    # 6. Output Table
    print(f"\nRan {n_queries} queries (Index: {vector_count:,} vectors, top_k={top_k})\n")
    print(f"{'stage':<12}{'avg':>8}{'p50':>8}{'p95':>8}{'p99':>8}   (ms)")
    for name in ["embed", "search", "total"]:
        r = results[name]
        print(
            f"{name:<12}"
            f"{r['avg']:>8.2f}"
            f"{r['p50']:>8.2f}"
            f"{r['p95']:>8.2f}"
            f"{r['p99']:>8.2f}"
        )

    p95_total = results["total"]["p95"]
    print(f"\nOwner Reference Budget : {budget_ms}ms | P95 total: {p95_total:.2f}ms")
    if p95_total <= budget_ms:
        print("  Owner Budget Verdict : PASS (within 50ms reference budget)")
    else:
        print(f"  Owner Budget Verdict : OVER BUDGET (by {p95_total - budget_ms:.2f}ms)")

    task2_req_ms = 200.0
    p100_total = results["total"]["max"]
    print(f"Task 2 Post-STT Req    : <{task2_req_ms}ms | P100 total: {p100_total:.2f}ms")
    if p100_total < task2_req_ms:
        print(f"  Task 2 Basic Verdict : PASS (<{task2_req_ms}ms post-STT)")
    else:
        print(f"  Task 2 Basic Verdict : EXCEEDS (<{task2_req_ms}ms, max={p100_total:.2f}ms)")

    report_payload = {
        "benchmark": "HHGoa Owner-Style Retrieval Latency Benchmark",
        "index_path": str(index_path),
        "vector_count": vector_count,
        "metadata_count": meta_count,
        "n_queries": n_queries,
        "top_k": top_k,
        "budget_ms": budget_ms,
        "warmup_passes": warmup_passes,
        "results": results,
        "raw_total_latencies_ms": total_ms_list,
    }

    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2)
        print(f"\nReport saved to: {out_json}")

    print("=" * 80)
    return report_payload


def main():
    parser = argparse.ArgumentParser(description="HHGoa Owner-Style Retrieval Latency Benchmark")
    parser.add_argument("n_queries", type=int, nargs="?", default=50, help="Number of benchmark queries")
    parser.add_argument("--index-path", type=str, default=str(DEFAULT_INDEX_PATH), help="Path to FAISS index")
    parser.add_argument("--meta-path", type=str, default=str(DEFAULT_META_PATH), help="Path to metadata pickle")
    parser.add_argument("--top-k", type=int, default=5, help="Number of nearest chunks to retrieve")
    parser.add_argument("--budget-ms", type=float, default=50.0, help="Owner reference latency budget in ms")
    parser.add_argument("--warmup", type=int, default=5, help="Number of warmup queries before timing")
    parser.add_argument("--out-json", type=str, default=str(DEFAULT_OUT_JSON), help="Output JSON path")
    args = parser.parse_args()

    run_benchmark(
        index_path=Path(args.index_path),
        meta_path=Path(args.meta_path),
        n_queries=args.n_queries,
        top_k=args.top_k,
        budget_ms=args.budget_ms,
        warmup_passes=args.warmup,
        out_json=Path(args.out_json) if args.out_json else None,
    )


if __name__ == "__main__":
    main()
