import pytest
from rag.generation import FastGroundedSynthesizer, GroundedGenerator
from rag.models import RetrievalResult


@pytest.fixture
def sample_context():
    return [
        RetrievalResult(
            chunk_id="101:0:0",
            text="A corporation is a legal entity created by individuals, stockholders, or shareholders. It operates under state laws.",
            score=0.88,
            language="hin_Deva",
            query_id=101,
            passage_index=0,
            is_selected=True,
            strategy="passage_preserving",
        )
    ]


def test_fast_synthesizer(sample_context):
    answer, source_ids = FastGroundedSynthesizer.synthesize(
        query="What is a corporation?",
        context_chunks=sample_context,
    )
    assert len(answer) > 0
    assert "corporation" in answer.lower()
    assert "101:0:0" in source_ids


def test_generator_fallback(sample_context):
    generator = GroundedGenerator()
    answer, source_ids = generator.generate(
        query="What is a corporation?",
        context_chunks=sample_context,
    )
    assert len(answer) > 0
    assert "101:0:0" in source_ids


def test_empty_context():
    generator = GroundedGenerator()
    answer, source_ids = generator.generate(
        query="Test query",
        context_chunks=[],
    )
    assert "couldn't find" in answer.lower()
    assert source_ids == []
