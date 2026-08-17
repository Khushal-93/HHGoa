"""
HHGoa — Isolated FAISS ANN Experiments for Full Corpus (360,967 vectors)

Evaluates:
  1. IndexFlatIP (Current Baseline)
  2. IndexHNSWFlat (M in [16, 32, 64], efSearch in [32, 64, 128])
  3. IndexIVFFlat (nlist in [1024, 2048], nprobe in [8, 16, 32, 64])

Metrics:
  - Build Time (s)
  - Index Size (MB)
  - FAISS Latency (P50, P95, P99, P100 ms)
  - Total Retrieval Latency (P50, P95, P99, P100 ms)
  - Recall@1, Recall@5, Recall@10
"""
import json
import os
import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from rag.config import PROCESSED_DATA_DIR, EMBEDDING_DIM
from rag.dataset import get_dataset_path, stream_dataset_records
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.retrieval import RetrievalService

FULL_INDEX_PATH = PROCESSED_DATA_DIR / "faiss_index_full.faiss"
FULL_META_PATH = PROCESSED_DATA_DIR / "metadata_full.pkl"
EXP_DIR = PROCESSED_DATA_DIR / "experiments"
EXP_REPORT_PATH = EXP_DIR / "ann_experiment_results.json"

REFERENCE_QUERIES = [
    "What is FAISS used for?",
    "How does HNSW indexing work?",
    "What is retrieval augmented generation?",
    "Which embedding model is fast on CPU?",
    "How do you reduce RAG latency?",
    "What does efSearch control?",
    "Why normalize embeddings before indexing?",
    "What are the stages of a RAG pipeline?",
    "कॉर्पोरेशन क्या है?",
    "कंपनी कानून के अंतर्गत कॉर्पोरेशन की क्या परिभाषा है?",
    "निगम के अधिकार और जिम्मेदारियां क्या हैं?",
    "व्यापार और व्यापारिक निगम क्या है?",
]


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f, c = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    return float(sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f]))


def load_eval_records(indexed_qids: set, sample_limit: int = 1500) -> List[Any]:
    dataset_path = get_dataset_path()
    evaluable = []
    for r in stream_dataset_records(dataset_path):
        if any(psg.is_selected for psg in r.passages) and r.query_id in indexed_qids:
            evaluable.append(r)
            if len(evaluable) >= sample_limit:
                break
    return evaluable


def evaluate_recall(
    index_wrapper: VectorIndex,
    eval_records: List[Any],
    embedder: MultilingualEmbeddingModel,
    ks: List[int] = [1, 5, 10],
) -> Dict[str, float]:
    ret_svc = RetrievalService(embedding_model=embedder, index=index_wrapper)
    max_k = max(ks)
    hits = {k: 0 for k in ks}
    total = 0

    for rec in eval_records:
        q = rec.query.strip() if rec.query and rec.query.strip() else rec.english_query.strip()
        if not q:
            continue
        gt = {psg.passage_index for psg in rec.passages if psg.is_selected}
        resp = ret_svc.retrieve(query=q, top_k=max_k)
        retrieved = [r.passage_index for r in resp.results if r.query_id == rec.query_id]
        for k in ks:
            if any(idx in gt for idx in retrieved[:k]):
                hits[k] += 1
        total += 1

    if total == 0:
        return {f"recall@{k}": 0.0 for k in ks}
    return {f"recall@{k}": round(hits[k] / total, 4) for k in ks}


