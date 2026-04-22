from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from app.core.db import Base, get_db
from app.api.routes_internal_discovery import router as internal_discovery_router
from app.api.internal_response import http_exception_to_internal, is_internal_path, validation_error_to_internal


def test_candidate_batch_api_flow(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    app = FastAPI()
    app.include_router(internal_discovery_router)

    @app.exception_handler(HTTPException)
    def _h(request: Request, exc: HTTPException):  # type: ignore[no-untyped-def]
        if is_internal_path(request.url.path):
            return http_exception_to_internal(request, exc)
        return http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    def _v(request: Request, exc: RequestValidationError):  # type: ignore[no-untyped-def]
        if is_internal_path(request.url.path):
            return validation_error_to_internal(request, exc)
        return request_validation_exception_handler(request, exc)

    def override_get_db():
        db = local_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    from app.api import routes_internal_discovery

    def fake_search_and_store(db, query: str, limit=None, allowed_domains=None) -> dict:
        return {
            "ok": True,
            "error": None,
            "batch_id": 1,
            "query": query,
            "source_type": "discovery",
            "created_at": "2026-01-01T00:00:00",
            "count": 1,
            "candidates": [
                {
                    "candidate_id": 1,
                    "candidate_rank": 1,
                    "title": "A",
                    "url": "https://example.com/a",
                    "domain": "example.com",
                    "snippet": "s",
                }
            ],
            "is_fallback": False,
        }

    def fake_get_batch(db, batch_id: int) -> dict:
        return {
            "batch_id": batch_id,
            "query": "phone",
            "source_type": "discovery",
            "created_at": "2026-01-01T00:00:00",
            "count": 1,
            "candidates": [
                {
                    "candidate_id": 1,
                    "candidate_rank": 1,
                    "title": "A",
                    "url": "https://example.com/a",
                    "domain": "example.com",
                    "snippet": "s",
                }
            ],
        }

    monkeypatch.setattr(routes_internal_discovery.service, "search_and_store", fake_search_and_store)
    monkeypatch.setattr(routes_internal_discovery.service, "get_batch", fake_get_batch)

    client = TestClient(app)
    create_resp = client.post("/internal/discovery/search", json={"query": "phone"})
    assert create_resp.status_code == 200
    payload = create_resp.json()
    assert payload["ok"] is True
    assert payload["data"]["batch_id"] == 1

    get_resp = client.get("/internal/discovery/batches/1")
    assert get_resp.status_code == 200
    payload = get_resp.json()
    assert payload["ok"] is True
    assert payload["data"]["count"] == 1

    app.dependency_overrides.clear()
