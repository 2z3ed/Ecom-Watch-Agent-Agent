from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _now_utc_naive() -> datetime:
    # 兼容当前项目大量使用 datetime.utcnow() 的 naive 方案
    return datetime.utcnow()


def _make_request_id() -> str:
    return uuid4().hex


def is_internal_path(path: str) -> bool:
    return path.startswith("/internal/")


def internal_success(data: object) -> dict:
    return {"ok": True, "data": data, "error": None}


def internal_error_payload(message: str, status_code: int, code: str, request_id: str | None = None) -> dict:
    return {
        "ok": False,
        "data": None,
        "error": {
            "message": message,
            "code": code,
            "status_code": status_code,
            "request_id": request_id,
            "timestamp": _now_utc_naive().isoformat(),
        },
    }


def http_exception_to_internal(request: Request, exc: HTTPException) -> JSONResponse:
    req_id = request.headers.get("X-Request-Id") or _make_request_id()
    return JSONResponse(
        status_code=exc.status_code,
        content=internal_error_payload(
            message=str(exc.detail),
            status_code=exc.status_code,
            code=f"HTTP_{exc.status_code}",
            request_id=req_id,
        ),
    )


def validation_error_to_internal(request: Request, exc: RequestValidationError) -> JSONResponse:
    req_id = request.headers.get("X-Request-Id") or _make_request_id()
    return JSONResponse(
        status_code=422,
        content=internal_error_payload(
            message="request validation failed",
            status_code=422,
            code="VALIDATION_ERROR",
            request_id=req_id,
        ),
    )

