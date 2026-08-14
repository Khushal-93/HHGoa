from statistics import mean, median

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from rag.models import DatasetRecord, Passage
from rag.chunking import passage_preserving, sentence_aware


REPO_ID = "ai4bharat/MSMARCO-XI"
FILE_PATH = "validation/hinval.parquet"

BATCH_SIZE = 1000


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


def summarize(name, chunks):

    lengths = [
        len(chunk.text)
        for chunk in chunks
        if chunk.text
    ]

    print(f"\n{name}")
    print("-" * 60)

    print(f"Chunks           : {len(chunks):,}")

    if lengths:
        print(f"Average length   : {mean(lengths):.2f} chars")
        print(f"Median length    : {median(lengths):.2f} chars")
        print(f"Min length       : {min(lengths)} chars")
        print(f"Max length       : {max(lengths)} chars")


def main():

    print("=" * 80)
    print("HHGOA — CHUNKING BENCHMARK V0")
    print("=" * 80)

    path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILE_PATH,
        repo_type="dataset",
    )

    parquet = pq.ParquetFile(path)

    passage_chunks = []
    sentence_chunks = []

    processed = 0

    for batch in parquet.iter_batches(
        batch_size=BATCH_SIZE
    ):

        for row in batch.to_pylist():

            record = make_record(row)

            passage_chunks.extend(
                passage_preserving(record)
            )

            sentence_chunks.extend(
                sentence_aware(
                    record,
                    sentences_per_chunk=2,
                )
            )

            processed += 1

        if processed % 10_000 == 0:
            print(
                f"Processed {processed:,} records..."
            )

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"\nRecords processed: {processed:,}")

    summarize(
        "Strategy 0 — Passage Preserving",
        passage_chunks,
    )

    summarize(
        "Strategy 1 — Sentence Aware (2 sentences)",
        sentence_chunks,
    )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()