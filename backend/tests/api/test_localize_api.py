"""API tests for POST /localize/hi."""

from config.constants import LocalizeContentType


def test_localize_hi_prose_success(client):
    response = client.post(
        "/localize/hi",
        json={
            "text": "• Photosynthesis is how plants make food using sunlight.",
            "content_type": LocalizeContentType.ANSWER.value,
            "class_level": 9,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["language"] == "hi"
    assert body["data"]["hindi_text"]


def test_localize_hi_quiz_success(client):
    response = client.post(
        "/localize/hi",
        json={
            "content_type": LocalizeContentType.QUIZ.value,
            "quiz": {
                "questions": [
                    {
                        "question": "What is force?",
                        "option_a": "Push or pull",
                        "option_b": "Color",
                        "option_c": "Sound",
                        "option_d": "Light",
                        "correct_answer": "A",
                    }
                ]
            },
            "class_level": 8,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["hindi_quiz"]["questions"][0]["correct_answer"] == "A"


def test_localize_hi_missing_text(client):
    response = client.post(
        "/localize/hi",
        json={
            "content_type": LocalizeContentType.ANSWER.value,
        },
    )
    assert response.status_code == 422


def test_hindi_endpoint_deprecated(client, monkeypatch):
    monkeypatch.setattr(
        "api.hindi.answer_question",
        lambda **kwargs: "Force is a push or pull on an object.",
    )
    response = client.post(
        "/hindi",
        json={
            "question": "What is force?",
            "source": "saksham",
            "class_level": 8,
            "subject": "Science",
            "topic": "Force and Pressure",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("Deprecation") == "true"
    assert response.json()["data"]["deprecated"] is True
