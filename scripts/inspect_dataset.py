from huggingface_hub import HfApi
import pyarrow.parquet as pq
import tempfile
import os


REPO_ID = "ai4bharat/MSMARCO-XI"
FILE_PATH = "train/hintrain.parquet"


def main():
    print("=" * 80)
    print("HHGOA — MSMARCO-XI PARQUET INSPECTION")
    print("=" * 80)

    print(f"\nRepository : {REPO_ID}")
    print(f"File       : {FILE_PATH}")

    api = HfApi()

    print("\nDownloading Parquet file for metadata inspection...")

    local_path = api.hf_hub_download(
        repo_id=REPO_ID,
        filename=FILE_PATH,
        repo_type="dataset",
    )

    print(f"\nLocal cache path:")
    print(local_path)

    print("\nReading Parquet metadata...")

    parquet_file = pq.ParquetFile(local_path)

    print("\n" + "=" * 80)
    print("FILE METADATA")
    print("=" * 80)

    print(f"\nNumber of row groups : {parquet_file.num_row_groups}")
    print(f"Number of rows      : {parquet_file.metadata.num_rows}")
    print(f"Number of columns   : {parquet_file.metadata.num_columns}")

    print("\nColumns:")

    for field in parquet_file.schema_arrow:
        print(f"  - {field.name}: {field.type}")

    print("\n" + "=" * 80)
    print("FIRST ROW GROUP")
    print("=" * 80)

    table = parquet_file.read_row_group(0)

    print(f"\nRows in first row group: {table.num_rows}")

    print("\nColumns:")
    for column in table.column_names:
        print(f"  - {column}")

    print("\n" + "=" * 80)
    print("FIRST EXAMPLE")
    print("=" * 80)

    first = table.slice(0, 1).to_pylist()[0]

    for key, value in first.items():

        print(f"\n[{key}]")

        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                print(f"  {nested_key}: {nested_value}")

        else:
            print(value)

    print("\n" + "=" * 80)
    print("INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()