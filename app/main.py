from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from app.api.routes_health import router as health_router
from app.api.routes_internal_discovery import router as internal_discovery_router
from app.api.routes_internal_monitor import router as internal_monitor_router
from app.api.routes_internal_products import router as internal_products_router
from app.api.routes_internal_reports import router as internal_reports_router
from app.api.routes_internal_summary import router as internal_summary_router
from app.api.routes_reports import router as reports_router
from app.api.routes_tasks import router as tasks_router
from app.api.internal_response import (
    http_exception_to_internal,
    is_internal_path,
    validation_error_to_internal,
)
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(reports_router)
app.include_router(internal_discovery_router)
app.include_router(internal_monitor_router)
app.include_router(internal_summary_router)
app.include_router(internal_products_router)
app.include_router(internal_reports_router)


@app.exception_handler(HTTPException)
def _internal_http_exception_handler(request: Request, exc: HTTPException):  # type: ignore[no-untyped-def]
    if is_internal_path(request.url.path):
        return http_exception_to_internal(request, exc)
    return http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
def _internal_validation_exception_handler(request: Request, exc: RequestValidationError):  # type: ignore[no-untyped-def]
    if is_internal_path(request.url.path):
        return validation_error_to_internal(request, exc)
    return request_validation_exception_handler(request, exc)
