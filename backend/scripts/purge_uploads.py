"""One-off maintenance: purge all uploaded PDFs and reset document records."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config.settings import get_settings
from database.db import SessionLocal, init_db
from services.document_service import purge_all_uploads


def main() -> None:
    settings = get_settings()
    settings.ensure_directories()
    init_db()

    with SessionLocal() as db:
        result = purge_all_uploads(db, settings.uploads_dir)

    remaining = len(list(settings.uploads_dir.glob("*.pdf")))
    print(
        f"Removed {result['removed_files']} PDF file(s), "
        f"deleted {result['deleted_documents']} document record(s). "
        f"Remaining PDFs: {remaining}."
    )


if __name__ == "__main__":
    main()