def benchmark_latency(
    index_wrapper: VectorIndex,
    embedder: MultilingualEmbeddingModel,
    n_queries: int = 100,
    top_k: int = 5,
    warmup: int = 5,
) -> Dict[str, Any]:
    ret_svc = RetrievalService(embedding_model=embedder, index=index_wrapper)

    # Warmup
    for i in range(warmup):
        q = REFERENCE_QUERIES[i % len(REFERENCE_QUERIES)]
        ret_svc.retrieve(q, top_k=top_k)

    embed_ms_l, faiss_ms_l, total_ms_l = [], [], []
    for i in range(n_queries):
        q = REFERENCE_QUERIES[i % len(REFERENCE_QUERIES)]
        resp = ret_svc.retrieve(q, top_k=top_k)
        embed_ms_l.append(resp.timing.embedding_ms)
        faiss_ms_l.append(resp.timing.retrieval_ms)
        total_ms_l.append(resp.timing.total_ms)

    return {
        "faiss_p50": round(percentile(faiss_ms_l, 50), 2),
        "faiss_p95": round(percentile(faiss_ms_l, 95), 2),
        "faiss_p99": round(percentile(faiss_ms_l, 99), 2),
        "faiss_p100": round(max(faiss_ms_l), 2),
        "embed_p50": round(percentile(embed_ms_l, 50), 2),
        "embed_p95": round(percentile(embed_ms_l, 95), 2),
        "embed_p99": round(percentile(embed_ms_l, 99), 2),
        "total_p50": round(percentile(total_ms_l, 50), 2),
        "total_p95": round(percentile(total_ms_l, 95), 2),
        "total_p99": round(percentile(total_ms_l, 99), 2),
        "total_p100": round(max(total_ms_l), 2),
    }


