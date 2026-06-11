"""PDF upload endpoint."""

import logging

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from api.responses import error_response, success_response
from config.constants import ALLOWED_PDF_EXTENSIONS, MAX_PDF_SIZE_BYTES
from database.db import get_db
from documents.processor import process_upload
from exceptions import PDFProcessingError, SakshamError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a PDF document."""
    if not file.filename:
        return error_response("Filename is required.", status_code=422)

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_PDF_EXTENSIONS:
        return error_response("Only PDF files are accepted.", status_code=422)

    content = await file.read()
    if len(content) > MAX_PDF_SIZE_BYTES:
        return error_response("File exceeds maximum size of 25 MB.", status_code=422)

    if len(content) == 0:
        return error_response("Uploaded file is empty.", status_code=422)

    try:
        result = process_upload(content, file.filename, db)
        logger.info("Upload successful: document_id=%d", result["document_id"])
        return success_response(result, status_code=201)
    except PDFProcessingError as exc:
        return error_response(exc.message, status_code=400)
    except SakshamError as exc:
        return error_response(exc.message, status_code=500)
