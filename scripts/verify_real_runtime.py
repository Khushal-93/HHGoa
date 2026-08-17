"""
HHGoa — Real Runtime Verification of Promoted Production Index
Tests real FastAPI application endpoints:
  - GET /health
  - POST /api/retrieve
  - POST /api/query
  - Multilingual queries (English, Hindi, Bengali)
  - Production runtime benchmark (Owner-style & Task 2 Post-STT)
"""
import json
import os
import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from rag.api import app
from rag.config import PROCESSED_DATA_DIR, FAISS_INDEX_PATH, METADATA_PATH

OWNER_QUERIES = [
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

MULTILINGUAL_QUERIES = [
    {"lang": "English", "query": "What are the legal liabilities of a corporation?"},
    {"lang": "Hindi", "query": "कॉर्पोरेशन की कानूनी देनदारियां क्या हैं?"},
    {"lang": "Bengali", "query": "কর্পোরেশনের আইনি দায়বদ্ধতা কি কি?"},
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


def main():
    print("=" * 80)
    print("HHGOA — REAL PRODUCTION RUNTIME VERIFICATION")
    print("=" * 80)
    print(f"  Production Index Path : {FAISS_INDEX_PATH} ({FAISS_INDEX_PATH.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  Production Meta Path  : {METADATA_PATH} ({METADATA_PATH.stat().st_size / (1024*1024):.2f} MB)")

    print("\n[1/5] Starting Real FastAPI Application (lifespan load)...")
    with TestClient(app) as client:
        # Step 5: GET /health
        print("\n[2/5] Testing GET /health ...")
        res_health = client.get("/health")
        print(f"  HTTP Status : {res_health.status_code}")
        health_data = res_health.json()
        print(f"  Response    : {json.dumps(health_data, indent=2)}")

        assert res_health.status_code == 200, "Health check failed"
        assert health_data["status"] == "healthy"
        assert health_data["index_loaded"] is True
        assert health_data["vector_count"] == 360967
        assert health_data["indexed_chunks"] == 360967
        assert health_data["dimension"] == 384
        assert "HNSW" in health_data["index_type"]
        assert health_data["ef_search"] == 128
        print("  -> /health VERIFIED: IndexHNSWFlat, 360,967 vectors, efSearch=128")

        # Step 6: POST /api/retrieve and POST /api/query
        print("\n[3/5] Testing POST /api/retrieve & POST /api/query ...")
        # Warmup
        for i in range(5):
            client.post("/api/retrieve", json={"query": "warmup query", "top_k": 5})

        res_ret = client.post("/api/retrieve", json={"query": "What is a corporation?", "top_k": 5})
        print(f"  POST /api/retrieve Status : {res_ret.status_code}")
        ret_data = res_ret.json()
        print(f"  Retrieved Chunks          : {len(ret_data['results'])}")
        print(f"  Top Match Chunk ID        : {ret_data['results'][0]['chunk_id']}")
        print(f"  Top Score                 : {ret_data['results'][0]['score']:.4f}")
        print(f"  Retrieval Timing          : {json.dumps(ret_data['timing'])}")

        assert res_ret.status_code == 200
        assert len(ret_data["results"]) == 5
        assert ret_data["timing"]["retrieval_ms"] < 10.0

        res_query = client.post("/api/query", json={"query": "What is a corporation?"})
        print(f"\n  POST /api/query Status    : {res_query.status_code}")
        query_data = res_query.json()
        print(f"  Answer                    : {query_data['answer'][:120]}...")
        print(f"  Grounded                  : {query_data['grounded']}")
        print(f"  Confidence                : {query_data['confidence_score']:.4f}")
        print(f"  Sources Count             : {len(query_data['sources'])}")
        print(f"  Pipeline Timing           : {json.dumps(query_data['timing'])}")

        assert res_query.status_code == 200
        assert query_data["grounded"] is True

        # Step 7: Multilingual Runtime Test
        print("\n[4/5] Testing Multilingual Endpoints (English, Hindi, Bengali) ...")
        ml_results = []
        for item in MULTILINGUAL_QUERIES:
            lang = item["lang"]
            q = item["query"]
            t0 = time.perf_counter()
            resp = client.post("/api/query", json={"query": q})
            dur = (time.perf_counter() - t0) * 1000.0
            assert resp.status_code == 200
            d = resp.json()
            citations = [s["chunk_id"] for s in d.get("sources", [])]
            ml_results.append({
                "lang": lang,
                "query": q,
                "status_code": resp.status_code,
                "grounded": d["grounded"],
                "confidence": d["confidence_score"],
                "sources_count": len(d["sources"]),
                "latency_ms": round(d["timing"]["total_pipeline_ms"], 2),
                "citations": citations,
            })
            print(f"  [{lang:<7}] Status={resp.status_code} | Grounded={d['grounded']} | Conf={d['confidence_score']:.4f} | Latency={d['timing']['total_pipeline_ms']:.2f}ms | Citations={citations}")

        # Step 8: Runtime Latency Test
        print("\n[5/5] Production Runtime Latency Benchmarks (100 queries) ...")
        # Owner style retrieval
        embed_l, faiss_l, tot_ret_l = [], [], []
        post_stt_l = []

        for i in range(100):
            q = OWNER_QUERIES[i % len(OWNER_QUERIES)]
            resp = client.post("/api/retrieve", json={"query": q, "top_k": 5})
            timing = resp.json()["timing"]
            embed_l.append(timing["embedding_ms"])
            faiss_l.append(timing["retrieval_ms"])
            tot_ret_l.append(timing["total_ms"])

            resp_q = client.post("/api/query", json={"query": q})
            q_timing = resp_q.json()["timing"]
            post_stt_l.append(q_timing["total_pipeline_ms"])

        print("\n  --- OWNER-STYLE RETRIEVAL BENCHMARK (ms) ---")
        for name, vals in [("Embedding", embed_l), ("FAISS HNSW", faiss_l), ("Total Ret", tot_ret_l)]:
            avg = statistics.mean(vals)
            p50 = percentile(vals, 50)
            p95 = percentile(vals, 95)
            p99 = percentile(vals, 99)
            p100 = max(vals)
            print(f"    {name:<12} | AVG={avg:>6.2f} | P50={p50:>6.2f} | P95={p95:>6.2f} | P99={p99:>6.2f} | P100={p100:>6.2f}")

        print("\n  --- TASK 2 POST-STT PIPELINE BENCHMARK (ms) ---")
        p50_stt = percentile(post_stt_l, 50)
        p70_stt = percentile(post_stt_l, 70)
        p100_stt = max(post_stt_l)
        print(f"    Total Post-STT | P50={p50_stt:>6.2f} ms | P70={p70_stt:>6.2f} ms | P100={p100_stt:>6.2f} ms")
        print(f"    Task 2 Requirement: <200.0 ms | Measured P100: {p100_stt:.2f} ms -> {'PASS' if p100_stt < 200.0 else 'FAIL'}")

    print("\n" + "=" * 80)
    print("REAL PRODUCTION RUNTIME VERIFICATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
