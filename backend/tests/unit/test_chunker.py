"""Unit tests for curriculum section chunking."""

from documents.chunker import create_curriculum_chunks, _split_curriculum_sections


def test_split_curriculum_sections_on_numbered_headings():
    text = (
        "Introduction to the village. "
        "1. Land is fixed. Farming is the main activity in Palampur. "
        "5. Who will provide the labour? Farm labourers are paid wages."
    )
    sections = _split_curriculum_sections(text)
    assert len(sections) >= 2
    labour_sections = [section for section in sections if "labour" in section.lower()]
    assert labour_sections


def test_create_curriculum_chunks_keeps_sections_together():
    text = (
        "Overview of Palampur. "
        "2. Is there a way one can grow more? Multiple cropping helps. "
        "Electricity came early to Palampur and transformed irrigation."
    )
    chunks = create_curriculum_chunks(text, chunk_size=200, overlap=20)
    assert chunks
    assert any("electricity" in chunk.lower() for chunk in chunks)
