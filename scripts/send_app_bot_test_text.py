import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.feishu_app_bot import send_app_bot_text_to_chat, send_app_bot_text_to_user


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send test text by Feishu app bot")
    parser.add_argument("--target", choices=["chat", "user"], default="chat")
    parser.add_argument("--chat-id", default="")
    parser.add_argument("--open-id", default="")
    parser.add_argument("--text", default="Ecom Watch Agent app bot test message")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.target == "chat":
        result = send_app_bot_text_to_chat(args.text, args.chat_id or None)
    else:
        result = send_app_bot_text_to_user(args.text, args.open_id or None)
    print(result)


if __name__ == "__main__":
    main()
