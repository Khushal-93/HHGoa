import pytest
from rag.stt import STTService, MockSTTEngine


def test_stt_mock_transcribe():
    service = STTService()
    audio = "What is a corporation?".encode("utf-8")
    transcript, stt_ms = service.transcribe(audio)

    assert transcript == "What is a corporation?"
    assert stt_ms >= 0.0


def test_stt_empty_audio():
    service = STTService()
    transcript, stt_ms = service.transcribe(b"")

    assert transcript == ""
    assert stt_ms >= 0.0


def test_stabilize_transcript():
    partials = ["what", "what is a", "what is a corporation?"]
    stable = STTService.stabilize_transcript(partials)
    assert stable == "what is a corporation?"
