from huggingface_hub import HfApi


REPO_ID = "ai4bharat/MSMARCO-XI"

FILES = [
    "train/hintrain.parquet",
    "validation/hinval.parquet",
]


def main():
    api = HfApi()

    print("=" * 80)
    print("MSMARCO-XI — REMOTE DATASET METADATA")
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

        size_mb = info.size / (1024 * 1024)
        size_gb = info.size / (1024 * 1024 * 1024)

        print(f"Size      : {info.size:,} bytes")
        print(f"Size      : {size_mb:.2f} MB")
        print(f"Size      : {size_gb:.3f} GB")
        print(f"Blob ID   : {info.blob_id}")

        if info.lfs:
            print(f"SHA256    : {info.lfs.sha256}")


if __name__ == "__main__":
    main()