def main():
    EXP_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print("HHGOA — ISOLATED FAISS ANN EXPERIMENTS (360,967 VECTORS)")
    print("=" * 80)

    # Load baseline index & metadata
    print("\n[1/5] Loading Full Baseline Index (FlatIP)...")
    baseline_wrapper = VectorIndex.load(str(FULL_INDEX_PATH), str(FULL_META_PATH))
    chunks = baseline_wrapper.chunks
    num_vectors = len(baseline_wrapper)
    print(f"  Loaded {num_vectors:,} vectors and {len(chunks):,} metadata chunks.")

    print("\n[2/5] Extracting Raw Normalized Vectors from FlatIP...")
    t0 = time.perf_counter()
    raw_vectors = baseline_wrapper.index.reconstruct_n(0, num_vectors)
    print(f"  Extracted {raw_vectors.shape} float32 in {time.perf_counter()-t0:.2f}s")

    print("\n[3/5] Loading Evaluation Records for Recall Benchmark...")
    indexed_qids = set(c.query_id for c in chunks)
    eval_records = load_eval_records(indexed_qids, sample_limit=1500)
    print(f"  Loaded {len(eval_records):,} evaluation records with ground-truth.")

    embedder = MultilingualEmbeddingModel()
    results = []

    # ─────────────────────────────────────────────────────────────
    # Config 1: Baseline IndexFlatIP
    # ─────────────────────────────────────────────────────────────
    print("\n" + "-" * 80)
    print("CONFIG 1: Baseline IndexFlatIP (Exact)")
    print("-" * 80)
    flat_lat = benchmark_latency(baseline_wrapper, embedder, n_queries=100, top_k=5)
    flat_rec = evaluate_recall(baseline_wrapper, eval_records, embedder)
    flat_size_mb = round(FULL_INDEX_PATH.stat().st_size / (1024 * 1024), 2)
    res_flat = {
        "name": "IndexFlatIP (Baseline)",
        "type": "FlatIP",
        "params": "exact",
        "build_time_s": 0.0,
        "size_mb": flat_size_mb,
        **flat_lat,
        **flat_rec,
    }
    results.append(res_flat)
    print(f"  FAISS: P50={flat_lat['faiss_p50']}ms, P95={flat_lat['faiss_p95']}ms, P99={flat_lat['faiss_p99']}ms, P100={flat_lat['faiss_p100']}ms")
    print(f"  Total: P50={flat_lat['total_p50']}ms, P95={flat_lat['total_p95']}ms, P100={flat_lat['total_p100']}ms")
    print(f"  Recall: R@1={flat_rec['recall@1']*100:.2f}%, R@5={flat_rec['recall@5']*100:.2f}%, R@10={flat_rec['recall@10']*100:.2f}%")

    # ─────────────────────────────────────────────────────────────
    # Config 2: HNSW Variants
    # ─────────────────────────────────────────────────────────────
    hnsw_configs = [
        {"M": 16, "efSearch": 32, "efConstruction": 64},
        {"M": 16, "efSearch": 64, "efConstruction": 64},
        {"M": 32, "efSearch": 64, "efConstruction": 128},
        {"M": 32, "efSearch": 128, "efConstruction": 128},
        {"M": 64, "efSearch": 128, "efConstruction": 200},
    ]

    built_hnsw_indexes = {}

    for cfg in hnsw_configs:
        m = cfg["M"]
        efS = cfg["efSearch"]
        efC = cfg["efConstruction"]
        tag = f"HNSW_M{m}_efC{efC}"

        if tag not in built_hnsw_indexes:
            print("\n" + "-" * 80)
            print(f"BUILDING HNSW INDEX: M={m}, efConstruction={efC}")
            print("-" * 80)
            t_b0 = time.perf_counter()
            hnsw_idx = faiss.IndexHNSWFlat(EMBEDDING_DIM, m, faiss.METRIC_INNER_PRODUCT)
            hnsw_idx.hnsw.efConstruction = efC
            hnsw_idx.add(raw_vectors)
            t_build = time.perf_counter() - t_b0

            hnsw_path = EXP_DIR / f"faiss_hnsw_M{m}_efC{efC}.faiss"
            faiss.write_index(hnsw_idx, str(hnsw_path))
            size_mb = round(hnsw_path.stat().st_size / (1024 * 1024), 2)
            print(f"  Built {tag} in {t_build:.2f}s | Size: {size_mb:.2f} MB")
            built_hnsw_indexes[tag] = (hnsw_idx, t_build, size_mb, hnsw_path)

        hnsw_idx, t_build, size_mb, _ = built_hnsw_indexes[tag]
        hnsw_idx.hnsw.efSearch = efS

        # Wrap in VectorIndex
        hnsw_wrapper = VectorIndex(dimension=EMBEDDING_DIM)
        hnsw_wrapper.index = hnsw_idx
        hnsw_wrapper.chunks = chunks

        print(f"\nEVALUATING: HNSW M={m}, efConstruction={efC}, efSearch={efS}")
        lat = benchmark_latency(hnsw_wrapper, embedder, n_queries=100, top_k=5)
        rec = evaluate_recall(hnsw_wrapper, eval_records, embedder)

        res_entry = {
            "name": f"HNSW (M={m}, efSearch={efS})",
            "type": "HNSW",
            "params": f"M={m}, efS={efS}, efC={efC}",
            "build_time_s": round(t_build, 2),
            "size_mb": size_mb,
            **lat,
            **rec,
        }
        results.append(res_entry)
        print(f"  FAISS: P50={lat['faiss_p50']}ms, P95={lat['faiss_p95']}ms, P99={lat['faiss_p99']}ms, P100={lat['faiss_p100']}ms")
        print(f"  Total: P50={lat['total_p50']}ms, P95={lat['total_p95']}ms, P100={lat['total_p100']}ms")
        print(f"  Recall: R@1={rec['recall@1']*100:.2f}%, R@5={rec['recall@5']*100:.2f}%, R@10={rec['recall@10']*100:.2f}%")

    # ─────────────────────────────────────────────────────────────
    # Config 3: IVF Variants
    # ─────────────────────────────────────────────────────────────
    ivf_configs = [
        {"nlist": 1024, "nprobe": 8},
        {"nlist": 1024, "nprobe": 16},
        {"nlist": 1024, "nprobe": 32},
        {"nlist": 2048, "nprobe": 16},
        {"nlist": 2048, "nprobe": 32},
        {"nlist": 2048, "nprobe": 64},
    ]

    built_ivf_indexes = {}

    for cfg in ivf_configs:
        nlist = cfg["nlist"]
        nprobe = cfg["nprobe"]
        tag = f"IVF_nlist{nlist}"

        if tag not in built_ivf_indexes:
            print("\n" + "-" * 80)
            print(f"BUILDING IVF INDEX: nlist={nlist}")
            print("-" * 80)
            t_b0 = time.perf_counter()
            quantizer = faiss.IndexFlatIP(EMBEDDING_DIM)
            ivf_idx = faiss.IndexIVFFlat(quantizer, EMBEDDING_DIM, nlist, faiss.METRIC_INNER_PRODUCT)
            ivf_idx.train(raw_vectors)
            ivf_idx.add(raw_vectors)
            t_build = time.perf_counter() - t_b0

            ivf_path = EXP_DIR / f"faiss_ivf_nlist{nlist}.faiss"
            faiss.write_index(ivf_idx, str(ivf_path))
            size_mb = round(ivf_path.stat().st_size / (1024 * 1024), 2)
            print(f"  Built {tag} in {t_build:.2f}s | Size: {size_mb:.2f} MB")
            built_ivf_indexes[tag] = (ivf_idx, t_build, size_mb, ivf_path)

        ivf_idx, t_build, size_mb, _ = built_ivf_indexes[tag]
        ivf_idx.nprobe = nprobe

        ivf_wrapper = VectorIndex(dimension=EMBEDDING_DIM)
        ivf_wrapper.index = ivf_idx
        ivf_wrapper.chunks = chunks

        print(f"\nEVALUATING: IVF nlist={nlist}, nprobe={nprobe}")
        lat = benchmark_latency(ivf_wrapper, embedder, n_queries=100, top_k=5)
        rec = evaluate_recall(ivf_wrapper, eval_records, embedder)

        res_entry = {
            "name": f"IVF (nlist={nlist}, nprobe={nprobe})",
            "type": "IVF",
            "params": f"nlist={nlist}, nprobe={nprobe}",
            "build_time_s": round(t_build, 2),
            "size_mb": size_mb,
            **lat,
            **rec,
        }
        results.append(res_entry)
        print(f"  FAISS: P50={lat['faiss_p50']}ms, P95={lat['faiss_p95']}ms, P99={lat['faiss_p99']}ms, P100={lat['faiss_p100']}ms")
        print(f"  Total: P50={lat['total_p50']}ms, P95={lat['total_p95']}ms, P100={lat['total_p100']}ms")
        print(f"  Recall: R@1={rec['recall@1']*100:.2f}%, R@5={rec['recall@5']*100:.2f}%, R@10={rec['recall@10']*100:.2f}%")

    # ─────────────────────────────────────────────────────────────
    # Summary Table
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 105)
    print("ALL EXPERIMENT RESULTS (FULL CORPUS: 360,967 VECTORS)")
    print("=" * 105)
    header = f"{'Index Configuration':<28} | {'R@1':>6} | {'R@5':>6} | {'R@10':>6} | {'FAISS P50':>9} | {'FAISS P95':>9} | {'FAISS P99':>9} | {'Tot P50':>8} | {'Tot P100':>8}"
    print(header)
    print("-" * len(header))

    for r in results:
        print(
            f"{r['name']:<28} | "
            f"{r['recall@1']*100:>5.1f}% | "
            f"{r['recall@5']*100:>5.1f}% | "
            f"{r['recall@10']*100:>5.1f}% | "
            f"{r['faiss_p50']:>8.2f}ms | "
            f"{r['faiss_p95']:>8.2f}ms | "
            f"{r['faiss_p99']:>8.2f}ms | "
            f"{r['total_p50']:>7.2f}ms | "
            f"{r['total_p100']:>7.2f}ms"
        )
    print("=" * 105)

    with open(EXP_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump({"benchmark": "HHGoa FAISS ANN Experiments", "results": results}, f, indent=2)
    print(f"\nAll results saved to: {EXP_REPORT_PATH}")


if __name__ == "__main__":
    main()
