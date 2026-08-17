import re
from typing import List

from transformers import AutoTokenizer

from rag.models import DatasetRecord, Chunk


# ============================================================
# Configuration
# ============================================================

TOKENIZER_NAME = "google/muril-base-cased"

_tokenizer = None

SENTENCE_PATTERN = re.compile(
    r"(?<=[.!?।॥])\s+"
)


# ============================================================
# Tokenizer
# ============================================================

def get_tokenizer():
    """
    Lazily load the MuRIL tokenizer.

    We only use the tokenizer for token counting.
    We are NOT loading or running the MuRIL model.
    """

    global _tokenizer

    if _tokenizer is None:

        _tokenizer = AutoTokenizer.from_pretrained(
            TOKENIZER_NAME
        )

        # We may inspect long passages while counting tokens.
        # This prevents the default 512-token warning.
        _tokenizer.model_max_length = 10**9

    return _tokenizer


def count_tokens(text: str) -> int:
    """
    Count tokens without special tokens.
    """

    if not text:
        return 0

    tokenizer = get_tokenizer()

    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
    )

    return len(token_ids)


# ============================================================
# Sentence Splitting
# ============================================================

def split_sentences(text: str) -> List[str]:
    """
    Split English/Hindi text into sentences.

    Supports common punctuation:

        .
        !
        ?
        ।
        ॥
    """

    if not text or not text.strip():
        return []

    sentences = SENTENCE_PATTERN.split(
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# Strategy 0 — Passage Preserving
# ============================================================

def passage_preserving(
    record: DatasetRecord,
) -> List[Chunk]:
    """
    Strategy 0.

    Keep every original dataset passage as one chunk.

    This provides our baseline.
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


# ============================================================
# Strategy 1 — Sentence Aware
# ============================================================

def sentence_aware(
    record: DatasetRecord,
    sentences_per_chunk: int = 2,
) -> List[Chunk]:
    """
    Strategy 1.

    Split passages into sentences and group them.

    Example:

        Sentence 1
        Sentence 2
        Sentence 3
        Sentence 4

    becomes:

        Chunk 1 = Sentence 1 + Sentence 2
        Chunk 2 = Sentence 3 + Sentence 4
    """

    if sentences_per_chunk < 1:
        raise ValueError(
            "sentences_per_chunk must be >= 1"
        )

    chunks = []

    for passage in record.passages:

        sentences = split_sentences(
            passage.text
        )

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

            text = " ".join(
                chunk_sentences
            )

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
                        "sentences_per_chunk":
                            sentences_per_chunk,
                        "sentence_count":
                            len(chunk_sentences),
                    },
                )
            )

    return chunks


# ============================================================
# Token Windows
# ============================================================

def token_windows(
    text: str,
    max_tokens: int,
) -> List[str]:
    """
    Split text into hard token-bounded windows.

    The decoded text is re-tokenized before being accepted.
    This helps ensure the final text remains within
    max_tokens after decoding.
    """

    if not text or not text.strip():
        return []

    if max_tokens < 1:
        raise ValueError(
            "max_tokens must be >= 1"
        )

    tokenizer = get_tokenizer()

    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
    )

    windows = []

    start = 0

    while start < len(token_ids):

        end = min(
            start + max_tokens,
            len(token_ids),
        )

        found_window = False

        while end > start:

            window_ids = token_ids[
                start:end
            ]

            window_text = tokenizer.decode(
                window_ids,
                skip_special_tokens=True,
            ).strip()

            actual_ids = tokenizer.encode(
                window_text,
                add_special_tokens=False,
            )

            if len(actual_ids) <= max_tokens:

                windows.append(
                    window_text
                )

                start = end

                found_window = True

                break

            end -= 1

        if not found_window:

            raise RuntimeError(
                "Unable to create a valid "
                "token-bounded chunk."
            )

    return windows


# ============================================================
# Strategy 2 — Adaptive Token
# ============================================================

def adaptive_token(
    record: DatasetRecord,
    max_tokens: int = 128,
) -> List[Chunk]:
    """
    Strategy 2 — Adaptive Sentence + Token Ceiling.

    Rules:

    1. Split each passage into sentences.
    2. Combine multiple sentences while staying
       under max_tokens.
    3. If a single sentence is larger than max_tokens,
       split that sentence using token windows.
    4. Preserve dataset metadata.
    """

    if max_tokens < 1:
        raise ValueError(
            "max_tokens must be >= 1"
        )

    chunks = []

    for passage in record.passages:

        if not passage.text or not passage.text.strip():
            continue

        sentences = split_sentences(
            passage.text
        )

        if not sentences:
            continue

        current_sentences = []
        current_tokens = 0
        chunk_index = 0

        def flush_current():

            nonlocal current_sentences
            nonlocal current_tokens
            nonlocal chunk_index

            if not current_sentences:
                return

            text = " ".join(
                current_sentences
            ).strip()

            actual_tokens = count_tokens(
                text
            )

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
                    strategy="adaptive_token",
                    chunk_index=chunk_index,
                    metadata={
                        "max_tokens":
                            max_tokens,
                        "actual_tokens":
                            actual_tokens,
                        "sentence_count":
                            len(current_sentences),
                    },
                )
            )

            chunk_index += 1

            current_sentences = []

            current_tokens = 0

        for sentence in sentences:

            sentence_tokens = count_tokens(
                sentence
            )

            # ------------------------------------------------
            # Case 1:
            # The sentence itself is too large.
            # ------------------------------------------------

            if sentence_tokens > max_tokens:

                # Save the current chunk first.
                flush_current()

                windows = token_windows(
                    sentence,
                    max_tokens,
                )

                for window in windows:

                    actual_tokens = count_tokens(
                        window
                    )

                    chunks.append(
                        Chunk(
                            chunk_id=(
                                f"{record.query_id}:"
                                f"{passage.passage_index}:"
                                f"{chunk_index}"
                            ),
                            query_id=record.query_id,
                            passage_index=passage.passage_index,
                            text=window,
                            english_text=passage.english_text,
                            is_selected=passage.is_selected,
                            strategy="adaptive_token",
                            chunk_index=chunk_index,
                            metadata={
                                "max_tokens":
                                    max_tokens,
                                "actual_tokens":
                                    actual_tokens,
                                "overflow_sentence":
                                    True,
                            },
                        )
                    )

                    chunk_index += 1

                continue

            # ------------------------------------------------
            # Case 2:
            # Adding this sentence would exceed the limit.
            # ------------------------------------------------

            if (
                current_tokens + sentence_tokens
                > max_tokens
            ):

                flush_current()

            current_sentences.append(
                sentence
            )

            current_tokens += sentence_tokens

        # Flush final chunk.
        flush_current()

    return chunks