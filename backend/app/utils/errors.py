"""
Shared error helpers so every route returns a consistent, safe error shape.
Never includes stack traces, file paths, or secrets in the response body.
"""

from fastapi import HTTPException


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=404, detail=message)


def upstream_failure(module_name: str) -> HTTPException:
    """Use when a downstream module (RAG, verification, etc.) fails or is
    unavailable, instead of leaking internal exception details."""
    return HTTPException(
        status_code=502,
        detail=f"{module_name} is currently unavailable. Please try again shortly.",
    )
