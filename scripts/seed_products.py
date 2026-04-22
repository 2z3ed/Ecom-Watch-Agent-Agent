from pathlib import Path
import sys

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.db import SessionLocal
from app.models.product import Product


SEED_PRODUCTS = [
    {"product_name": "Mock Phone X", "product_url": "mock://product-phone", "source_site": "mock"},
    {"product_name": "Mock Headphone Pro", "product_url": "mock://product-headphone", "source_site": "mock"},
    {"product_name": "Mock Keyboard Mini", "product_url": "mock://product-keyboard", "source_site": "mock"},
]


def main() -> None:
    db = SessionLocal()
    try:
        for item in SEED_PRODUCTS:
            exists = db.execute(select(Product).where(Product.product_url == item["product_url"])).scalar_one_or_none()
            if exists:
                continue
            db.add(Product(**item))
        db.commit()
        count = db.execute(select(Product)).scalars().all()
        print(f"Seed completed. active products: {len(count)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
