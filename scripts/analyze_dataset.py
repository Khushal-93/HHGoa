from collections import Counter
from statistics import mean, median

from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq


REPO_ID = "ai4bharat/MSMARCO-XI"
FILE_PATH = "validation/hinval.parquet"

BATCH_SIZE = 1000


def text_length(text):
    if not text:
        return 0

    return len(text)


def main():
    print("=" * 80)
    print("HHGOA — MSMARCO-XI DATASET ANALYSIS")
    print("=" * 80)

    local_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILE_PATH,
        repo_type="dataset",
    )

    parquet = pq.ParquetFile(local_path)

    total_records = 0

    passage_counts = []
    selected_counts = []

    query_lengths = []
    answer_lengths = []
    passage_lengths = []

    query_types = Counter()

    zero_selected = 0
    multiple_selected = 0

    empty_queries = 0
    empty_answers = 0
    empty_passages = 0

    duplicate_passages = 0

    language_pairs = Counter()

    for batch_number, batch in enumerate(
        parquet.iter_batches(batch_size=BATCH_SIZE)
    ):
        rows = batch.to_pylist()

        for row in rows:

            total_records += 1

            query = row.get("query") or ""
            answer = row.get("Answer") or ""

            query_lengths.append(text_length(query))
            answer_lengths.append(text_length(answer))

            query_types[row.get("query_type") or "UNKNOWN"] += 1

            source_lang = row.get("source_lang")
            target_lang = row.get("target_lang")

            language_pairs[(source_lang, target_lang)] += 1

            if not query.strip():
                empty_queries += 1

            if not answer.strip():
                empty_answers += 1

            passages = row.get("passages") or {}

            english_passages = passages.get("English_passages") or []
            translated_passages = passages.get("Translated_passages") or []
            selected = passages.get("is_selected") or []

            passage_count = len(translated_passages)

            passage_counts.append(passage_count)

            selected_count = sum(
                1 for value in selected
                if value == 1
            )

            selected_counts.append(selected_count)

            if selected_count == 0:
                zero_selected += 1

            if selected_count > 1:
                multiple_selected += 1

            seen = set()

            for index, passage in enumerate(translated_passages):

                passage = passage or ""

                passage_lengths.append(
                    text_length(passage)
                )

                if not passage.strip():
                    empty_passages += 1

                normalized = passage.strip()

                if normalized in seen and normalized:
                    duplicate_passages += 1

                seen.add(normalized)

            # Check English/Hindi passage alignment.
            if len(english_passages) != len(translated_passages):
                print(
                    f"WARNING: passage alignment mismatch "
                    f"at query_id={row.get('query_id')}"
                )

        if (batch_number + 1) % 10 == 0:
            print(
                f"Processed {total_records:,} records..."
            )

    print("\n")
    print("=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)

    print(f"\nTotal records          : {total_records:,}")

    print(
        f"Average passages/query : "
        f"{mean(passage_counts):.2f}"
    )

    print(
        f"Median passages/query  : "
        f"{median(passage_counts):.2f}"
    )

    print(
        f"Min passages/query     : "
        f"{min(passage_counts)}"
    )

    print(
        f"Max passages/query     : "
        f"{max(passage_counts)}"
    )

    print("\nSelected passages/query:")

    print(
        f"Average selected       : "
        f"{mean(selected_counts):.2f}"
    )

    print(
        f"Queries with 0 selected : "
        f"{zero_selected:,}"
    )

    print(
        f"Queries with >1 selected: "
        f"{multiple_selected:,}"
    )

    print("\nText statistics:")

    print(
        f"Average query length   : "
        f"{mean(query_lengths):.2f} characters"
    )

    print(
        f"Median query length    : "
        f"{median(query_lengths):.2f} characters"
    )

    print(
        f"Average answer length  : "
        f"{mean(answer_lengths):.2f} characters"
    )

    print(
        f"Average passage length : "
        f"{mean(passage_lengths):.2f} characters"
    )

    print(
        f"Median passage length  : "
        f"{median(passage_lengths):.2f} characters"
    )

    print("\nData quality:")

    print(f"Empty queries          : {empty_queries:,}")
    print(f"Empty answers          : {empty_answers:,}")
    print(f"Empty passages         : {empty_passages:,}")
    print(f"Duplicate passages     : {duplicate_passages:,}")

    print("\nQuery types:")

    for query_type, count in query_types.most_common():
        print(
            f"  {query_type:<25} {count:,}"
        )

    print("\nLanguage pairs:")

    for (source, target), count in language_pairs.items():
        print(
            f"  {source} → {target}: {count:,}"
        )

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()