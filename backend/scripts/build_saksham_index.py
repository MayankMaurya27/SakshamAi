# Curriculum index builder (delegates to knowledge_service)

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.knowledge_service import build_saksham_index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    force = "--force" in sys.argv
    build_saksham_index(force=force)
    logger.info("Saksham index build complete")
