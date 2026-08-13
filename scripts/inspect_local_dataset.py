from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq


REPO_ID = "ai4bharat/MSMARCO-XI"
FILE_PATH = "validation/hinval.parquet"


def main():
    print("=" * 80)
    print("HHGOA — MSMARCO-XI LOCAL DATASET INSPECTION")
    print("=" * 80)

    print("\nLocating downloaded dataset...")

    local_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILE_PATH,
        repo_type="dataset",
    )

    print(f"\nDataset path:")
    print(local_path)

    print("\nOpening Parquet file...")

    parquet = pq.ParquetFile(local_path)

    print("\n" + "=" * 80)
    print("FILE INFORMATION")
    print("=" * 80)

    print(f"\nRows       : {parquet.metadata.num_rows:,}")
    print(f"Columns    : {parquet.metadata.num_columns}")
    print(f"Row groups: {parquet.num_row_groups}")

    print("\n" + "=" * 80)
    print("SCHEMA")
    print("=" * 80)

    for field in parquet.schema_arrow:
        print(f"\n{field.name}")
        print(f"  Type: {field.type}")

    print("\n" + "=" * 80)
    print("READING FIRST ROW")
    print("=" * 80)

    # Only read the first row group.
    table = parquet.read_row_group(0)

    print(f"\nRows in first row group: {table.num_rows}")

    first_row = table.slice(0, 1).to_pylist()[0]

    for key, value in first_row.items():
        print("\n" + "-" * 80)
        print(f"FIELD: {key}")
        print("-" * 80)
        print(value)

    print("\n" + "=" * 80)
    print("INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()