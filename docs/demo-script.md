# 3-5 分钟演示脚本（第三轮）

## 0. 演示前准备

1. 激活环境并确认依赖已安装
2. 运行 `python scripts/check_demo_ready.py`
3. 确认 `data/mock_pages/state.txt` 为 `baseline`
4. 若要展示接口，提前启动服务：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8005`

## 1. 业务问题

运营同学需要持续关注竞品商品的价格、库存和活动变化，手工巡检成本高且易遗漏。

## 2. 系统怎么工作

本 Demo 走完整链路：
采集 mock 商品页 -> 快照入库 -> diff 检测 -> 变化分析 -> 飞书通知（或 dry-run）-> 接口回查。

## 3. 现场操作步骤

1. 启动服务：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8005`
2. 确认状态 baseline，执行：`python scripts/run_demo_once.py`
3. 切换状态：`python scripts/switch_mock_state.py`
4. 再执行：`python scripts/run_demo_once.py`
5. 查看接口：
   - `GET /api/v1/tasks/latest`
   - `GET /api/v1/reports/latest`
   - `GET /api/v1/tasks/{task_id}`

## 4. 现场应看到什么

- 第二次运行出现 `price_changed` / `stock_changed` / `promotion_changed`
- 产生 `agent_reports` 记录，包含 `summary/priority/suggested_action`
- 未配置飞书时，流程依然可跑通（dry-run）

## 5. 这个 Demo 证明了什么

该 Demo 已证明采集型 Agent 最小业务闭环能力：
采集、变化检测、分析、通知、回查全链路可运行且可复现。

## 6. 常见翻车点处理

- **Playwright 启动失败**：执行 `python -m playwright install chromium` 后重试。
- **`/health` 不通**：确认服务是否已启动，以及端口是否是 `8005`。
- **无变化事件**：确认第一次在 `baseline` 跑过一次，再切到 `changed` 跑第二次。
- **无报告记录**：确认第二次运行 `changes_count > 0`，有变化才会写 `agent_reports`。

## 7. 现场最短演示路径

1. 先执行 `python scripts/check_demo_ready.py`
2. 启动服务 `uvicorn app.main:app --reload --host 0.0.0.0 --port 8005`
3. 一键演示 `python scripts/run_demo_flow.py`
4. 快速验接口 `python scripts/smoke_api.py`

这样可以在最少操作下演示完整闭环，降低现场误操作风险。

## 8. 如果只有 2 分钟怎么演示

1. 直接运行 `python scripts/run_demo_flow.py --reset-db`
2. 强调输出中的两段任务摘要（baseline 与 changed）
3. 展示第二段里 `changes_count` 与 `reports_count` 非 0
4. 打开 `data/demo_last_run.json`，快速展示固化结果
5. 口头说明：系统已完成“采集 -> 检测 -> 分析 -> 回查”

## 9. API 或浏览器临时异常时的兜底展示

若接口或浏览器临时异常，不中断演示，切换到证据展示：

1. 展示 `data/demo_last_run.json`（最近一次演示摘要）
2. 展示 `data/screenshots/` 的页面截图证据
3. 展示 `/api/v1/tasks/latest` 与 `/api/v1/reports/latest`（若 API 可用）
4. 展示 `data/app.db` 中留痕结果（`monitor_tasks`/`snapshots`/`change_events`/`agent_reports`）
5. 说明系统已具备自检和失败留痕能力，异常只影响当次现场采集

## 10. 现场最短路径（脚本 + 固化结果）

如果现场时间极短，只做两步：

1. `python scripts/run_demo_flow.py --reset-db`
2. 打开 `data/demo_last_run.json`

即可完成“干净首跑 + 变化二跑 + 分析摘要”的最短演示闭环。
