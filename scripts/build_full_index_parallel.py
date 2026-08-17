import sys
import time
import os
import psutil
import shutil
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from rag.config import EMBEDDING_DIM, PROCESSED_DATA_DIR
from rag.dataset import get_dataset_path, stream_dataset_records
from rag.chunking import passage_preserving
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex
from rag.models import DatasetRecord, Passage, Chunk

TEMP_INDEX_PATH = PROCESSED_DATA_DIR / "faiss_index_full.faiss"
TEMP_META_PATH = PROCESSED_DATA_DIR / "metadata_full.pkl"
CHECKPOINT_PREFIX = PROCESSED_DATA_DIR / "full_build_checkpoint"

NUM_WORKERS = min(6, os.cpu_count() or 4)
RECORD_BATCH_SIZE = 400  # records per worker task (~4000 chunks)
CHECKPOINT_VECTORS = 10000


def get_mem_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def sep(c="=", w=72):
    print(c * w, flush=True)


def serialize_record(rec: DatasetRecord) -> dict:
    return {
        "query_id": rec.query_id,
        "query": rec.query,
        "english_query": rec.english_query,
        "answer": rec.answer,
        "english_answer": rec.english_answer,
        "query_type": rec.query_type,
        "source_lang": rec.source_lang,
        "target_lang": rec.target_lang,
        "passages": [
            {
                "passage_index": p.passage_index,
                "text": p.text,
                "english_text": p.english_text,
                "is_selected": p.is_selected,
            }
            for p in rec.passages
        ],
    }


def worker_embed_batch(record_dicts: list) -> tuple:
    import os
    import numpy as np
    from rag.embeddings import MultilingualEmbeddingModel
    from rag.models import DatasetRecord, Passage
    from rag.chunking import passage_preserving

    embedder = MultilingualEmbeddingModel()

    all_chunks = []
    for r_dict in record_dicts:
        passages = [Passage(**p) for p in r_dict["passages"]]
        rec = DatasetRecord(
            query_id=r_dict["query_id"],
            query=r_dict["query"],
            english_query=r_dict["english_query"],
            answer=r_dict["answer"],
            english_answer=r_dict["english_answer"],
            query_type=r_dict["query_type"],
            source_lang=r_dict["source_lang"],
            target_lang=r_dict["target_lang"],
            passages=passages,
        )
        chunks = passage_preserving(rec)
        all_chunks.extend(chunks)

    if not all_chunks:
        return [], np.empty((0, 384), dtype=np.float32)

    doc_texts = [c.text for c in all_chunks]
    embeddings = embedder.embed_documents(doc_texts, batch_size=256, show_progress_bar=False)
    return all_chunks, embeddings


