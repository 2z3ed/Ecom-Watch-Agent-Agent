from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes_internal_reports import router as reports_router
from app.api.internal_response import http_exception_to_internal, is_internal_path, validation_error_to_internal
from app.core.db import Base, get_db
from app.models.agent_report import AgentReport
from app.models.product import Product


def _attach_internal_handlers(app: FastAPI) -> None:
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


def test_reports_latest_empty() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    app = FastAPI()
    app.include_router(reports_router)
    _attach_internal_handlers(app)

    def override_get_db():
        db = local_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    resp = client.get("/internal/reports/latest")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert data["count"] == 0
    assert data["report"] is None


def test_reports_latest_returns_stable_shape() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    app = FastAPI()
    app.include_router(reports_router)
    _attach_internal_handlers(app)

    def override_get_db():
        db = local_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with local_session() as db:
        p = Product(product_name="P1", product_url="mock://product-phone", source_site="mock_playwright", is_active=True)
        db.add(p)
        db.flush()
        db.add(
            AgentReport(
                task_id=1,
                product_id=p.id,
                summary="S",
                priority="high",
                suggested_action="A",
                raw_response="{}",
                created_at=datetime.utcnow(),
            )
        )
        db.commit()

    client = TestClient(app)
    resp = client.get("/internal/reports/latest")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert data["count"] == 1
    assert data["report"]["product_name"] == "P1"
    assert set(data["report"].keys()) == {"product_id", "product_name", "summary", "priority", "suggested_action"}
