from rag.models import DatasetRecord, Passage
from rag.chunking import (
    passage_preserving,
    sentence_aware,
    split_sentences,
)


def make_record(text="यह पहला वाक्य है। यह दूसरा वाक्य है। यह तीसरा वाक्य है।"):
    return DatasetRecord(
        query_id=123,
        query="कॉर्पोरेशन क्या है?",
        english_query="what is a corporation?",
        answer="एक कंपनी...",
        english_answer="A corporation is a company...",
        query_type="DESCRIPTION",
        source_lang="eng_Latn",
        target_lang="hin_Deva",
        passages=[
            Passage(
                passage_index=0,
                text=text,
                english_text="This is an English passage.",
                is_selected=True,
            )
        ],
    )


def test_passage_preserving():

    record = make_record()

    chunks = passage_preserving(record)

    assert len(chunks) == 1
    assert chunks[0].text == record.passages[0].text
    assert chunks[0].is_selected is True
    assert chunks[0].strategy == "passage_preserving"


def test_split_sentences_hindi():

    text = "यह पहला वाक्य है। यह दूसरा वाक्य है।"

    sentences = split_sentences(text)

    assert sentences == [
        "यह पहला वाक्य है।",
        "यह दूसरा वाक्य है।",
    ]


def test_sentence_aware():

    record = make_record()

    chunks = sentence_aware(
        record,
        sentences_per_chunk=2,
    )

    assert len(chunks) == 2

    assert chunks[0].text == (
        "यह पहला वाक्य है। यह दूसरा वाक्य है।"
    )

    assert chunks[1].text == (
        "यह तीसरा वाक्य है।"
    )


def test_sentence_aware_preserves_metadata():

    record = make_record()

    chunks = sentence_aware(record)

    assert all(
        chunk.query_id == 123
        for chunk in chunks
    )

    assert all(
        chunk.passage_index == 0
        for chunk in chunks
    )

    assert all(
        chunk.is_selected is True
        for chunk in chunks
    )

    assert all(
        chunk.strategy == "sentence_aware"
        for chunk in chunks
    )


def test_empty_passage():

    record = make_record(text="")

    chunks = sentence_aware(record)

    assert chunks == []


def test_invalid_sentence_window():

    record = make_record()

    try:
        sentence_aware(
            record,
            sentences_per_chunk=0,
        )
        assert False
    except ValueError:
        assert True