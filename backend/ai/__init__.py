"""AI layer package."""

from ai.embeddings import embed_batch, embed_text, get_embedding_model, set_embedding_model
from ai.faiss_manager import (
    get_saksham_index,
    get_user_index,
    save_saksham_index,
    save_user_index,
)
from ai.llm import generate_answer, get_llm, set_llm
from ai.prompt_builder import build_fallback_prompt, build_prompt, format_retrieved_chunks
from ai.retriever import ChunkContext, retrieve_document_context, retrieve_saksham_context

__all__ = [
    "ChunkContext",
    "build_fallback_prompt",
    "build_prompt",
    "embed_batch",
    "embed_text",
    "format_retrieved_chunks",
    "generate_answer",
    "get_embedding_model",
    "get_llm",
    "get_saksham_index",
    "get_user_index",
    "retrieve_document_context",
    "retrieve_saksham_context",
    "save_saksham_index",
    "save_user_index",
    "set_embedding_model",
    "set_llm",
]
