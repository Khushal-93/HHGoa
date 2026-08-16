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


@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    score: float
    language: str
    query_id: int
    passage_index: int
    is_selected: bool
    strategy: str
    metadata: dict = field(default_factory=dict)


@dataclass
class TimingInfo:
    embedding_ms: float
    retrieval_ms: float
    metadata_lookup_ms: float
    total_ms: float


@dataclass
class RetrievalResponse:
    results: List[RetrievalResult]
    timing: TimingInfo


@dataclass
class EvaluationMetrics:
    total_queries: int
    recall_at_1: float
    recall_at_3: float
    recall_at_5: float
    recall_at_10: float
    embedding_p50: float
    embedding_p70: float
    embedding_p100: float
    retrieval_p50: float
    retrieval_p70: float
    retrieval_p100: float
    total_p50: float
    total_p70: float
    total_p100: float
    language_breakdown: dict = field(default_factory=dict)


@dataclass
class SourceCitation:
    chunk_id: str
    text: str
    score: float
    language: str = "hin_Deva"
    query_id: int = 0
    passage_index: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class PipelineTimingInfo:
    stt_ms: float = 0.0
    query_preprocessing_ms: float = 0.0
    query_embedding_ms: float = 0.0
    vector_search_ms: float = 0.0
    metadata_lookup_ms: float = 0.0
    retrieval_total_ms: float = 0.0
    answerability_check_ms: float = 0.0
    context_build_ms: float = 0.0
    llm_generation_ms: float = 0.0
    grounding_validation_ms: float = 0.0
    api_overhead_ms: float = 0.0
    total_pipeline_ms: float = 0.0


@dataclass
class GroundedQueryResponse:
    answer: str
    sources: List[SourceCitation]
    timing: PipelineTimingInfo
    grounded: bool
    confidence_score: float


@dataclass
class VoiceQueryResponse:
    transcript: str
    answer: str
    sources: List[SourceCitation]
    timing: PipelineTimingInfo
    grounded: bool
    confidence_score: float
