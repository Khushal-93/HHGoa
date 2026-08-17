from statistics import mean, median

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from rag.models import DatasetRecord, Passage
from rag.chunking import adaptive_token


REPO_ID = "ai4bharat/MSMARCO-XI"
FILE_PATH = "validation/hinval.parquet"

BATCH_SIZE = 1000

TOKEN_LIMITS = [64 ,128, 256]


def make_record(row):
    passages = row["passages"]

    english = passages["English_passages"]
    translated = passages["Translated_passages"]
    selected = passages["is_selected"]

    passage_objects = [
        Passage(
            passage_index=i,
            text=translated[i],
            english_text=english[i],
            is_selected=bool(selected[i]),
        )
        for i in range(len(translated))
    ]

    return DatasetRecord(
        query_id=row["query_id"],
        query=row["query"],
        english_query=row["Eng_Query"],
        answer=row["Answer"],
        english_answer=row["Eng_Answer"],
        query_type=row["query_type"],
        source_lang=row["source_lang"],
        target_lang=row["target_lang"],
        passages=passage_objects,
    )


def benchmark_limit(parquet, max_tokens):

    chunk_count = 0
    token_lengths = []
    char_lengths = []

    selected_chunks = 0

    processed = 0

    for batch in parquet.iter_batches(
        batch_size=BATCH_SIZE
    ):

        for row in batch.to_pylist():

            record = make_record(row)

            chunks = adaptive_token(
                record,
                max_tokens=max_tokens,
            )

            for chunk in chunks:

                chunk_count += 1

                tokens = chunk.metadata[
                    "actual_tokens"
                ]

                token_lengths.append(tokens)
                char_lengths.append(
                    len(chunk.text)
                )

                if chunk.is_selected:
                    selected_chunks += 1

            processed += 1

        if processed % 10_000 == 0:

            print(
                f"    Processed "
                f"{processed:,} records..."
            )

    print()
    print(
        f"    Records        : {processed:,}"
    )

    print(
        f"    Chunks         : {chunk_count:,}"
    )

    print(
        f"    Selected chunks: {selected_chunks:,}"
    )

    print(
        f"    Avg tokens     : "
        f"{mean(token_lengths):.2f}"
    )

    print(
        f"    Median tokens  : "
        f"{median(token_lengths):.2f}"
    )

    print(
        f"    Max tokens     : "
        f"{max(token_lengths)}"
    )

    print(
        f"    Avg chars      : "
        f"{mean(char_lengths):.2f}"
    )

    print(
        f"    Median chars   : "
        f"{median(char_lengths):.2f}"
    )

    print(
        f"    Max chars      : "
        f"{max(char_lengths)}"
    )


def main():

    print("=" * 80)
    print("HHGOA — STRATEGY 2 ADAPTIVE CHUNKING BENCHMARK")
    print("=" * 80)

    print()
    print("Downloading / locating validation dataset...")

    path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILE_PATH,
        repo_type="dataset",
    )

    parquet = pq.ParquetFile(path)

    print()
    print("Dataset ready.")
    print(
        f"Rows available: "
        f"{parquet.metadata.num_rows:,}"
    )

    for max_tokens in TOKEN_LIMITS:

        print()
        print("=" * 80)
        print(
            f"STRATEGY 2 — MAX {max_tokens} TOKENS"
        )
        print("=" * 80)

        benchmark_limit(
            parquet,
            max_tokens,
        )

    print()
    print("=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()