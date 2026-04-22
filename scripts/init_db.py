from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.db import init_db


def main() -> None:
    settings.screenshots_path.mkdir(parents=True, exist_ok=True)
    settings.mock_pages_path.mkdir(parents=True, exist_ok=True)
    settings.mock_state_path.parent.mkdir(parents=True, exist_ok=True)
    if not settings.mock_state_path.exists():
        settings.mock_state_path.write_text("baseline", encoding="utf-8")
    init_db()
    print("Database initialized.")


if __name__ == "__main__":
    main()
