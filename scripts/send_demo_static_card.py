import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.feishu_app_bot import send_static_card_to_chat_from_demo, send_static_card_to_user_from_demo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send static card from demo_last_run.json")
    parser.add_argument("--target", choices=["chat", "user"], default="chat")
    parser.add_argument("--chat-id", default="")
    parser.add_argument("--open-id", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.target == "chat":
        result = send_static_card_to_chat_from_demo(args.chat_id or None)
    else:
        result = send_static_card_to_user_from_demo(args.open_id or None)
    print(result)


if __name__ == "__main__":
    main()
