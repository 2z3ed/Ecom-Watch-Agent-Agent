import argparse
import json
import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="P7 boss flow demo (no feishu entry)")
    p.add_argument("--base-url", default="http://127.0.0.1:8005", help="API base url")
    p.add_argument("--query", default="wireless headphone", help="Discovery query")
    p.add_argument("--limit", type=int, default=5, help="Discovery limit")
    p.add_argument("--add-url", default="mock://product-phone", help="Stable add-by-url target")
    p.add_argument("--add-source-type", default="mock_playwright", help="Source type for add-by-url")
    p.add_argument(
        "--use-add-from-candidates",
        action="store_true",
        help="Prefer discovery -> add-from-candidates when possible; fallback to add-by-url if not.",
    )
    p.add_argument(
        "--candidates-count",
        type=int,
        default=1,
        help="How many candidates to add when using add-from-candidates (default: 1)",
    )
    p.add_argument("--pause-after", action="store_true", help="Pause after add")
    p.add_argument("--resume-after", action="store_true", help="Resume after pause")
    return p.parse_args()


def _must_ok(resp_json: dict, step: str) -> dict:
    if not resp_json.get("ok"):
        raise RuntimeError(f"{step} failed: {json.dumps(resp_json, ensure_ascii=False)}")
    return resp_json["data"]


def _title(text: str) -> None:
    print(f"\n=== {text} ===")


def _bullet(label: str, value: object) -> None:
    print(f"- {label}: {value}")


def _preview_candidates(batch: dict, max_items: int = 3) -> None:
    rows = batch.get("candidates", [])[:max_items]
    if not rows:
        _bullet("候选", "无")
        return
    print("- 候选预览:")
    for item in rows:
        print(f"  - #{item['candidate_rank']} {item['title'][:60]} ({item['domain']})")


def _pick_candidate_ids(batch: dict, k: int) -> list[int]:
    candidates = list(batch.get("candidates", []))
    candidates.sort(key=lambda x: x.get("candidate_rank", 999999))
    picked = []
    for item in candidates:
        cid = item.get("candidate_id")
        if isinstance(cid, int):
            picked.append(cid)
        if len(picked) >= k:
            break
    return picked


def main() -> None:
    args = parse_args()
    base = args.base_url.rstrip("/")

    headers = {"X-Request-Id": "p7-demo"}
    with httpx.Client(timeout=10.0, headers=headers) as client:
        _title("第一步：发现候选")
        r = client.post(
            f"{base}/internal/discovery/search",
            json={"query": args.query, "limit": args.limit},
        )
        _bullet("请求", "discovery/search")
        _bullet("HTTP", r.status_code)
        batch = _must_ok(r.json(), "discovery/search")
        _bullet("批次", batch["batch_id"])
        _bullet("候选数量", batch["count"])
        _preview_candidates(batch)

        _title("第二步：加入监控")
        add = None
        add_mode = "add-by-url"
        if args.use_add_from_candidates:
            candidate_ids = _pick_candidate_ids(batch, max(1, int(args.candidates_count)))
            if not candidate_ids:
                _bullet("候选加入", "不可用：未找到可用 candidate_id，回退到 add-by-url")
            else:
                try:
                    r = client.post(
                        f"{base}/internal/monitor/add-from-candidates",
                        json={
                            "batch_id": batch["batch_id"],
                            "candidate_ids": candidate_ids,
                            # 让后端基于 URL 推断 source_type；如需强制可在未来加参数
                        },
                    )
                    _bullet("请求", "monitor/add-from-candidates")
                    _bullet("HTTP", r.status_code)
                    add = _must_ok(r.json(), "monitor/add-from-candidates")
                    add_mode = "add-from-candidates"
                except Exception as exc:  # noqa: BLE001
                    _bullet("候选加入", f"失败：{exc}，回退到 add-by-url")

        if add is None:
            r = client.post(
                f"{base}/internal/monitor/add-by-url",
                json={"url": args.add_url, "source_type": args.add_source_type, "product_name_hint": "P7 Demo Target"},
            )
            _bullet("请求", "monitor/add-by-url")
            _bullet("HTTP", r.status_code)
            add = _must_ok(r.json(), "monitor/add-by-url")

        _bullet("加入方式", add_mode)
        target = add["targets"][0]
        product_id = target["product_id"]
        _bullet("监控对象ID", product_id)
        _bullet("商品名", target["product_name"])
        _bullet("baseline状态", target["baseline"]["status"])
        if target["baseline"]["status"] != "succeeded":
            _bullet("baseline错误", target["baseline"].get("error"))

        _title("第三步：查看今日摘要")
        r = client.get(f"{base}/internal/summary/today")
        _bullet("请求", "summary/today")
        _bullet("HTTP", r.status_code)
        summary = _must_ok(r.json(), "summary/today")
        _bullet("日期", summary["date"])
        _bullet("监控商品数", summary["total_monitored_products"])
        _bullet("今日有变化商品数", summary["changed_products_count"])
        _bullet("高优先级数", summary["high_priority_count"])
        if summary.get("suggested_actions"):
            print("- 建议动作（去重预览）:")
            for item in summary["suggested_actions"][:3]:
                print(f"  - {item[:120]}")
        else:
            _bullet("建议动作", "无")

        _title("第四步：查看商品详情")
        r = client.get(f"{base}/internal/products/{product_id}/detail")
        _bullet("请求", "products/{id}/detail")
        _bullet("HTTP", r.status_code)
        detail = _must_ok(r.json(), "products/{id}/detail")
        snap = detail.get("current_snapshot")
        if snap:
            _bullet("当前价格", snap["price"])
            _bullet("库存", snap["stock_status"])
            _bullet("活动", snap.get("promotion_text") or "无")
            _bullet("采集时间", snap["collected_at"])
        else:
            _bullet("当前快照", "暂无")
        _bullet("最近变化条数", len(detail.get("recent_change_events", [])))
        rep = detail.get("latest_report")
        if rep:
            _bullet("优先级", rep["priority"])
            _bullet("摘要", rep["summary"][:160])
            _bullet("建议动作", rep["suggested_action"][:160])
        else:
            _bullet("最新报告", "暂无（可能今日无变化）")

        _title("第五步：暂停 / 恢复")
        if args.pause_after:
            r = client.post(f"{base}/internal/monitor/{product_id}/pause")
            _bullet("请求", "monitor/{id}/pause")
            _bullet("HTTP", r.status_code)
            out = _must_ok(r.json(), "monitor/{id}/pause")
            _bullet("状态", out["status"])

        if args.resume_after:
            r = client.post(f"{base}/internal/monitor/{product_id}/resume")
            _bullet("请求", "monitor/{id}/resume")
            _bullet("HTTP", r.status_code)
            out = _must_ok(r.json(), "monitor/{id}/resume")
            _bullet("状态", out["status"])

        if not args.pause_after and not args.resume_after:
            _bullet("提示", "可加 --pause-after / --resume-after 演示管理动作")

        print("\nDone. (P7 boss flow demo)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
        sys.exit(1)
