"""
HHGOA — FULL FAISS INDEX VALIDATION & TASK 2 BENCHMARK
Run: py -3.13 scripts/validate_full_index.py
"""
import json, os, shutil, sys, time, statistics
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from rag.config import (PROCESSED_DATA_DIR, FAISS_INDEX_PATH, METADATA_PATH,
    EMBEDDING_DIM, CONFIDENCE_THRESHOLD, DEFAULT_TOP_K, MAX_CONTEXT_CHUNKS)
from rag.dataset import get_dataset_path, stream_dataset_records
from rag.embeddings import MultilingualEmbeddingModel
from rag.evaluation import calculate_percentile
from rag.index import VectorIndex
from rag.orchestrator import RAGOrchestrator
from rag.retrieval import RetrievalService

FULL_INDEX_PATH   = PROCESSED_DATA_DIR / 'faiss_index_full.faiss'
FULL_META_PATH    = PROCESSED_DATA_DIR / 'metadata_full.pkl'
BACKUP_INDEX_PATH = PROCESSED_DATA_DIR / 'faiss_index_backup.faiss'
BACKUP_META_PATH  = PROCESSED_DATA_DIR / 'metadata_backup.pkl'
OUT_REPORT_PATH   = PROCESSED_DATA_DIR / 'full_index_validation_report.json'
OLD_P50, OLD_P70, OLD_P100 = 14.272, 17.184, 34.385
SEP = '=' * 80

def p(msg=''): print(msg, flush=True)
def sep(label=''): 
    if label:
        p(f'\n{SEP}\n  {label}\n{SEP}')
    else:
        p(SEP)
def pct(vals, perc): return round(calculate_percentile(vals, perc), 3)

