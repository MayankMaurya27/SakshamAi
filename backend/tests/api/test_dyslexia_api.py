"""API tests for dyslexia accessibility mode."""


def test_ask_dyslexia_returns_accessibility_block(client, monkeypatch):
    monkeypatch.setattr(
        "api.ask.answer_question",
        lambda **kwargs: "• Photosynthesis uses sunlight.\n\n• Plants make food in leaves.",
    )

    response = client.post(
        "/ask",
        json={
            "question": "What is photosynthesis?",
            "source": "saksham",
            "class_level": 7,
            "subject": "Science",
            "chapter": "Nutrition in Plants",
            "accessibility_profile": "dyslexia",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "accessibility" in data
    assert data["accessibility"]["profile"] == "dyslexia"
    assert data["accessibility"]["display_hints"]["prefer_audio"] is True
    assert data["accessibility"]["reading_segments"]


def test_ask_without_profile_unchanged(client, monkeypatch):
    monkeypatch.setattr(
        "api.ask.answer_question",
        lambda **kwargs: "Plain answer text.",
    )
    response = client.post(
        "/ask",
        json={
            "question": "What is force?",
            "source": "document",
            "document_id": 1,
        },
    )
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()["data"]
        assert data["answer"] == "Plain answer text."
        assert "accessibility" not in data


def test_summary_dyslexia_formats_text(client, monkeypatch):
    monkeypatch.setattr(
        "services.summary_service.generate_saksham_summary",
        lambda *args, **kwargs: {
            "summary": (
                "Photosynthesis is the process by which green plants make food "
                "using sunlight, and chlorophyll helps capture that energy."
            ),
            "format_version": "v2-prose",
            "source": "saksham",
        },
    )
    monkeypatch.setattr(
        "services.summary_service.get_chapter_chunk_texts",
        lambda *args, **kwargs: ["Photosynthesis uses chlorophyll in leaves."],
    )

    response = client.post(
        "/summary",
        json={
            "source": "saksham",
            "class_level": 7,
            "subject": "Science",
            "chapter": "Nutrition in Plants",
            "accessibility_profile": "dyslexia",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "•" in data["summary"]
    assert data["accessibility"]["profile"] == "dyslexia"


def test_quiz_dyslexia_formats_questions(client, monkeypatch):
    monkeypatch.setattr(
        "services.quiz_service.generate_saksham_quiz",
        lambda *args, **kwargs: {
            "questions": [
                {
                    "question": "What is photosynthesis in green plants using sunlight energy?",
                    "option_a": "Making food",
                    "option_b": "Making noise",
                    "option_c": "Making rocks",
                    "option_d": "Making metal",
                    "correct_answer": "A",
                }
            ],
            "source": "saksham",
        },
    )
    monkeypatch.setattr(
        "services.quiz_service.get_chapter_chunk_texts",
        lambda *args, **kwargs: ["Photosynthesis occurs in chloroplasts."],
    )

    response = client.post(
        "/quiz",
        json={
            "source": "saksham",
            "class_level": 7,
            "subject": "Science",
            "chapter": "Nutrition in Plants",
            "question_count": 5,
            "accessibility_profile": "dyslexia",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["accessibility"]["profile"] == "dyslexia"
    assert "•" in data["questions"][0]["question"]
