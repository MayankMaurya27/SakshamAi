"""Ollama LLM client for local inference."""

import logging
import time
from typing import Protocol

import httpx

from config.settings import get_settings
from exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMClient(Protocol):
    """Protocol for LLM client implementations."""

    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""


class OllamaLLM:
    """Production LLM client using Ollama HTTP API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout_seconds
        self._client = client or httpx.Client(timeout=self.timeout)

    def generate(self, prompt: str) -> str:
        """Send prompt to Ollama and return generated text."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        start = time.time()
        try:
            response = self._client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            result = data.get("response", "").strip()
            logger.info(
                "LLM generation completed in %.2fs (model=%s)",
                time.time() - start,
                self.model,
            )
            return result
        except httpx.ConnectError as exc:
            raise ServiceUnavailableError(
                "Ollama is not available. Please ensure Ollama is running locally."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ServiceUnavailableError(
                f"Ollama request failed: {exc.response.status_code}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise ServiceUnavailableError("Ollama request timed out.") from exc

    def is_available(self) -> bool:
        """Check if Ollama service is reachable."""
        try:
            response = self._client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except httpx.HTTPError:
            return False


class MockLLM:
    """Deterministic mock LLM for testing."""

    def __init__(self, default_response: str = "Mock LLM response.") -> None:
        self.default_response = default_response
        self.last_prompt: str | None = None

    def generate(self, prompt: str) -> str:
        """Return mock response based on prompt content."""
        self.last_prompt = prompt

        if "Generate 5 multiple-choice questions" in prompt or '"questions"' in prompt:
            return """{"questions": [
                {"question": "What is the main topic?", "option_a": "Science", "option_b": "History", "option_c": "Art", "option_d": "Music", "correct_answer": "A"},
                {"question": "Which concept is discussed?", "option_a": "Force", "option_b": "Light", "option_c": "Sound", "option_d": "Heat", "correct_answer": "A"},
                {"question": "What is the key idea?", "option_a": "Energy", "option_b": "Matter", "option_c": "Space", "option_d": "Time", "correct_answer": "A"},
                {"question": "Which example is given?", "option_a": "Pushing", "option_b": "Reading", "option_c": "Sleeping", "option_d": "Eating", "correct_answer": "A"},
                {"question": "What should students remember?", "option_a": "Basics", "option_b": "Nothing", "option_c": "Dates", "option_d": "Names", "correct_answer": "A"}
            ]}"""

        if "Analyze the document" in prompt:
            return """{"summary": "This document covers fundamental concepts.", "key_concepts": [{"name": "Force", "description": "A push or pull on an object."}], "questions": [
                {"question": "What is force?", "option_a": "Push or pull", "option_b": "Color", "option_c": "Sound", "option_d": "Light", "correct_answer": "A"}
            ]}"""

        if "Extract the most important" in prompt:
            return '{"concepts": [{"name": "Force", "description": "A push or pull on an object."}]}'

        if "Explain in Hindi" in prompt:
            return "यह एक शैक्षिक व्याख्या है।"

        if "Class 6 student" in prompt:
            return "This is a simplified explanation for young learners."

        return self.default_response


_llm_instance: LLMClient | None = None


def get_llm(use_mock: bool = False) -> LLMClient:
    """Return singleton LLM client instance."""
    global _llm_instance
    if _llm_instance is None:
        if use_mock:
            _llm_instance = MockLLM()
        else:
            _llm_instance = OllamaLLM()
    return _llm_instance


def set_llm(client: LLMClient) -> None:
    """Override LLM client (for testing)."""
    global _llm_instance
    _llm_instance = client


def generate_answer(prompt: str) -> str:
    """Generate text using the default LLM client."""
    return get_llm().generate(prompt)
