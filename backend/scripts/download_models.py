"""Download embedding and reranker models into data/models/ for offline deployment."""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# PyTorch-only files Saksham actually loads (skips ONNX/OpenVino — saves ~2 GB).
PYTORCH_ONLY_PATTERNS: dict[str, list[str]] = {
    "embedding": [
        "config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "sentencepiece.bpe.model",
        "modules.json",
        "sentence_bert_config.json",
        "1_Pooling/**",
    ],
    "rerank": [
        "config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "vocab.txt",
    ],
}

REQUIRED_FILES: dict[str, tuple[str, ...]] = {
    "embedding": ("model.safetensors", "config.json", "tokenizer.json"),
    "rerank": ("model.safetensors", "config.json"),
}

# Leftover dirs/files from full-repo downloads — not used by sentence-transformers PyTorch.
REMOVABLE_DIRS = ("onnx", "openvino", ".cache", ".eval_results")
REMOVABLE_FILES = (
    "flax_model.msgpack",
    "pytorch_model.bin",
    "tf_model.h5",
    "rust_model.ot",
)


@dataclass(frozen=True)
class BundledModel:
    """HuggingFace model to bundle for offline use."""

    key: str
    repo_id: str
    local_dir_name: str
    approx_size_mb: int


BUNDLED_MODELS: tuple[BundledModel, ...] = (
    BundledModel(
        key="embedding",
        repo_id="intfloat/multilingual-e5-small",
        local_dir_name="multilingual-e5-small",
        approx_size_mb=470,
    ),
    BundledModel(
        key="rerank",
        repo_id="cross-encoder/ms-marco-MiniLM-L-6-v2",
        local_dir_name="ms-marco-MiniLM-L-6-v2",
        approx_size_mb=90,
    ),
)


def _selected_models(args: argparse.Namespace) -> list[BundledModel]:
    if args.embedding_only:
        return [BUNDLED_MODELS[0]]
    if args.rerank_only:
        return [BUNDLED_MODELS[1]]
    return list(BUNDLED_MODELS)


def _model_is_complete(model: BundledModel, target_dir: Path) -> bool:
    return all((target_dir / name).exists() for name in REQUIRED_FILES[model.key])


def _cleanup_model_dir(model_dir: Path) -> int:
    """Remove unused export formats from a bundled model directory."""
    if not model_dir.is_dir():
        return 0

    removed_bytes = 0

    for dirname in REMOVABLE_DIRS:
        path = model_dir / dirname
        if not path.exists():
            continue
        size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        shutil.rmtree(path)
        removed_bytes += size
        logger.info("Removed %s/ (~%.1f MB)", path.name, size / 1_048_576)

    for filename in REMOVABLE_FILES:
        path = model_dir / filename
        if not path.is_file():
            continue
        if filename == "pytorch_model.bin" and not (model_dir / "model.safetensors").exists():
            continue
        size = path.stat().st_size
        path.unlink()
        removed_bytes += size
        logger.info("Removed %s (~%.1f MB)", filename, size / 1_048_576)

    return removed_bytes


def cleanup_bundled_models(models_dir: Path) -> None:
    """Strip ONNX/OpenVino/cache extras from all bundled model folders."""
    total_removed = 0
    for model in BUNDLED_MODELS:
        model_dir = models_dir / model.local_dir_name
        if model_dir.is_dir():
            total_removed += _cleanup_model_dir(model_dir)

    logger.info(
        "Cleanup freed ~%.1f MB under %s",
        total_removed / 1_048_576,
        models_dir,
    )


def _download_model(
    model: BundledModel,
    models_dir: Path,
    force: bool,
    full_repo: bool,
) -> Path:
    from huggingface_hub import snapshot_download

    target_dir = models_dir / model.local_dir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    if not force and _model_is_complete(model, target_dir):
        logger.info(
            "Skipping %s — already present at %s (use --force to re-download)",
            model.repo_id,
            target_dir,
        )
        return target_dir.resolve()

    mode = "full repo (~2+ GB extras)" if full_repo else "PyTorch only"
    logger.info(
        "Downloading %s (%s, ~%d MB core) to %s",
        model.repo_id,
        mode,
        model.approx_size_mb,
        target_dir,
    )

    kwargs: dict = {
        "repo_id": model.repo_id,
        "local_dir": str(target_dir),
        "force_download": force,
    }
    if not full_repo:
        kwargs["allow_patterns"] = PYTORCH_ONLY_PATTERNS[model.key]

    snapshot_download(**kwargs)
    _cleanup_model_dir(target_dir)
    logger.info("Downloaded %s", model.repo_id)
    return target_dir.resolve()


