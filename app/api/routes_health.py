from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ecom-watch-agent"}


@router.get("/mock/products/{slug}", response_class=HTMLResponse)
def get_mock_product_page(slug: str) -> str:
    state = settings.mock_state_path.read_text(encoding="utf-8").strip()
    file_path = settings.mock_pages_path / state / f"{slug}.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="mock product not found")
    return file_path.read_text(encoding="utf-8")
