import time
from typing import List, Optional

from rag.config import (
    CONFIDENCE_THRESHOLD,
    DEFAULT_TOP_K,
    MAX_CONTEXT_CHUNKS,
)
from rag.generation import GroundedGenerator
from rag.guardrails import AnswerabilityGate, CitationValidator, REFUSAL_MESSAGE
from rag.models import (
    GroundedQueryResponse,
    PipelineTimingInfo,
    RetrievalResult,
    SourceCitation,
    VoiceQueryResponse,
)
from rag.retrieval import RetrievalService
from rag.stt import STTService


class RAGOrchestrator:
    """
    Unified end-to-end RAG orchestrator.
    Coordinates STT -> Query Processing -> Vector Retrieval -> Answerability Gate -> Minimal Context -> LLM Generation -> Citation Validation -> Latency Breakdown.
    """

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        answerability_gate: Optional[AnswerabilityGate] = None,
        generator: Optional[GroundedGenerator] = None,
        validator: Optional[CitationValidator] = None,
        stt_service: Optional[STTService] = None,
    ):
        self.retrieval_service = (
            retrieval_service if retrieval_service is not None else RetrievalService()
        )
        self.answerability_gate = (
            answerability_gate if answerability_gate is not None else AnswerabilityGate(CONFIDENCE_THRESHOLD)
        )
        self.generator = (
            generator if generator is not None else GroundedGenerator()
        )
        self.validator = (
            validator if validator is not None else CitationValidator()
        )
        self.stt_service = (
            stt_service if stt_service is not None else STTService()
        )

    def run_text_pipeline(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> GroundedQueryResponse:
        """
        Execute full text RAG pipeline with high-resolution monotonic timer breakdown.
        """
        t_pipeline_start = time.perf_counter()

        # Step 1: Preprocessing
        t_prep_start = time.perf_counter()
        clean_query = query.strip() if query else ""
        t_prep_end = time.perf_counter()
        query_preprocessing_ms = (t_prep_end - t_prep_start) * 1000.0

        if not clean_query:
            t_pipeline_end = time.perf_counter()
            return GroundedQueryResponse(
                answer="Please provide a non-empty query string.",
                sources=[],
                timing=PipelineTimingInfo(
                    query_preprocessing_ms=round(query_preprocessing_ms, 3),
                    total_pipeline_ms=round((t_pipeline_end - t_pipeline_start) * 1000.0, 3),
                ),
                grounded=False,
                confidence_score=0.0,
            )

        # Step 2: Vector Retrieval Core
        retrieval_response = self.retrieval_service.retrieve(
            query=clean_query,
            top_k=top_k,
        )

        retrieved_results = retrieval_response.results
        ret_timing = retrieval_response.timing

        # Step 3: Answerability Gate
        t_gate_start = time.perf_counter()
        is_answerable, top_score, refusal_reason = self.answerability_gate.evaluate(
            retrieved_results
        )
        t_gate_end = time.perf_counter()
        answerability_check_ms = (t_gate_end - t_gate_start) * 1000.0

        if not is_answerable:
            t_pipeline_end = time.perf_counter()
            return GroundedQueryResponse(
                answer=REFUSAL_MESSAGE,
                sources=[],
                timing=PipelineTimingInfo(
                    query_preprocessing_ms=round(query_preprocessing_ms, 3),
                    query_embedding_ms=ret_timing.embedding_ms,
                    vector_search_ms=ret_timing.retrieval_ms,
                    metadata_lookup_ms=ret_timing.metadata_lookup_ms,
                    retrieval_total_ms=ret_timing.total_ms,
                    answerability_check_ms=round(answerability_check_ms, 3),
                    total_pipeline_ms=round((t_pipeline_end - t_pipeline_start) * 1000.0, 3),
                ),
                grounded=False,
                confidence_score=round(top_score, 4),
            )

        # Step 4: Minimal Context Selection
        t_ctx_start = time.perf_counter()
        selected_context = retrieved_results[:MAX_CONTEXT_CHUNKS]
        t_ctx_end = time.perf_counter()
        context_build_ms = (t_ctx_end - t_ctx_start) * 1000.0

        # Step 5: Grounded LLM Generation
        t_gen_start = time.perf_counter()
        raw_answer, returned_source_ids = self.generator.generate(
            query=clean_query,
            context_chunks=selected_context,
        )
        t_gen_end = time.perf_counter()
        llm_generation_ms = (t_gen_end - t_gen_start) * 1000.0

        # Step 6: Source Citation Validation
        t_val_start = time.perf_counter()
        validated_citations = self.validator.validate_and_build(
            returned_source_ids=returned_source_ids,
            retrieved_results=selected_context,
        )
        t_val_end = time.perf_counter()
        grounding_validation_ms = (t_val_end - t_val_start) * 1000.0

        t_pipeline_end = time.perf_counter()
        total_pipeline_ms = (t_pipeline_end - t_pipeline_start) * 1000.0

        return GroundedQueryResponse(
            answer=raw_answer,
            sources=validated_citations,
            timing=PipelineTimingInfo(
                stt_ms=0.0,
                query_preprocessing_ms=round(query_preprocessing_ms, 3),
                query_embedding_ms=ret_timing.embedding_ms,
                vector_search_ms=ret_timing.retrieval_ms,
                metadata_lookup_ms=ret_timing.metadata_lookup_ms,
                retrieval_total_ms=ret_timing.total_ms,
                answerability_check_ms=round(answerability_check_ms, 3),
                context_build_ms=round(context_build_ms, 3),
                llm_generation_ms=round(llm_generation_ms, 3),
                grounding_validation_ms=round(grounding_validation_ms, 3),
                api_overhead_ms=0.0,
                total_pipeline_ms=round(total_pipeline_ms, 3),
            ),
            grounded=True,
            confidence_score=round(top_score, 4),
        )

    def run_voice_pipeline(
        self,
        audio_bytes: bytes,
        language: str = "hin_Deva",
        allow_mock: bool = False,
    ) -> VoiceQueryResponse:
        """
        Execute full Voice RAG pipeline: STT -> Text RAG -> VoiceQueryResponse.
        """
        t_voice_start = time.perf_counter()

        # Step 1: Speech-to-Text Transcription
        transcript, stt_ms = self.stt_service.transcribe(
            audio_bytes=audio_bytes,
            language=language,
            allow_mock=allow_mock,
        )

        if not transcript or not transcript.strip():
            t_voice_end = time.perf_counter()
            return VoiceQueryResponse(
                transcript="",
                answer="Could not transcribe audio input.",
                sources=[],
                timing=PipelineTimingInfo(
                    stt_ms=stt_ms,
                    total_pipeline_ms=round((t_voice_end - t_voice_start) * 1000.0, 3),
                ),
                grounded=False,
                confidence_score=0.0,
            )

        # Step 2: Execute Text RAG Pipeline
        text_response = self.run_text_pipeline(query=transcript)

        # Merge STT timing into total voice pipeline timing
        t_voice_end = time.perf_counter()
        total_voice_ms = (t_voice_end - t_voice_start) * 1000.0

        timing = text_response.timing
        timing.stt_ms = stt_ms
        timing.total_pipeline_ms = round(total_voice_ms, 3)

        return VoiceQueryResponse(
            transcript=transcript,
            answer=text_response.answer,
            sources=text_response.sources,
            timing=timing,
            grounded=text_response.grounded,
            confidence_score=text_response.confidence_score,
        )