def _verify_model(model: BundledModel, model_dir: Path) -> None:
    logger.info("Verifying offline load for %s from %s", model.repo_id, model_dir)

    if model.key == "embedding":
        from sentence_transformers import SentenceTransformer

        encoder = SentenceTransformer(str(model_dir), local_files_only=True)
        vector = encoder.encode("query: offline verification", normalize_embeddings=True)
        if vector is None or len(vector) == 0:
            raise RuntimeError(f"Embedding verification failed for {model_dir}")
        logger.info("Embedding model OK (dim=%d)", len(vector))
        return

    from sentence_transformers import CrossEncoder

    reranker = CrossEncoder(str(model_dir), local_files_only=True)
    scores = reranker.predict([["minimum wages", "Farm labourers are paid wages."]])
    if scores is None or len(scores) == 0:
        raise RuntimeError(f"Reranker verification failed for {model_dir}")
    logger.info("Reranker model OK (sample score=%.4f)", float(scores[0]))


def _print_env_snippet(model_paths: dict[str, Path]) -> None:
    embedding_path = model_paths.get("embedding")
    rerank_path = model_paths.get("rerank")

    print("\nAdd these lines to backend/.env for offline mode:\n")
    if embedding_path:
        print(f"EMBEDDING_MODEL_PATH={embedding_path}")
    if rerank_path:
        print(f"RERANK_MODEL_PATH={rerank_path}")
    print("EMBEDDING_LOCAL_FILES_ONLY=true")
    print("RERANK_LOCAL_FILES_ONLY=true")
    print("\nCopy the entire data/models/ folder to Jetson along with data/faiss/.")


def main() -> None:
    """Download bundled models for offline/Jetson deployment."""
    parser = argparse.ArgumentParser(
        description="Download Saksham retrieval models into data/models/",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the model directory already exists",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Download entire HuggingFace repo including ONNX/OpenVino (slow, ~2.7 GB)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Load each model with local_files_only=True after download",
    )
    parser.add_argument(
        "--embedding-only",
        action="store_true",
        help="Download only the embedding model (~470 MB)",
    )
    parser.add_argument(
        "--rerank-only",
        action="store_true",
        help="Download only the reranker model (~90 MB)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove ONNX/OpenVino/cache extras from data/models/ (no download)",
    )
    args = parser.parse_args()

    if args.embedding_only and args.rerank_only:
        parser.error("Use only one of --embedding-only or --rerank-only")

    settings = get_settings()
    models_dir = settings.models_dir.resolve()
    models_dir.mkdir(parents=True, exist_ok=True)

    if args.cleanup:
        cleanup_bundled_models(models_dir)
        if args.verify:
            for model in BUNDLED_MODELS:
                model_dir = models_dir / model.local_dir_name
                if _model_is_complete(model, model_dir):
                    _verify_model(model, model_dir)
                else:
                    logger.warning(
                        "Missing core files for %s — run without --cleanup to download",
                        model.repo_id,
                    )
        logger.info("Cleanup complete")
        return

    logger.info("Model output directory: %s", models_dir)
    if not args.full:
        logger.info(
            "Using PyTorch-only download (fast). Pass --full for ONNX/OpenVino extras."
        )

    downloaded: dict[str, Path] = {}

    for model in _selected_models(args):
        model_dir = _download_model(
            model,
            models_dir,
            force=args.force,
            full_repo=args.full,
        )
        downloaded[model.key] = model_dir
        if args.verify:
            _verify_model(model, model_dir)

    _print_env_snippet(downloaded)
    logger.info("Model download complete")


if __name__ == "__main__":
    main()
