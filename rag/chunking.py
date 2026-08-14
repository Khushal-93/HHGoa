import re
from typing import List

from rag.models import DatasetRecord, Chunk


# Hindi/English sentence boundaries.
SENTENCE_PATTERN = re.compile(
    r"(?<=[.!?।॥])\s+"
)


def split_sentences(text: str) -> List[str]:
    """
    Split text using common English + Hindi sentence terminators.

    Supported:
    . ! ? । ॥
    """

    if not text or not text.strip():
        return []

    sentences = SENTENCE_PATTERN.split(text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def passage_preserving(record: DatasetRecord) -> List[Chunk]:
    """
    Strategy 0 — Passage Preserving.

    Each original dataset passage becomes one retrieval chunk.
    """

    chunks = []

    for passage in record.passages:

        chunks.append(
            Chunk(
                chunk_id=(
                    f"{record.query_id}:"
                    f"{passage.passage_index}:0"
                ),
                query_id=record.query_id,
                passage_index=passage.passage_index,
                text=passage.text,
                english_text=passage.english_text,
                is_selected=passage.is_selected,
                strategy="passage_preserving",
                chunk_index=0,
            )
        )

    return chunks


def sentence_aware(
    record: DatasetRecord,
    sentences_per_chunk: int = 2,
) -> List[Chunk]:
    """
    Strategy 1 — Sentence Aware.

    Passages are split into sentences and grouped into
    configurable sentence windows.

    Short passages remain intact.
    """

    if sentences_per_chunk < 1:
        raise ValueError(
            "sentences_per_chunk must be >= 1"
        )

    chunks = []

    for passage in record.passages:

        sentences = split_sentences(passage.text)

        if not sentences:
            continue

        for chunk_index in range(
            0,
            len(sentences),
            sentences_per_chunk,
        ):

            chunk_sentences = sentences[
                chunk_index:
                chunk_index + sentences_per_chunk
            ]

            text = " ".join(chunk_sentences)

            chunks.append(
                Chunk(
                    chunk_id=(
                        f"{record.query_id}:"
                        f"{passage.passage_index}:"
                        f"{chunk_index}"
                    ),
                    query_id=record.query_id,
                    passage_index=passage.passage_index,
                    text=text,
                    english_text=passage.english_text,
                    is_selected=passage.is_selected,
                    strategy="sentence_aware",
                    chunk_index=chunk_index,
                    metadata={
                        "sentences_per_chunk": sentences_per_chunk,
                        "sentence_count": len(chunk_sentences),
                    },
                )
            )

    return chunks