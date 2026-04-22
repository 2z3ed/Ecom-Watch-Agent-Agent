import json
from typing import Any

import httpx

from app.core.config import settings


def _mock_analysis(product_name: str, events: list[dict[str, Any]]) -> dict[str, str]:
    if not events:
        return {
            "summary": f"{product_name} 暂无变化。",
            "priority": "low",
            "suggested_action": "继续保持监控，暂无需人工干预。",
        }

    event_types = [event["event_type"] for event in events]
    has_price = "price_changed" in event_types
    has_stock = "stock_changed" in event_types
    has_promo = "promotion_changed" in event_types

    priority = "medium"
    if has_stock and has_price:
        priority = "high"

    summary_parts: list[str] = []
    if has_price:
        summary_parts.append("价格发生变动")
    if has_stock:
        summary_parts.append("库存状态发生变化")
    if has_promo:
        summary_parts.append("活动标签发生变化")

    summary = f"{product_name}：" + "，".join(summary_parts) + "。"
    suggested_action = "建议运营同学复核竞品变化，并评估是否调整我方商品策略。"

    return {
        "summary": summary,
        "priority": priority,
        "suggested_action": suggested_action,
    }


def _build_prompt(product_name: str, events: list[dict[str, Any]]) -> str:
    payload = {"product_name": product_name, "events": events}
    return (
        "你是电商竞品监控分析助手。请基于输入变化事件输出严格 JSON，字段仅允许："
        "summary, priority, suggested_action。"
        "priority 只能是 low/medium/high。\n"
        f"输入: {json.dumps(payload, ensure_ascii=False)}"
    )


def _real_llm_analysis(product_name: str, events: list[dict[str, Any]]) -> dict[str, str]:
    prompt = _build_prompt(product_name, events)
    headers = {"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"}
    body = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": "你只输出 JSON，不要输出其他文本。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    url = settings.llm_base_url.rstrip("/") + "/chat/completions"

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return {
            "summary": parsed["summary"],
            "priority": parsed["priority"],
            "suggested_action": parsed["suggested_action"],
        }


def analyze_changes(product_name: str, events: list[dict[str, Any]]) -> dict[str, str]:
    if settings.llm_enabled and settings.llm_api_key:
        try:
            return _real_llm_analysis(product_name, events)
        except Exception:  # noqa: BLE001
            return _mock_analysis(product_name, events)
    return _mock_analysis(product_name, events)
