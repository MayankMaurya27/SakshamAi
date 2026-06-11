"""Standard API response helpers."""

from typing import Any

from fastapi.responses import JSONResponse


def success_response(data: Any, status_code: int = 200) -> JSONResponse:
    """Return a standardized success JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "data": data},
    )


def error_response(error: str, status_code: int = 400) -> JSONResponse:
    """Return a standardized error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": error},
    )
