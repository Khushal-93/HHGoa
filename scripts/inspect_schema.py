from huggingface_hub import HfApi


REPO_ID = "ai4bharat/MSMARCO-XI"

FILES = [
    "train/hintrain.parquet",
    "validation/hinval.parquet",
]


def main():
    api = HfApi()

    print("=" * 80)
    print("MSMARCO-XI — DATASET SCHEMA INSPECTION")
    print("=" * 80)

    for file_path in FILES:
        print("\n" + "-" * 80)
        print(file_path)
        print("-" * 80)

        info = api.get_paths_info(
            REPO_ID,
            paths=file_path,
            repo_type="dataset",
        )[0]

        print(f"File size : {info.size:,} bytes")

        print("\nRepository file metadata:")
        print(info)


if __name__ == "__main__":
    main()