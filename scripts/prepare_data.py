import sys
import argparse
from pathlib import Path

# Ensure project root is in sys.path and stdout is utf-8
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from rag.dataset import get_dataset_path, stream_dataset_records


def main():
    parser = argparse.ArgumentParser(description="Download and inspect MSMARCO-XI dataset")
    parser.add_argument("--max-records", type=int, default=100, help="Number of records to sample")
    args = parser.parse_args()

    print("=" * 80)
    print("HHGOA — DATASET PREPARATION & INSPECTION")
    print("=" * 80)

    print("\nDownloading/verifying dataset...")
    path = get_dataset_path()
    print(f"Local Parquet file: {path}")

    records = list(stream_dataset_records(path, max_records=args.max_records))
    print(f"\nSuccessfully loaded sample of {len(records)} DatasetRecord objects.")

    if records:
        sample = records[0]
        print("\nSample Record:")
        print(f"  Query ID: {sample.query_id}")
        print(f"  Query: {sample.query}")
        print(f"  Eng Query: {sample.english_query}")
        print(f"  Passages Count: {len(sample.passages)}")
        selected_count = sum(1 for p in sample.passages if p.is_selected)
        print(f"  Selected Passages Count: {selected_count}")

    print("\n" + "=" * 80)
    print("PREPARATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
