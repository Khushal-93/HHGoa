import pytest
from rag.guardrails import AnswerabilityGate, CitationValidator, REFUSAL_MESSAGE
from rag.models import RetrievalResult


def test_answerability_gate_accept():
    gate = AnswerabilityGate(threshold=0.40)
    results = [
        RetrievalResult(
            chunk_id="101:0:0",
            text="High confidence result",
            score=0.85,
            language="hin_Deva",
            query_id=101,
            passage_index=0,
            is_selected=True,
            strategy="passage_preserving",
        )
    ]
    is_answerable, top_score, reason = gate.evaluate(results)
    assert is_answerable is True
    assert top_score == 0.85


def test_answerability_gate_refuse():
    gate = AnswerabilityGate(threshold=0.40)
    results = [
        RetrievalResult(
            chunk_id="999:0:0",
            text="Low relevance random result",
            score=0.15,
            language="hin_Deva",
            query_id=999,
            passage_index=0,
            is_selected=False,
            strategy="passage_preserving",
        )
    ]
    is_answerable, top_score, reason = gate.evaluate(results)
    assert is_answerable is False
    assert top_score == 0.15


def test_citation_validator():
    retrieved = [
        RetrievalResult(
            chunk_id="c1",
            text="Text 1",
            score=0.9,
            language="hin_Deva",
            query_id=1,
            passage_index=0,
            is_selected=True,
            strategy="passage_preserving",
        ),
        RetrievalResult(
            chunk_id="c2",
            text="Text 2",
            score=0.8,
            language="hin_Deva",
            query_id=1,
            passage_index=1,
            is_selected=False,
            strategy="passage_preserving",
        ),
    ]

    # Valid ID + fake ID
    citations = CitationValidator.validate_and_build(
        returned_source_ids=["c1", "fake_id_123"],
        retrieved_results=retrieved,
    )
    assert len(citations) == 1
    assert citations[0].chunk_id == "c1"
