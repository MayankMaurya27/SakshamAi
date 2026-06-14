"""Download bundled Piper TTS voice model for offline speech."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config.settings import get_settings

VOICE_FILES = {
    "en_US-lessac-medium.onnx": (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    ),
    "en_US-lessac-medium.onnx.json": (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    ),
}


def download_piper_voice(target_dir: Path | None = None) -> Path:
    settings = get_settings()
    out_dir = target_dir or (settings.models_dir / "piper")
    out_dir.mkdir(parents=True, exist_ok=True)

    for filename, url in VOICE_FILES.items():
        dest = out_dir / filename
        if dest.exists() and dest.stat().st_size > 0:
            print(f"Already present: {dest}")
            continue
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, dest)
        print(f"Saved {dest} ({dest.stat().st_size} bytes)")

    model_path = out_dir / "en_US-lessac-medium.onnx"
    if not model_path.exists():
        raise RuntimeError(f"Download failed: {model_path} missing")
    return model_path


def main() -> None:
    model_path = download_piper_voice()
    print(f"Piper voice ready at {model_path}")
    print("Set in .env:")
    print(f"PIPER_MODEL_PATH=./data/models/piper/en_US-lessac-medium.onnx")


if __name__ == "__main__":
    main()