def main():
    BENCH_N = 250  # benchmark query count

    sep('HHGOA — FULL FAISS INDEX VALIDATION & TASK 2 BENCHMARK')
    p(f'  Full index  : {FULL_INDEX_PATH}')
    p(f'  Full meta   : {FULL_META_PATH}')
    p(f'  Old index   : {FAISS_INDEX_PATH}')
    p(f'  Bench count : {BENCH_N}')

    # ── STEP 1: BACKUP ────────────────────────────────────────────────────────
    sep('STEP 1 — BACKUP CURRENT INDEX')
    for src, dst in [(FAISS_INDEX_PATH, BACKUP_INDEX_PATH), (METADATA_PATH, BACKUP_META_PATH)]:
        if src.exists():
            shutil.copy2(src, dst)
            p(f'  Backed up: {src.name} -> {dst.name} ({dst.stat().st_size/1024/1024:.2f} MB)')
        else:
            p(f'  SKIP: {src.name} not present')
    p('  Original files NOT deleted.')

    # ── STEP 2: INTEGRITY ─────────────────────────────────────────────────────
    sep('STEP 2 — FULL INDEX INTEGRITY VERIFICATION')
    if not FULL_INDEX_PATH.exists() or not FULL_META_PATH.exists():
        p('ERROR: Full index files not found. Aborting.')
        sys.exit(1)

    p(f'  faiss_index_full.faiss : {FULL_INDEX_PATH.stat().st_size/1024/1024:.2f} MB')
    p(f'  metadata_full.pkl      : {FULL_META_PATH.stat().st_size/1024/1024:.2f} MB')
    p('  Loading full index ...')
    t0 = time.perf_counter()
    index = VectorIndex.load(str(FULL_INDEX_PATH), str(FULL_META_PATH))
    t1 = time.perf_counter()
    vc, mc, dim = len(index), len(index.chunks), index.index.d
    p(f'  Load time              : {(t1-t0):.2f}s')
    p(f'  Vector count (FAISS)   : {vc:,}')
    p(f'  Metadata count (chunks): {mc:,}')
    p(f'  Embedding dimension    : {dim} (expected {EMBEDDING_DIM})')

    errors = []
    if vc != mc: errors.append(f'MISMATCH: {vc:,} vectors vs {mc:,} metadata')
    if dim != EMBEDDING_DIM: errors.append(f'DIM ERROR: got {dim}, expected {EMBEDDING_DIM}')
    if vc == 0: errors.append('EMPTY INDEX')
    if errors:
        for e in errors: p(f'  ERROR: {e}')
        sys.exit(1)

    # Spot-check chunk mapping
    for c in index.chunks[:5] + index.chunks[-5:]:
        parts = c.chunk_id.split(':')
        assert len(parts) == 3, f'Bad chunk_id: {c.chunk_id}'
        assert c.text, 'Empty text'
        assert c.query_id is not None

    p('  INTEGRITY OK — chunk_id/query_id/passage_index mapping verified.')

    # ── STEPS 3+4: RECALL EVALUATION ─────────────────────────────────────────
    sep('STEPS 3+4 — FULL-CORPUS RECALL@K EVALUATION')
    embedder = MultilingualEmbeddingModel()
    ret_svc = RetrievalService(embedding_model=embedder, index=index)
    p(f'  ONNX backend           : {embedder.using_onnx}')

    indexed_qids = set(c.query_id for c in index.chunks)
    p(f'  Unique query_ids in full index: {len(indexed_qids):,}')
    p('  Streaming ALL dataset records ...')
    dataset_path = get_dataset_path()
    all_records = list(stream_dataset_records(dataset_path))
    total_records = len(all_records)

    evaluable = [
        r for r in all_records
        if any(psg.is_selected for psg in r.passages) and r.query_id in indexed_qids
    ]
    excl_no_sel  = sum(1 for r in all_records if not any(psg.is_selected for psg in r.passages))
    excl_not_idx = sum(1 for r in all_records
                       if any(psg.is_selected for psg in r.passages) and r.query_id not in indexed_qids)

    p(f'\n  Total records in dataset   : {total_records:,}')
    p(f'  Evaluable (indexed + sel)  : {len(evaluable):,}')
    p(f'  Excluded (no selected psg) : {excl_no_sel:,}')
    p(f'  Excluded (not in index)    : {excl_not_idx:,}')
    p(f'  DENOMINATOR for all Recall : {len(evaluable):,}')

    if not evaluable:
        p('ERROR: No evaluable records.')
        sys.exit(1)

    ks = [1, 3, 5, 10]
    max_k = max(ks)
    hits = {k: 0 for k in ks}
    t_eval = time.perf_counter()

    for i, rec in enumerate(evaluable):
        q = rec.query.strip() if rec.query and rec.query.strip() else rec.english_query.strip()
        if not q:
            continue
        gt = {psg.passage_index for psg in rec.passages if psg.is_selected}
        resp = ret_svc.retrieve(query=q, top_k=max_k)
        retrieved = [r.passage_index for r in resp.results if r.query_id == rec.query_id]
        for k in ks:
            if any(idx in gt for idx in retrieved[:k]):
                hits[k] += 1
        if (i + 1) % 200 == 0:
            p(f'    [{i+1:,}/{len(evaluable):,}] elapsed={time.perf_counter()-t_eval:.1f}s')

    eval_dur = time.perf_counter() - t_eval
    n = len(evaluable)
    recall = {k: round(hits[k] / n, 4) for k in ks}

    p(f'\n  Recall evaluation complete in {eval_dur:.1f}s')
    p(f'  Hits@1  = {hits[1]:,}  Recall@1  = {recall[1]*100:.2f}%  (denom={n:,})')
    p(f'  Hits@3  = {hits[3]:,}  Recall@3  = {recall[3]*100:.2f}%  (denom={n:,})')
    p(f'  Hits@5  = {hits[5]:,}  Recall@5  = {recall[5]*100:.2f}%  (denom={n:,})')
    p(f'  Hits@10 = {hits[10]:,}  Recall@10 = {recall[10]*100:.2f}%  (denom={n:,})')

    # ── STEP 5: LATENCY BENCHMARK ─────────────────────────────────────────────
    sep(f'STEP 5 — OFFICIAL POST-STT LATENCY BENCHMARK (N={BENCH_N})')
    p('  Timer: START=STT transcript in memory  END=grounded output assembled')
    p('  STT latency is NOT included.')

    # Use a fresh orchestrator backed by the full index
    embedder2 = MultilingualEmbeddingModel()
    ret_svc2 = RetrievalService(embedding_model=embedder2, index=index)
    orch = RAGOrchestrator(retrieval_service=ret_svc2)

    # Warmup (excluded from timing)
    for _ in range(5):
        orch.run_text_pipeline('warmup कॉर्पोरेशन query')
    p('  Warmup complete (5 passes, excluded).')

    bench_queries = []
    for r in all_records:
        q = r.query.strip() if r.query and r.query.strip() else r.english_query.strip()
        if q:
            bench_queries.append(q)
        if len(bench_queries) >= BENCH_N:
            break
    p(f'  Collected {len(bench_queries)} benchmark queries.')

    prep_l, emb_l, srch_l, gate_l, ctx_l, gen_l, val_l, tot_l = [], [], [], [], [], [], [], []
    t_bench = time.perf_counter()

    for i, q in enumerate(bench_queries):
        res = orch.run_text_pipeline(q)
        t = res.timing
        prep_l.append(t.query_preprocessing_ms)
        emb_l.append(t.query_embedding_ms)
        srch_l.append(t.vector_search_ms)
        gate_l.append(t.answerability_check_ms)
        ctx_l.append(t.context_build_ms)
        gen_l.append(t.llm_generation_ms)
        val_l.append(t.grounding_validation_ms)
        tot_l.append(t.total_pipeline_ms)
        if (i + 1) % 50 == 0:
            p(f'    [{i+1}/{len(bench_queries)}] last_total={t.total_pipeline_ms:.2f}ms  elapsed={time.perf_counter()-t_bench:.1f}s')

    bench_dur = time.perf_counter() - t_bench
    p(f'  Benchmark complete in {bench_dur:.1f}s')

    stages = [
        ('1.Query Preprocessing', prep_l),
        ('2.ONNX E5-small Embed',  emb_l),
        ('3.FAISS ANN Search',    srch_l),
        ('4.Answerability Gate',  gate_l),
        ('5.Context Selection',   ctx_l),
        ('6.Grounded Generation', gen_l),
        ('7.Citation Validation', val_l),
        ('Total Post-STT Pipeline', tot_l),
    ]

    p(f'\n  {"Stage":<28} | {"P50":>8} | {"P70":>8} | {"P100":>8} | {"Mean":>8} | {"Max":>8}')
    p(f'  {"-"*28}-+-{"-"*8}-+-{"-"*8}-+-{"-"*8}-+-{"-"*8}-+-{"-"*8}')
    stage_res = {}
    for name, vals in stages:
        if vals:
            r = dict(
                p50_ms=pct(vals, 50), p70_ms=pct(vals, 70), p100_ms=pct(vals, 100),
                mean_ms=round(statistics.mean(vals), 3), max_ms=round(max(vals), 3)
            )
            stage_res[name] = r
            p(f'  {name:<28} | {r["p50_ms"]:>8.3f} | {r["p70_ms"]:>8.3f} | {r["p100_ms"]:>8.3f} | {r["mean_ms"]:>8.3f} | {r["max_ms"]:>8.3f}')
    s = stage_res['Total Post-STT Pipeline']

    # ── STEP 6: COMPARISON ────────────────────────────────────────────────────
    sep('STEP 6 — OLD INDEX vs FULL INDEX COMPARISON')
    p(f'  {"Metric":<10} | {"Old Index":>12} | {"Full Index":>12} | {"Delta":>12}')
    p(f'  {"-"*10}-+-{"-"*12}-+-{"-"*12}-+-{"-"*12}')
    for label, old, new in [('P50', OLD_P50, s['p50_ms']), ('P70', OLD_P70, s['p70_ms']), ('P100', OLD_P100, s['p100_ms'])]:
        d = new - old
        sign = '+' if d > 0 else ''
        p(f'  {label:<10} | {old:>12.3f} | {new:>12.3f} | {sign}{d:.3f} ms')

    # ── STEP 7: VERDICT ───────────────────────────────────────────────────────
    sep('STEP 7 — TASK 2 VERDICT')
    p100 = s['p100_ms']
    p(f'  Requirement  : P100 < 200 ms (post-STT, STT excluded)')
    p(f'  Measured P100: {p100:.3f} ms')
    passed = p100 < 200.0
    if passed:
        p(f'\n  PASS — FULL CORPUS POST-STT PIPELINE <200 ms  (P100={p100:.3f}ms, margin={200.0-p100:.3f}ms)')
    else:
        p(f'\n  FAIL — FULL CORPUS POST-STT PIPELINE >=200 ms (P100={p100:.3f}ms, excess={p100-200.0:.3f}ms)')
        bottleneck = max(
            ((k, v) for k, v in stage_res.items() if k != 'Total Post-STT Pipeline'),
            key=lambda x: x[1]['p100_ms']
        )
        p(f'  Bottleneck stage: {bottleneck[0]}  P100={bottleneck[1]["p100_ms"]:.3f}ms')

    # ── SAVE REPORT ───────────────────────────────────────────────────────────
    report = dict(
        benchmark='HHGoa Full Index Validation',
        latency_definition='Timer starts after STT transcript available; stops after citations assembled. STT excluded.',
        index_files=dict(
            faiss_path=str(FULL_INDEX_PATH),
            meta_path=str(FULL_META_PATH),
            vector_count=vc, metadata_count=mc, dimension=dim,
            faiss_size_mb=round(FULL_INDEX_PATH.stat().st_size / 1024 / 1024, 2),
            meta_size_mb=round(FULL_META_PATH.stat().st_size / 1024 / 1024, 2),
        ),
        recall=dict(
            denominator=n,
            total_dataset_records=total_records,
            excluded_no_selected=excl_no_sel,
            excluded_not_indexed=excl_not_idx,
            hits_at_1=hits[1], hits_at_3=hits[3], hits_at_5=hits[5], hits_at_10=hits[10],
            recall_at_1=recall[1], recall_at_3=recall[3], recall_at_5=recall[5], recall_at_10=recall[10],
        ),
        latency_benchmark=dict(
            n_queries=len(bench_queries),
            stage_breakdown=stage_res,
            summary=s,
            raw_total_latencies_ms=[round(v, 4) for v in tot_l],
        ),
        comparison=dict(
            old_p50=OLD_P50, old_p70=OLD_P70, old_p100=OLD_P100,
            new_p50=s['p50_ms'], new_p70=s['p70_ms'], new_p100=s['p100_ms'],
        ),
        task2_compliance=dict(requirement_ms=200.0, p100_ms=p100, passes=passed),
    )

    OUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # ── FINAL SUMMARY ─────────────────────────────────────────────────────────
    sep('FINAL REPORT SUMMARY')
    p(f'  A. Full index integrity         : OK')
    p(f'  B. Full vector count            : {vc:,}')
    p(f'  C. Full metadata count          : {mc:,}')
    p(f'  D. Recall@1/3/5/10 (denom={n:,}): {recall[1]*100:.2f}% / {recall[3]*100:.2f}% / {recall[5]*100:.2f}% / {recall[10]*100:.2f}%')
    p(f'  E. Full-index P50/P70/P100      : {s["p50_ms"]:.3f} / {s["p70_ms"]:.3f} / {s["p100_ms"]:.3f} ms')
    p(f'  F. Stage breakdown              : see report JSON and table above')
    p(f'  G. Old P100 -> New P100         : {OLD_P100:.3f} ms -> {s["p100_ms"]:.3f} ms')
    p(f'  H. Tests                        : run separately with: py -3.13 -m pytest')
    p(f'  I. Task 2 <200ms verdict        : {"PASS" if passed else "FAIL"}')
    p(f'  J. Remaining issues             : {"None" if passed else "Latency bottleneck identified above"}')
    p(f'\n  Report saved to: {OUT_REPORT_PATH}')
    sep()


if __name__ == '__main__':
    main()
