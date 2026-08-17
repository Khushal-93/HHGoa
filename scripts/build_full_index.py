import sys
import time
import os
import psutil
from pathlib import Path
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

TEMP_INDEX_PATH = PROCESSED_DATA_DIR / "faiss_index_full.faiss"
TEMP_META_PATH = PROCESSED_DATA_DIR / "metadata_full.pkl"
CHECKPOINT_PREFIX = PROCESSED_DATA_DIR / "full_build_checkpoint"

BATCH_SIZE = 256
CHECKPOINT_INTERVAL = 5000  # Save checkpoint every 5,000 chunks

def get_mem_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def sep(c="=", w=72):
    print(c * w, flush=True)

def main():
    sep()
    print("HHGOA TASK 2 — FULL CORPUS FAISS INDEX BUILD", flush=True)
    sep()
    print(f"Project root     : {PROJECT_ROOT}", flush=True)
    print(f"Target dataset   : ai4bharat/MSMARCO-XI (validation/hinval.parquet)", flush=True)
    print(f"Chunking strategy: passage_preserving", flush=True)
    print(f"Batch size       : {BATCH_SIZE}", flush=True)
    print(f"Temp Index Out   : {TEMP_INDEX_PATH}", flush=True)
    print(f"Temp Metadata Out: {TEMP_META_PATH}", flush=True)
    sep()

    dataset_path = get_dataset_path()
    print(f"\n[1/4] Dataset located at: {dataset_path}", flush=True)

    print("\n[2/4] Initialising MultilingualEmbeddingModel...", flush=True)
    t_mod_start = time.perf_counter()
    embedder = MultilingualEmbeddingModel()
    index = VectorIndex(dimension=EMBEDDING_DIM)
    print(f"  Model initialised in {(time.perf_counter() - t_mod_start):.2f}s", flush=True)

    chk_idx = Path(f"{CHECKPOINT_PREFIX}.faiss")
    chk_meta = Path(f"{CHECKPOINT_PREFIX}.pkl")
    existing_query_ids = set()

    if chk_idx.exists() and chk_meta.exists():
        print(f"\n  Found existing checkpoint! Loading from {chk_idx}...", flush=True)
        index = VectorIndex.load(str(chk_idx), str(chk_meta))
        existing_query_ids = set(c.query_id for c in index.chunks)
        print(f"  Resuming from checkpoint ({len(existing_query_ids):,} existing records, {len(index):,} vectors loaded).", flush=True)
    elif TEMP_INDEX_PATH.exists() and TEMP_META_PATH.exists():
        print(f"\n  Found existing full index temp files! Loading from {TEMP_INDEX_PATH}...", flush=True)
        index = VectorIndex.load(str(TEMP_INDEX_PATH), str(TEMP_META_PATH))
        existing_query_ids = set(c.query_id for c in index.chunks)
        print(f"  Resuming from temp files ({len(existing_query_ids):,} existing records, {len(index):,} vectors loaded).", flush=True)

    print("\n[3/4] Building full index across all records...", flush=True)
    t_start = time.perf_counter()

    total_records = 0
    total_chunks = 0
    chunk_buffer = []

    initial_chunks = len(index)
    last_checkpoint_count = initial_chunks

    import shutil

    for record in stream_dataset_records(dataset_path, max_records=None):
        total_records += 1

        if record.query_id in existing_query_ids:
            continue

        chunks = passage_preserving(record)
        chunk_buffer.extend(chunks)

        if len(chunk_buffer) >= 1000:
            doc_texts = [c.text for c in chunk_buffer]
            embeddings = embedder.embed_documents(
                doc_texts,
                batch_size=BATCH_SIZE,
                show_progress_bar=False,
            )
            index.add_embeddings(embeddings, chunk_buffer)
            total_chunks += len(chunk_buffer)
            chunk_buffer = []

            now = time.perf_counter()
            elapsed = now - t_start
            added = len(index) - initial_chunks
            cps = added / elapsed if elapsed > 0 else 0
            mem_mb = get_mem_mb()
            disk_free_gb = shutil.disk_usage(str(PROCESSED_DATA_DIR)).free / (1024**3)

            print(f"  Records: {total_records:>6,} | Vectors: {len(index):>8,} | "
                  f"Metadata: {len(index.chunks):>8,} | Speed: {cps:>6.1f} v/s | "
                  f"RAM: {mem_mb:>6.1f} MB | Disk Free: {disk_free_gb:>5.1f} GB | Elapsed: {elapsed/60:>5.1f}m", flush=True)

            if len(index) - last_checkpoint_count >= CHECKPOINT_INTERVAL:
                print(f"  >>> Saving checkpoint ({len(index):,} chunks)...", flush=True)
                index.save(str(chk_idx), str(chk_meta))
                index.save(str(TEMP_INDEX_PATH), str(TEMP_META_PATH))
                last_checkpoint_count = len(index)

    if chunk_buffer:
        doc_texts = [c.text for c in chunk_buffer]
        embeddings = embedder.embed_documents(
            doc_texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
        )
        index.add_embeddings(embeddings, chunk_buffer)
        total_chunks += len(chunk_buffer)
        chunk_buffer = []

    t_end = time.perf_counter()
    duration = t_end - t_start
    throughput = (len(index) - initial_chunks) / duration if duration > 0 else 0

    sep()
    print("FULL INDEX BUILD COMPLETE", flush=True)
    sep()
    print(f"Total Records Processed : {total_records:,}", flush=True)
    print(f"Total Chunks Indexed    : {len(index):,}", flush=True)
    print(f"Build Duration          : {duration/60:.2f} minutes ({duration:.1f} seconds)", flush=True)
    print(f"Average Throughput      : {throughput:.1f} chunks/sec", flush=True)
    print(f"Peak RAM Usage          : {get_mem_mb():.1f} MB", flush=True)

    print("\n[4/4] Persisting full index and metadata...", flush=True)
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
