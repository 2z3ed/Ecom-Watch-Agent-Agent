from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes_internal_monitor import router as monitor_router
from app.api.internal_response import http_exception_to_internal, is_internal_path, validation_error_to_internal
from app.core.db import Base, get_db
from app.models.product import Product


def _make_test_app(local_session):
    app = FastAPI()
    app.include_router(monitor_router)

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
    return app


def test_targets_list_empty() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    client = TestClient(_make_test_app(local_session))
    resp = client.get("/internal/monitor/targets")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert data["count"] == 0
    assert data["targets"] == []


def test_pause_resume_delete_flow() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    with local_session() as db:
        p = Product(product_name="P1", product_url="mock://product-phone", source_site="mock_playwright", is_active=True)
        db.add(p)
        db.commit()
        pid = p.id

    client = TestClient(_make_test_app(local_session))

    # pause
    resp = client.post(f"/internal/monitor/{pid}/pause")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    assert payload["data"]["status"] == "paused"
    assert payload["data"]["is_active"] is False

    # list active only
    resp = client.get("/internal/monitor/targets?include_inactive=false")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    assert payload["data"]["count"] == 0

    # resume
    resp = client.post(f"/internal/monitor/{pid}/resume")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    assert payload["data"]["status"] == "resumed"
    assert payload["data"]["is_active"] is True

    # delete (soft disable)
    resp = client.delete(f"/internal/monitor/{pid}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    assert payload["data"]["status"] == "deleted"
    assert payload["data"]["is_active"] is False


def test_pause_unknown_returns_404() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    client = TestClient(_make_test_app(local_session))
    resp = client.post("/internal/monitor/999/pause")
    assert resp.status_code == 404
