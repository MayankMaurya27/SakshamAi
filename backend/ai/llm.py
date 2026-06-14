"""Ollama LLM client for local inference."""

import json
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

    def generate(
        self,
        prompt: str,
        num_predict: int | None = None,
        format_json: bool = False,
    ) -> str:
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

    def generate(
        self,
        prompt: str,
        num_predict: int | None = None,
        format_json: bool = False,
    ) -> str:
        """Send prompt to Ollama and return generated text."""
        url = f"{self.base_url}/api/generate"
        options: dict = {
            "temperature": settings.ollama_temperature,
            "num_ctx": settings.ollama_num_ctx,
        }
        if num_predict is not None:
            options["num_predict"] = num_predict

        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
        if format_json:
            payload["format"] = "json"

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
        self._quiz_offset = 0

    def _format_text_quiz(self, count: int, prompt: str = "") -> str:
        context = prompt.lower()
        templates: list[tuple[str, str, str, str, str, str]] = []
        if "agriculture" in context:
            templates = [
                (
                    "What is agriculture described as in the text?",
                    "A primary activity",
                    "A decorative art",
                    "A transport network",
                    "A mining process",
                    "A",
                ),
                (
                    "Which crops are mentioned as major crops?",
                    "Rice and wheat",
                    "Tea and coffee only",
                    "Rubber and jute only",
                    "Cotton and silk only",
                    "A",
                ),
                (
                    "What does agriculture provide according to the text?",
                    "Food and raw materials",
                    "Only electronic goods",
                    "Only luxury items",
                    "Only imported products",
                    "A",
                ),
                (
                    "Where are rice and wheat grown according to the text?",
                    "Across many states",
                    "Only in deserts",
                    "Only in hill stations",
                    "Only in coastal ports",
                    "A",
                ),
                (
                    "Agriculture is mainly linked to which outputs in the text?",
                    "Food and raw materials",
                    "Only software exports",
                    "Only gold mining",
                    "Only air travel",
                    "A",
                ),
            ]
        elif "force" in context or "newton" in context:
            templates = [
                (
                    "What is force described as in the text?",
                    "A push or pull",
                    "A type of light",
                    "A kind of sound",
                    "A form of heat",
                    "A",
                ),
                (
                    "Who studied force and motion according to the text?",
                    "Newton",
                    "Darwin",
                    "Einstein",
                    "Galileo",
                    "A",
                ),
                (
                    "Force can be described as which action on an object?",
                    "Push or pull",
                    "Only rotation",
                    "Only reflection",
                    "Only evaporation",
                    "A",
                ),
                (
                    "Which scientist is linked with force and motion in the text?",
                    "Newton",
                    "Curie",
                    "Tesla",
                    "Faraday",
                    "A",
                ),
                (
                    "What basic idea about force appears in the text?",
                    "Force is a push or pull",
                    "Force is only color",
                    "Force is only smell",
                    "Force is only taste",
                    "A",
                ),
            ]
        elif "resources" in context:
            templates = [
                (
                    "What topic does the text discuss?",
                    "Resources and development",
                    "Sports and games",
                    "Music and dance",
                    "Fashion and design",
                    "A",
                ),
                (
                    "What does the text link resources with?",
                    "Development",
                    "Entertainment",
                    "Painting",
                    "Cooking",
                    "A",
                ),
                (
                    "Which pair best matches the text theme?",
                    "Resources and development",
                    "Games and sports",
                    "Dance and music",
                    "Design and fashion",
                    "A",
                ),
                (
                    "The text mainly discusses development in which context?",
                    "Resources",
                    "Sports",
                    "Music",
                    "Fashion",
                    "A",
                ),
                (
                    "Which answer fits the text focus?",
                    "Resources and development",
                    "Games only",
                    "Songs only",
                    "Clothing only",
                    "A",
                ),
            ]
        blocks: list[str] = []
        for idx in range(count):
            qnum = self._quiz_offset + idx + 1
            if templates:
                template = templates[(self._quiz_offset + idx) % len(templates)]
                question, a, b, c, d, answer = template
                question = question.replace("?", f" ({qnum})?")
            else:
                question = f"Mock quiz question {qnum}?"
                a, b, c, d, answer = "First choice", "Second choice", "Third choice", "Fourth choice", "A"
            blocks.append(
                f"Question {idx + 1}: {question}\n"
                f"A. {a}\n"
                f"B. {b}\n"
                f"C. {c}\n"
                f"D. {d}\n"
                f"Answer: {answer}"
            )
        self._quiz_offset += count
        return "\n\n".join(blocks)

    def generate(
        self,
        prompt: str,
        num_predict: int | None = None,
        format_json: bool = False,
    ) -> str:
        """Return mock response based on prompt content."""
        _ = format_json
        self.last_prompt = prompt

        if "Generate exactly" in prompt and "multiple-choice questions" in prompt:
            import re

            match = re.search(r"Generate exactly (\d+) multiple-choice questions", prompt)
            count = int(match.group(1)) if match else 5
            return self._format_text_quiz(count, prompt)

        if '"questions"' in prompt and "multiple-choice" in prompt.lower():
            return """{"questions": [
                {"question": "What is the main topic?", "option_a": "Science", "option_b": "History", "option_c": "Art", "option_d": "Music", "correct_answer": "A"},
                {"question": "Which concept is discussed?", "option_a": "Force", "option_b": "Light", "option_c": "Sound", "option_d": "Heat", "correct_answer": "A"},
                {"question": "What is the key idea?", "option_a": "Energy", "option_b": "Matter", "option_c": "Space", "option_d": "Time", "correct_answer": "A"},
                {"question": "Which example is given?", "option_a": "Pushing", "option_b": "Reading", "option_c": "Sleeping", "option_d": "Eating", "correct_answer": "A"},
                {"question": "What should students remember?", "option_a": "Basics", "option_b": "Nothing", "option_c": "Dates", "option_d": "Names", "correct_answer": "A"}
            ]}"""

        if "Write revision notes" in prompt or "Combine these" in prompt:
            if "Combine these" in prompt or "Combine the partial revision notes" in prompt:
                return (
                    "Electricity is an important form of energy used in homes, schools, and industry. "
                    "Students use it every day through lights, fans, and many appliances.\n\n"
                    "An electric circuit is a closed path that allows electric current to flow. "
                    "A battery or cell provides the potential difference needed to push charges through the circuit.\n\n"
                    "Resistance opposes the flow of current in a conductor. "
                    "Ohm's law links voltage, current, and resistance in a simple electric circuit."
                )

            if "one part of a longer chapter" in prompt:
                return (
                    "Electric current is the flow of electric charge through a conductor. "
                    "It needs a closed path called an electric circuit.\n\n"
                    "Potential difference is the work done to move a unit charge between two points. "
                    "It is measured using a voltmeter."
                )

            if "electric circuit" in prompt.lower() or "electricity" in prompt.lower():
                return (
                    "An electric circuit is a continuous and closed path for electric current. "
                    "Current flows when there is a potential difference in the circuit.\n\n"
                    "A resistor opposes current flow, while variable resistance helps control current "
                    "without changing the voltage source.\n\n"
                    "Students should remember the basic definitions and how current, voltage, "
                    "and resistance work together in a circuit."
                )

            return (
                "Force is a push or pull that can change how an object moves. "
                "It is one of the basic ideas students study in science.\n\n"
                "Motion happens when an object's position changes over time. "
                "Force can start, stop, or change the direction of motion.\n\n"
                "Students should remember that force and motion are closely linked in everyday examples."
            )

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
