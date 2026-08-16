from typing import Generator, Optional
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from rag.config import DATASET_REPO, DATASET_FILE
from rag.models import DatasetRecord, Passage


def get_dataset_path(
    repo_id: str = DATASET_REPO,
    filename: str = DATASET_FILE,
) -> str:
    """
    Download or return local cached path for the Parquet dataset file.
    """
    try:
        return hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset",
            local_files_only=True,
        )
    except Exception:
        return hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset",
        )


def parse_row_to_record(row: dict) -> DatasetRecord:
    """
    Parse a single raw dataset dictionary into a DatasetRecord object.
    """
    passages_dict = row.get("passages") or {}
    english_passages = passages_dict.get("English_passages") or []
    translated_passages = passages_dict.get("Translated_passages") or []
    is_selected = passages_dict.get("is_selected") or []

    passage_objects = []
    num_passages = len(translated_passages)

    for i in range(num_passages):
        eng_text = english_passages[i] if i < len(english_passages) else ""
        selected = bool(is_selected[i]) if i < len(is_selected) else False
        passage_objects.append(
            Passage(
                passage_index=i,
                text=translated_passages[i] or "",
                english_text=eng_text or "",
                is_selected=selected,
            )
        )

    return DatasetRecord(
        query_id=row.get("query_id", 0),
        query=row.get("query") or "",
        english_query=row.get("Eng_Query") or "",
        answer=row.get("Answer") or "",
        english_answer=row.get("Eng_Answer") or "",
        query_type=row.get("query_type") or "UNKNOWN",
        source_lang=row.get("source_lang") or "eng_Latn",
        target_lang=row.get("target_lang") or "hin_Deva",
        passages=passage_objects,
    )


def stream_dataset_records(
    parquet_path: str,
    max_records: Optional[int] = None,
    batch_size: int = 1000,
) -> Generator[DatasetRecord, None, None]:
    """
    Stream DatasetRecord objects from a local parquet file without loading
    the entire dataset into RAM.
    """
    parquet_file = pq.ParquetFile(parquet_path)
    count = 0

    for batch in parquet_file.iter_batches(batch_size=batch_size):
        rows = batch.to_pylist()
        for row in rows:
            record = parse_row_to_record(row)
            yield record
            count += 1
            if max_records is not None and count >= max_records:
                return
