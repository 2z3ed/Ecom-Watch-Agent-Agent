from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes_internal_products import router as products_router
from app.api.internal_response import http_exception_to_internal, is_internal_path, validation_error_to_internal
from app.core.db import Base, get_db
from app.models.agent_report import AgentReport
from app.models.change_event import ChangeEvent
from app.models.product import Product
from app.models.snapshot import Snapshot


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


def test_product_detail_not_found() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    app = FastAPI()
    app.include_router(products_router)
    _attach_internal_handlers(app)

    def override_get_db():
        db = local_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    resp = client.get("/internal/products/1/detail")
    assert resp.status_code == 404


def test_product_detail_found_with_empty_parts() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    app = FastAPI()
    app.include_router(products_router)
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
        db.commit()
        pid = p.id

    client = TestClient(app)
    resp = client.get(f"/internal/products/{pid}/detail")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert data["product_id"] == pid
    assert data["current_snapshot"] is None
    assert data["recent_change_events"] == []
    assert data["latest_report"] is None
    assert isinstance(data["detail_summary"], str)


def test_product_detail_with_snapshot_and_report() -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    app = FastAPI()
    app.include_router(products_router)
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
            Snapshot(
                task_id=1,
                product_id=p.id,
                title="T",
                price=9.99,
                stock_status="in_stock",
                promotion_text="promo",
                page_url=p.product_url,
                screenshot_path="x.png",
                collected_at=datetime.utcnow(),
            )
        )
        db.add(
            ChangeEvent(
                task_id=1,
                product_id=p.id,
                event_type="price_changed",
                old_value="10",
                new_value="9.99",
                change_ratio=-0.1,
                detected_at=datetime.utcnow(),
            )
        )
        db.add(
            AgentReport(
                task_id=1,
                product_id=p.id,
                summary="S",
                priority="low",
                suggested_action="A",
                raw_response="{}",
                created_at=datetime.utcnow(),
            )
        )
        db.commit()
        pid = p.id

    client = TestClient(app)
    resp = client.get(f"/internal/products/{pid}/detail")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert data["current_snapshot"]["title"] == "T"
    assert data["latest_report"]["summary"] == "S"
    assert len(data["recent_change_events"]) == 1
