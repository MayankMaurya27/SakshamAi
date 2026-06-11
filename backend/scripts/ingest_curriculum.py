"""Ingest curriculum PDFs into Saksham FAISS index."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.knowledge_service import build_saksham_index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Build Saksham index from curriculum PDFs."""
    parser = argparse.ArgumentParser(description="Ingest Saksham curriculum PDFs")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rebuild even if curriculum hash is unchanged",
    )
    args = parser.parse_args()

    logger.info("Starting curriculum ingestion (force=%s)", args.force)
    build_saksham_index(force=args.force)
    logger.info("Curriculum ingestion complete")


if __name__ == "__main__":
    main()
