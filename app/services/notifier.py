import json
from typing import Any

import httpx

from app.core.config import settings


def build_notification_text(product_name: str, events: list[dict[str, Any]], report: dict[str, str]) -> str:
    lines = [
        "【Ecom Watch Agent】检测到商品变化",
        f"商品: {product_name}",
        f"变化数: {len(events)}",
    ]
    for event in events:
        lines.append(f"- {event['event_type']}: {event['old_value']} -> {event['new_value']}")
    lines.extend(
        [
            f"摘要: {report['summary']}",
            f"优先级: {report['priority']}",
            f"建议动作: {report['suggested_action']}",
        ]
    )
    return "\n".join(lines)


def send_notification(product_name: str, events: list[dict[str, Any]], report: dict[str, str]) -> dict[str, Any]:
    text = build_notification_text(product_name, events, report)
    if not settings.feishu_webhook_url:
        return {"mode": "dry_run", "sent": False, "message_preview": text}

    payload = {"msg_type": "text", "content": {"text": text}}
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(settings.feishu_webhook_url, json=payload)
            resp.raise_for_status()
        return {"mode": "webhook", "sent": True, "response": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {
            "mode": "webhook_failed",
            "sent": False,
            "error": str(exc),
            "payload_preview": json.dumps(payload, ensure_ascii=False),
        }
