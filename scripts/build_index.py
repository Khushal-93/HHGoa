import argparse
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path and stdout is utf-8
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from rag.chunking import passage_preserving, sentence_aware
from rag.config import (
    BATCH_SIZE,
    EMBEDDING_DIM,
    FAISS_INDEX_PATH,
    METADATA_PATH,
)
from rag.dataset import get_dataset_path, stream_dataset_records
from rag.embeddings import MultilingualEmbeddingModel
from rag.index import VectorIndex


def main():
    parser = argparse.ArgumentParser(
        description="Build offline FAISS vector index from MSMARCO-XI dataset"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["passage_preserving", "sentence_aware"],
        default="passage_preserving",
        help="Chunking strategy to use",
    )
    parser.add_argument(
        "--sentences-per-chunk",
        type=int,
        default=2,
        help="Sentences per chunk for sentence_aware strategy",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maximum dataset records to index (default: all)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help="Batch size for embedding generation",
    )
    parser.add_argument(
        "--index-out",
        type=str,
        default=str(FAISS_INDEX_PATH),
        help="Output path for FAISS index",
    )
    parser.add_argument(
        "--metadata-out",
        type=str,
        default=str(METADATA_PATH),
        help="Output path for metadata store",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("HHGOA — INDEX BUILDER")
    print("=" * 80)
    print(f"Strategy            : {args.strategy}")
    if args.strategy == "sentence_aware":
        print(f"Sentences per Chunk : {args.sentences_per_chunk}")
    print(f"Max Records         : {args.max_records or 'All'}")
    print(f"Batch Size          : {args.batch_size}")
    print(f"Index Output        : {args.index_out}")
    print(f"Metadata Output     : {args.metadata_out}")
    print("=" * 80)

    print("\n[1/4] Locating dataset...")
    dataset_path = get_dataset_path()

    print("\n[2/4] Initializing embedding model...")
    t_model_start = time.perf_counter()
    embedder = MultilingualEmbeddingModel()
    # Use config dimension to avoid triggering lazy tokenizer download at init
    index = VectorIndex(dimension=EMBEDDING_DIM)
    t_model_end = time.perf_counter()
    print(f"Embedding model ready in {(t_model_end - t_model_start):.2f} seconds (tokenizer loads on first batch).")

    print("\n[3/4] Streaming dataset and generating embeddings...")

    total_records = 0
    total_chunks = 0
    chunk_buffer = []

    t_idx_start = time.perf_counter()

    for record in stream_dataset_records(dataset_path, max_records=args.max_records):
        total_records += 1

        if args.strategy == "passage_preserving":
            chunks = passage_preserving(record)
        else:
            chunks = sentence_aware(record, sentences_per_chunk=args.sentences_per_chunk)

        chunk_buffer.extend(chunks)

        # Process buffer in chunks of 5000 to manage RAM
        if len(chunk_buffer) >= 5000:
            doc_texts = [c.text for c in chunk_buffer]
            embeddings = embedder.embed_documents(
                doc_texts,
                batch_size=args.batch_size,
                show_progress_bar=False,
            )
            index.add_embeddings(embeddings, chunk_buffer)
            total_chunks += len(chunk_buffer)
            print(f"  Indexed {total_chunks:,} chunks from {total_records:,} records...")
            chunk_buffer = []

    # Process remaining buffer
    if chunk_buffer:
        doc_texts = [c.text for c in chunk_buffer]
        embeddings = embedder.embed_documents(
            doc_texts,
            batch_size=args.batch_size,
            show_progress_bar=False,
        )
        index.add_embeddings(embeddings, chunk_buffer)
        total_chunks += len(chunk_buffer)
        chunk_buffer = []

    t_idx_end = time.perf_counter()
    duration = t_idx_end - t_idx_start
    throughput = total_chunks / duration if duration > 0 else 0

    print(f"\nIndexing finished in {duration:.2f} seconds ({throughput:.1f} chunks/sec).")
    print(f"Total Records Processed : {total_records:,}")
    print(f"Total Chunks Indexed    : {total_chunks:,}")

    print("\n[4/4] Persisting FAISS index and metadata...")
    index.save(args.index_out, args.metadata_out)

    index_size_mb = Path(args.index_out).stat().st_size / (1024 * 1024)
    meta_size_mb = Path(args.metadata_out).stat().st_size / (1024 * 1024)

    print(f"Saved FAISS index ({index_size_mb:.2f} MB) to {args.index_out}")
    print(f"Saved Metadata    ({meta_size_mb:.2f} MB) to {args.metadata_out}")

    print("\n" + "=" * 80)
    print("INDEX BUILD COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
