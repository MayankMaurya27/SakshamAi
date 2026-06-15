"""Download bundled Piper TTS voice models for offline speech."""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config.settings import get_settings

ENGLISH_VOICE_FILES = {
    "en_US-lessac-medium.onnx": (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    ),
    "en_US-lessac-medium.onnx.json": (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    ),
}

HINDI_VOICE_FILES = {
    "hi_IN-rohan-medium.onnx": (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/rohan/medium/hi_IN-rohan-medium.onnx"
    ),
    "hi_IN-rohan-medium.onnx.json": (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/rohan/medium/hi_IN-rohan-medium.onnx.json"
    ),
}


def _download_files(files: dict[str, str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for filename, url in files.items():
        dest = out_dir / filename
        if dest.exists() and dest.stat().st_size > 0:
            print(f"Already present: {dest}")
            continue
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, dest)
        print(f"Saved {dest} ({dest.stat().st_size} bytes)")


def download_piper_voice(target_dir: Path | None = None) -> Path:
    settings = get_settings()
    out_dir = target_dir or (settings.models_dir / "piper")
    _download_files(ENGLISH_VOICE_FILES, out_dir)
    model_path = out_dir / "en_US-lessac-medium.onnx"
    if not model_path.exists():
        raise RuntimeError(f"Download failed: {model_path} missing")
    return model_path


def download_piper_hindi_voice(target_dir: Path | None = None) -> Path:
    settings = get_settings()
    out_dir = target_dir or (settings.models_dir / "piper")
    _download_files(HINDI_VOICE_FILES, out_dir)
    model_path = out_dir / "hi_IN-rohan-medium.onnx"
    if not model_path.exists():
        raise RuntimeError(f"Download failed: {model_path} missing")
    return model_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Piper TTS voice models")
    parser.add_argument(
        "--hindi",
        action="store_true",
        help="Download Hindi voice (hi_IN-rohan-medium)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download English and Hindi voices",
    )
    args = parser.parse_args()

    if args.all or not args.hindi:
        model_path = download_piper_voice()
        print(f"English Piper voice ready at {model_path}")
        print("Set in .env:")
        print("PIPER_MODEL_PATH=./data/models/piper/en_US-lessac-medium.onnx")

    if args.all or args.hindi:
        hindi_path = download_piper_hindi_voice()
        print(f"Hindi Piper voice ready at {hindi_path}")
        print("Set in .env:")
        print("PIPER_HINDI_MODEL_PATH=./data/models/piper/hi_IN-rohan-medium.onnx")


if __name__ == "__main__":
    main()
