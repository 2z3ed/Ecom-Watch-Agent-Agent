import json
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import desc, select

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.agent_report import AgentReport
from app.models.monitor_task import MonitorTask
from app.models.product import Product


FEISHU_API_BASE = "https://open.feishu.cn/open-apis"


def _dry_run(payload: dict[str, Any], reason: str) -> dict[str, Any]:
    return {"mode": "dry_run", "sent": False, "reason": reason, "payload_preview": payload}


def _load_demo_last_run() -> dict[str, Any]:
    file_path = settings.base_dir / "data" / "demo_last_run.json"
    if not file_path.exists():
        raise FileNotFoundError(f"demo_last_run.json not found: {file_path}")
    return json.loads(file_path.read_text(encoding="utf-8"))


def _load_latest_result_from_db() -> dict[str, Any]:
    db = SessionLocal()
    try:
        latest_task = db.execute(select(MonitorTask).order_by(desc(MonitorTask.id)).limit(1)).scalar_one_or_none()
        if latest_task is None:
            return {
                "generated_at": "",
                "baseline_run": {},
                "changed_run": {},
                "report_summaries": [],
            }
        reports = db.execute(select(AgentReport).where(AgentReport.task_id == latest_task.id)).scalars().all()
        products = {p.id: p.product_name for p in db.execute(select(Product)).scalars().all()}
        report_summaries = [
            {
                "product_name": products.get(item.product_id, f"product-{item.product_id}"),
                "summary": item.summary,
                "priority": item.priority,
                "suggested_action": item.suggested_action,
            }
            for item in reports
        ]
        return {
            "generated_at": latest_task.finished_at.isoformat() if latest_task.finished_at else "",
            "baseline_run": {},
            "changed_run": {"task_id": latest_task.id},
            "report_summaries": report_summaries,
        }
    finally:
        db.close()


def _resolve_card_data() -> dict[str, Any]:
    if settings.feishu_use_demo_last_run:
        try:
            return _load_demo_last_run()
        except Exception:  # noqa: BLE001
            return _load_latest_result_from_db()
    return _load_latest_result_from_db()


def _get_tenant_access_token(client: httpx.Client) -> str:
    resp = client.post(
        f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal",
        json={"app_id": settings.feishu_app_id, "app_secret": settings.feishu_app_secret},
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != 0:
        raise RuntimeError(f"Get tenant token failed: {payload}")
    return payload["tenant_access_token"]


def _send_message(receive_id: str, receive_id_type: str, msg_type: str, content: dict[str, Any]) -> dict[str, Any]:
    payload = {"receive_id": receive_id, "msg_type": msg_type, "content": json.dumps(content, ensure_ascii=False)}

    if not settings.feishu_enable_app_bot:
        return _dry_run(payload, "FEISHU_ENABLE_APP_BOT is false")
    if not settings.feishu_enable_send:
        return _dry_run(payload, "FEISHU_ENABLE_SEND is false")
    if not settings.feishu_app_id or not settings.feishu_app_secret:
        return _dry_run(payload, "Missing FEISHU_APP_ID or FEISHU_APP_SECRET")

    try:
        with httpx.Client(timeout=10.0) as client:
            token = _get_tenant_access_token(client)
            resp = client.post(
                f"{FEISHU_API_BASE}/im/v1/messages",
                params={"receive_id_type": receive_id_type},
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 0:
                return {"mode": "app_bot_failed", "sent": False, "error": str(data), "payload_preview": payload}
            return {"mode": "app_bot", "sent": True, "data": data.get("data", {})}
    except Exception as exc:  # noqa: BLE001
        return {"mode": "app_bot_failed", "sent": False, "error": str(exc), "payload_preview": payload}


def send_app_bot_text_to_chat(text: str, chat_id: str | None = None) -> dict[str, Any]:
    target = chat_id or settings.feishu_default_chat_id
    if not target:
        return _dry_run({"text": text}, "Missing chat_id and FEISHU_DEFAULT_CHAT_ID")
    return _send_message(target, "chat_id", "text", {"text": text})


def send_app_bot_text_to_user(text: str, open_id: str | None = None) -> dict[str, Any]:
    target = open_id or settings.feishu_default_open_id
    if not target:
        return _dry_run({"text": text}, "Missing open_id and FEISHU_DEFAULT_OPEN_ID")
    return _send_message(target, "open_id", "text", {"text": text})


def build_static_card_from_demo_last_run(demo_data: dict[str, Any]) -> dict[str, Any]:
    baseline = demo_data.get("baseline_run", {})
    changed = demo_data.get("changed_run", {})
    reports = demo_data.get("report_summaries", [])
    generated_at = demo_data.get("generated_at", "")

    elements: list[dict[str, Any]] = [
        {"tag": "markdown", "content": f"**运行时间**: {generated_at}"},
        {
            "tag": "markdown",
            "content": (
                f"**Baseline**: snapshots={baseline.get('snapshots_count', 0)}, "
                f"changes={baseline.get('changes_count', 0)}, reports={baseline.get('reports_count', 0)}"
            ),
        },
        {
            "tag": "markdown",
            "content": (
                f"**Changed**: snapshots={changed.get('snapshots_count', 0)}, "
                f"changes={changed.get('changes_count', 0)}, reports={changed.get('reports_count', 0)}"
            ),
        },
        {"tag": "hr"},
    ]

    if not reports:
        elements.append({"tag": "markdown", "content": "_暂无商品分析摘要_"})
    else:
        for item in reports:
            product_name = item.get("product_name", "Unknown Product")
            summary = item.get("summary", "")
            priority = item.get("priority", "unknown")
            suggested_action = item.get("suggested_action", "无")
            elements.append(
                {
                    "tag": "markdown",
                    "content": (
                        f"**{product_name}**\n"
                        f"- summary: {summary}\n"
                        f"- priority: {priority}\n"
                        f"- suggested_action: {suggested_action}"
                    ),
                }
            )

    return {
        "header": {"title": {"tag": "plain_text", "content": "Ecom Watch Agent Demo Result"}},
        "elements": elements,
    }


def send_static_card_to_chat_from_demo(chat_id: str | None = None) -> dict[str, Any]:
    target = chat_id or settings.feishu_default_chat_id
    if not target:
        return _dry_run({"msg_type": "interactive"}, "Missing chat_id and FEISHU_DEFAULT_CHAT_ID")
    demo_data = _resolve_card_data()
    card = build_static_card_from_demo_last_run(demo_data)
    return _send_message(target, "chat_id", "interactive", card)


def send_static_card_to_user_from_demo(open_id: str | None = None) -> dict[str, Any]:
    target = open_id or settings.feishu_default_open_id
    if not target:
        return _dry_run({"msg_type": "interactive"}, "Missing open_id and FEISHU_DEFAULT_OPEN_ID")
    demo_data = _resolve_card_data()
    card = build_static_card_from_demo_last_run(demo_data)
    return _send_message(target, "open_id", "interactive", card)

