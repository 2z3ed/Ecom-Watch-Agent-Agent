from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings


def main() -> None:
    current = settings.mock_state_path.read_text(encoding="utf-8").strip()
    next_state = "changed" if current == "baseline" else "baseline"
    settings.mock_state_path.write_text(next_state, encoding="utf-8")
    print(f"mock state switched: {current} -> {next_state}")


if __name__ == "__main__":
    main()