def main():
    sep()
    print("HHGOA TASK 2 — PARALLEL FULL CORPUS FAISS INDEX BUILD", flush=True)
    sep()
    print(f"Project root     : {PROJECT_ROOT}", flush=True)
    print(f"Target dataset   : ai4bharat/MSMARCO-XI (validation/hinval.parquet)", flush=True)
    print(f"Chunking strategy: passage_preserving", flush=True)
    print(f"Parallel Workers : {NUM_WORKERS}", flush=True)
    print(f"Record Batch Size: {RECORD_BATCH_SIZE}", flush=True)
    print(f"Temp Index Out   : {TEMP_INDEX_PATH}", flush=True)
    print(f"Temp Metadata Out: {TEMP_META_PATH}", flush=True)
    sep()

    dataset_path = get_dataset_path()
    print(f"\n[1/4] Dataset located at: {dataset_path}", flush=True)

    print("\n[2/4] Initializing VectorIndex and checking checkpoints...", flush=True)
    index = VectorIndex(dimension=EMBEDDING_DIM)

    chk_idx = Path(f"{CHECKPOINT_PREFIX}.faiss")
    chk_meta = Path(f"{CHECKPOINT_PREFIX}.pkl")
    existing_query_ids = set()

    if chk_idx.exists() and chk_meta.exists():
        print(f"  Found existing checkpoint! Loading from {chk_idx}...", flush=True)
        index = VectorIndex.load(str(chk_idx), str(chk_meta))
        existing_query_ids = set(c.query_id for c in index.chunks)
        print(f"  Resuming from checkpoint ({len(existing_query_ids):,} existing records, {len(index):,} vectors loaded).", flush=True)
    elif TEMP_INDEX_PATH.exists() and TEMP_META_PATH.exists():
        print(f"  Found existing full index temp files! Loading from {TEMP_INDEX_PATH}...", flush=True)
        index = VectorIndex.load(str(TEMP_INDEX_PATH), str(TEMP_META_PATH))
        existing_query_ids = set(c.query_id for c in index.chunks)
        print(f"  Resuming from temp files ({len(existing_query_ids):,} existing records, {len(index):,} vectors loaded).", flush=True)

    print("\n[3/4] Streaming dataset and preparing unindexed record batches...", flush=True)
    t_stream_start = time.perf_counter()

    unindexed_record_batches = []
    current_batch = []
    total_unindexed_records = 0
    total_records_seen = 0

    for rec in stream_dataset_records(dataset_path, max_records=None):
        total_records_seen += 1
        if rec.query_id in existing_query_ids:
            continue
        
        current_batch.append(serialize_record(rec))
        total_unindexed_records += 1

        if len(current_batch) >= RECORD_BATCH_SIZE:
            unindexed_record_batches.append(current_batch)
            current_batch = []

    if current_batch:
        unindexed_record_batches.append(current_batch)
        current_batch = []

    t_stream_end = time.perf_counter()
    print(f"  Dataset scan finished in {(t_stream_end - t_stream_start):.2f}s.")
    print(f"  Total records seen : {total_records_seen:,}")
    print(f"  Unindexed records  : {total_unindexed_records:,} ({len(unindexed_record_batches)} batches)")

    if not unindexed_record_batches:
        print("\nAll dataset records are already indexed!", flush=True)
    else:
        print(f"\n[4/4] Executing parallel embedding across {NUM_WORKERS} worker processes...", flush=True)
        t_start = time.perf_counter()
        initial_vectors = len(index)
        last_checkpoint_count = initial_vectors
        completed_batches = 0

        with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
            future_to_batch = {
                executor.submit(worker_embed_batch, batch): idx
                for idx, batch in enumerate(unindexed_record_batches)
            }

            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                try:
                    chunks, embeddings = future.result()
                    if chunks and len(embeddings) > 0:
                        index.add_embeddings(embeddings, chunks)
                    
                    completed_batches += 1
                    now = time.perf_counter()
                    elapsed = now - t_start
                    added = len(index) - initial_vectors
                    vps = added / elapsed if elapsed > 0 else 0
                    mem_mb = get_mem_mb()
                    disk_free_gb = shutil.disk_usage(str(PROCESSED_DATA_DIR)).free / (1024**3)

                    print(f"  Batch {completed_batches:>3}/{len(unindexed_record_batches)} | "
                          f"Vectors: {len(index):>8,} | Metadata: {len(index.chunks):>8,} | "
                          f"Speed: {vps:>6.1f} v/s | RAM: {mem_mb:>6.1f} MB | "
                          f"Disk Free: {disk_free_gb:>5.1f} GB | Elapsed: {elapsed/60:>5.1f}m", flush=True)

                    if len(index) - last_checkpoint_count >= CHECKPOINT_VECTORS:
                        print(f"  >>> Saving checkpoint ({len(index):,} vectors)...", flush=True)
                        index.save(str(chk_idx), str(chk_meta))
                        index.save(str(TEMP_INDEX_PATH), str(TEMP_META_PATH))
                        last_checkpoint_count = len(index)

                except Exception as e:
                    print(f"  ERROR processing batch {batch_idx}: {e}", flush=True)

        t_end = time.perf_counter()
        duration = t_end - t_start
        added_vectors = len(index) - initial_vectors
        throughput = added_vectors / duration if duration > 0 else 0

        sep()
        print("PARALLEL INDEX BUILD COMPLETE", flush=True)
        sep()
        print(f"Total Vectors in Index  : {len(index):,}", flush=True)
        print(f"Total Metadata Records  : {len(index.chunks):,}", flush=True)
        print(f"New Vectors Added       : {added_vectors:,}", flush=True)
        print(f"Parallel Build Duration : {duration/60:.2f} minutes ({duration:.1f} seconds)", flush=True)
        print(f"Average Throughput      : {throughput:.1f} vectors/sec", flush=True)
        print(f"Peak Main Process RAM   : {get_mem_mb():.1f} MB", flush=True)

    print("\n[5/5] Persisting final full index and metadata to temp paths...", flush=True)
    index.save(str(TEMP_INDEX_PATH), str(TEMP_META_PATH))

    index_size_mb = TEMP_INDEX_PATH.stat().st_size / (1024 * 1024)
    meta_size_mb = TEMP_META_PATH.stat().st_size / (1024 * 1024)

    print(f"Saved FAISS index ({index_size_mb:.2f} MB) to {TEMP_INDEX_PATH}", flush=True)
    print(f"Saved Metadata    ({meta_size_mb:.2f} MB) to {TEMP_META_PATH}", flush=True)

    if chk_idx.exists():
        chk_idx.unlink()
    if chk_meta.exists():
        chk_meta.unlink()

    sep()
    print("FULL INDEX READY FOR VALIDATION & SWAP", flush=True)
    sep()


if __name__ == "__main__":
    main()
