from dataclasses import dataclass, field
from typing import List


@dataclass
class Passage:
    passage_index: int
    text: str
    english_text: str
    is_selected: bool


@dataclass
class DatasetRecord:
    query_id: int
    query: str
    english_query: str
    answer: str
    english_answer: str
    query_type: str
    source_lang: str
    target_lang: str
    passages: List[Passage] = field(default_factory=list)


@dataclass
class Chunk:
    chunk_id: str
    query_id: int
    passage_index: int
    text: str
    english_text: str
    is_selected: bool
    strategy: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)