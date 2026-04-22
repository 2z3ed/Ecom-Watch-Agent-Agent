# Ecom Watch Agent Demo

一个用于面试展示的最小可运行“电商竞品监控与分析 Agent”闭环系统（当前完成 P1 + P2 + P3 + P4 + P5 最小版）。

## 本轮实现内容

- FastAPI 基础服务与健康检查接口：`GET /health`
- SQLite 表结构：`products`、`monitor_tasks`、`snapshots`、`change_events`、`agent_reports`
- Playwright 采集 mock 商品页面并截图
- 字段解析与统一结构标准化
- 快照入库与三类变化检测：`price_changed`、`stock_changed`、`promotion_changed`
- analyzer：支持 real LLM mode + fallback mock mode
- notifier：支持飞书 webhook + dry-run mode
- 任务与报告接口：
  - `POST /api/v1/tasks/run`
  - `GET /api/v1/tasks/latest`
  - `GET /api/v1/tasks/{task_id}`
  - `GET /api/v1/reports/latest`
- 可控 mock 演示链路（`baseline`/`changed` 两态切换）
- 本地脚本：初始化 DB、写入种子商品、执行一次监控任务、切换 mock 状态

## 环境要求

- Python 3.11+
- Linux/macOS/WSL

## 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 安装 Playwright 浏览器

```bash
python -m playwright install chromium
```

## 初始化数据库

```bash
python scripts/init_db.py
```

## 写入 mock 商品

```bash
python scripts/seed_products.py
```

## 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
```

访问接口：

- [http://127.0.0.1:8005/health](http://127.0.0.1:8005/health)
- [http://127.0.0.1:8005/api/v1/tasks/latest](http://127.0.0.1:8005/api/v1/tasks/latest)
- [http://127.0.0.1:8005/api/v1/reports/latest](http://127.0.0.1:8005/api/v1/reports/latest)

可选访问 mock 页面（取决于当前状态）：

- [http://127.0.0.1:8005/mock/products/product-phone](http://127.0.0.1:8005/mock/products/product-phone)

## 第一次运行 demo（baseline）

确保 `data/mock_pages/state.txt` 为 `baseline`，然后运行：

```bash
python scripts/run_demo_once.py
```

预期：采集成功、快照入库成功、变化事件为空或很少（首次一般为空）。

## 切换到 changed 状态

```bash
python scripts/switch_mock_state.py
```

该脚本会在 `baseline` 与 `changed` 间切换。

## 第二次运行并查看 diff

```bash
python scripts/run_demo_once.py
```

预期：输出并入库多类变化事件（价格、库存、活动标签）。

## 查看结果方法

- 命令行输出：`run_demo_once.py` 会打印任务、快照、变化事件、分析报告
- 截图文件：`data/screenshots/`
- SQLite 数据库：`data/app.db`

## 第二轮配置说明（可选）

默认无需真实 LLM key 和飞书 webhook，也可完整跑通（mock + dry-run）。

如需真实 LLM：

- `LLM_ENABLED=true`
- `LLM_BASE_URL`（OpenAI 兼容地址）
- `LLM_API_KEY`
- `LLM_MODEL`

如需真实飞书通知：

- 配置 `FEISHU_WEBHOOK_URL`

## 演示前检查

建议每次面试演示前先执行：

```bash
python scripts/check_demo_ready.py
```

该脚本会检查：

- `data/app.db` 是否存在
- `products` 是否已 seed
- mock 状态文件是否存在
- `data/screenshots/` 是否可写
- Playwright 浏览器是否可启动
- `/health` 是否可访问（默认检查 `127.0.0.1:8005`）

## 一键演示命令

### 干净一键演示

```bash
python scripts/run_demo_flow.py --reset-db
```

推荐面试现场使用 `--reset-db`，会在运行前清理以下历史演示数据：

- `monitor_tasks`
- `snapshots`
- `change_events`
- `agent_reports`

并保留 `products`，然后自动执行：

1. set `baseline`
2. baseline 首跑
3. switch to `changed`
4. changed 二跑
5. 输出关键摘要：
   - `task_id`
   - `snapshots_count`
   - `changes_count`
   - `reports_count`
   - 每个商品的 `summary` / `priority`
6. 固化结果到 `data/demo_last_run.json`

如果不加参数：

```bash
python scripts/run_demo_flow.py
```

则会保留历史任务数据，baseline 可能出现 `changes_count > 0`。

## 离线展示最近一次演示结果

`data/demo_last_run.json` 会保存最近一次一键演示摘要，可用于 API 或浏览器异常时的离线展示。

推荐展示方式：

1. 打开 `data/demo_last_run.json`，展示 baseline 与 changed 两轮关键指标
2. 配合 `data/screenshots/` 展示页面证据
3. 配合数据库 `data/app.db` 展示留痕结果

## API smoke test

服务启动后执行：

```bash
python scripts/smoke_api.py
```

会自动校验：

- `/health`
- `/api/v1/tasks/latest`
- `/api/v1/reports/latest`
- `/api/v1/tasks/{task_id}`（基于 latest task）
- `data/demo_last_run.json` 是否存在且结构完整（`generated_at`、`baseline_run`、`changed_run`、`report_summaries`）

脚本失败时返回非 0 退出码，便于快速判断是否可演示。

## 飞书企业自建应用（静态卡片版）

当前支持“企业自建应用机器人”发送能力，范围仅包含：

- 测试文本消息发送
- 基于 `data/demo_last_run.json` 的静态卡片发送
- 群聊发送（`chat_id`）
- 单聊发送（`open_id`）
- dry-run/mock 兜底（配置不完整也不阻断本地演示）

不包含按钮交互、回调、项目 A/B 对接。

### 环境变量

请在 `.env` 中配置（字段名与 AGENTS 约束一致）：

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_ENABLE_APP_BOT`
- `FEISHU_DEFAULT_CHAT_ID`
- `FEISHU_DEFAULT_OPEN_ID`
- `FEISHU_USE_DEMO_LAST_RUN`
- `FEISHU_ENABLE_SEND`

### 推荐打通顺序

1. 发送测试文本消息（群聊）

```bash
python scripts/send_app_bot_test_text.py --target chat
```

2. 发送静态卡片（群聊，数据源默认 `demo_last_run.json`）

```bash
python scripts/send_demo_static_card.py --target chat
```

3. 发送静态卡片（单聊）

```bash
python scripts/send_demo_static_card.py --target user
```

如需覆盖默认目标，可显式传参：

- `--chat-id <chat_id>`
- `--open-id <open_id>`

当 `FEISHU_ENABLE_SEND=false` 或配置缺失时，脚本会返回 dry-run 结果预览，不会真正发送。

## P6 Discovery 最小能力（第一轮）

当前新增 discovery 发现层（SearXNG）用于辅助发现候选 seed URLs，范围仅包含：

- 输入 query
- 调用 SearXNG 获取候选 URL
- 最小 URL 去重
- 最小域名过滤（allowed_domains）
- 独立 demo 运行脚本

当前 discovery 不是主演示入口，不影响现有 mock + Playwright 主链路。

### 配置项

在 `.env` 中可配置：

- `ENABLE_DISCOVERY`
- `SEARXNG_BASE_URL`
- `SEARXNG_TIMEOUT`
- `SEARXNG_DEFAULT_LIMIT`
- `SEARXNG_ALLOWED_DOMAINS`（逗号分隔）

### 运行 discovery demo

```bash
python scripts/run_discovery_demo.py --query "wireless headphone"
python scripts/run_discovery_demo.py --query "gaming keyboard" --limit 5
python scripts/run_discovery_demo.py --query "phone case" --allowed-domains example.com demo.com
```

如果 SearXNG 不可用或未配置，脚本会明确提示并返回 fallback 结果（仅用于本地开发演示兜底）。

## P6 Scrapy 最小能力（第二轮）

当前新增独立 Scrapy demo 能力（静态页面最小接入），用于补充采集能力展示。

本轮只做：

- 1 类静态页面采集
- 独立脚本演示
- 输出统一字段兼容结构
- fixture/mock 兜底

本轮不做：

- 不接 snapshot / diff / analyzer 主链路
- 不改 run_demo_flow.py
- 不改飞书发送主流程
- 不做 discovery + scrapy 串联

### 运行 Scrapy demo

```bash
python scripts/run_scrapy_demo.py
python scripts/run_scrapy_demo.py --source fixture
python scripts/run_scrapy_demo.py --source real --url https://example.com
```

### fixture/mock 与真实抓取区别

- `source_mode=fixture`：表示当前使用本地 fixture 演示结果（稳定、可控）
- `source_mode=real`：表示当前来自真实 URL
- 若真实 URL 抓取失败，会明确提示并回退 fixture，不会静默失败

## P6 第三轮：多源分发最小演示

当前新增统一分发演示入口（不接主链路）：

- `source_router`：做 source_type 路由与校验
- `scrape_dispatcher`：调用对应来源服务并返回统一摘要
- `run_multi_source_demo.py`：一条脚本演示多来源结果

三类来源职责：

- `mock_playwright`：沿用现有 mock + Playwright 采集能力做最小演示
- `discovery`：返回候选 URL 列表（发现层）
- `static_scrapy`：返回静态页面采集结果（fixture/real）

当前阶段不接主链路的原因：

- 先验证“多源分发能力可演示”
- 避免影响前 1-6 轮已通过闭环

### 运行 run_multi_source_demo.py

```bash
python scripts/run_multi_source_demo.py --source mock_playwright
python scripts/run_multi_source_demo.py --source discovery --query "wireless headphone"
python scripts/run_multi_source_demo.py --source static_scrapy --mode fixture
```

可选一次跑三类来源：

```bash
python scripts/run_multi_source_demo.py --source all --query "gaming keyboard"
```

## P6 第四轮：桥接验证版（实验）

当前第四轮新增桥接验证脚本，只做“分发结果到统一结构映射”的实验展示，不接正式主链路。

新增脚本：

- `scripts/run_multi_source_bridge_demo.py`

它会打印两段内容：

1. `scrape_dispatcher` 原始摘要输出
2. 映射后的“统一采集结构实验输出”

### 运行桥接验证

```bash
python scripts/run_multi_source_bridge_demo.py --source all --query "wireless headphone" --mode fixture
```

### 多源摘要 vs 统一结构映射

- 多源摘要：面向分发演示，核心是 `source_type/source_mode/records_count/preview_items`
- 统一结构映射：面向后续主链路接入的实验形态（本轮仅打印，不入库、不进 diff/analyzer）

### 当前为什么仍不接正式主链路

- 先验证映射可行性，避免直接改动已通过的稳定闭环
- 保证 run_demo_flow / smoke_api / 飞书入口不退化

## P6 回归检查

新增脚本：

```bash
python scripts/check_p6_regression.py
```

会检查以下入口仍可运行：

- `run_demo_flow.py --reset-db`
- `smoke_api.py`
- 飞书静态卡片发送入口（至少 dry-run 可用）

## P7 第一轮：老板需求补足层（候选池）

本轮把 discovery 从“技术 demo 输出”升级为“业务候选池落库”。

新增能力：

- 候选批次：`candidate_batches`
- 候选项：`candidate_items`
- 业务接口：`POST /internal/discovery/search`
- 批次查询：`GET /internal/discovery/batches/{batch_id}`

当前关系：

- `app/services/discovery.py`：底层 discovery 能力（保留）
- `app/services/discovery_business_service.py`：候选池业务封装
- `scripts/run_discovery_demo.py`：P6 技术演示入口（保留）
- `/internal/discovery/*`：P7 产品语义接口

### 调用示例

1. 发起 discovery 并落候选池

```bash
curl -X POST "http://127.0.0.1:8005/internal/discovery/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "wireless headphone",
    "limit": 5,
    "allowed_domains": ["example.com", "demo.com"]
  }'
```

2. 查询候选批次

```bash
curl "http://127.0.0.1:8005/internal/discovery/batches/1"
```

返回结构可作为“加入监控”接口的输入。

## P7 第二轮：加入监控与最小 baseline

当前在不影响前 1-6 轮主链路的前提下，补齐“加入监控”最小动作。

新增接口：

- `POST /internal/monitor/add-from-candidates`
- `POST /internal/monitor/add-by-url`

能力边界（本轮）：

- 支持从候选项创建正式监控对象（当前复用 `products` 作为 monitor target 层）
- 支持从 URL 直接创建正式监控对象
- 创建后触发一次最小 baseline（只做首次采集 + 首快照写入）
- 默认不进入 diff / analyzer / notifier 流程
- 当前仍不做今日摘要 / 商品详情 / 监控对象管理

### 调用示例

1. 从候选项加入监控并建立 baseline

```bash
curl -X POST "http://127.0.0.1:8005/internal/monitor/add-from-candidates" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": 1,
    "candidate_ids": [1, 2],
    "source_type": "static_scrapy"
  }'
```

2. 从 URL 直接加入监控并建立 baseline

```bash
curl -X POST "http://127.0.0.1:8005/internal/monitor/add-by-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/products/demo-1",
    "source_type": "static_scrapy",
    "product_name_hint": "Demo Product"
  }'
```

## P7 第三轮：老板视角查询能力

本轮新增“老板视角查询能力”（只做查询，不做管理，不进入 A/B 对接）：

- 今日摘要：`GET /internal/summary/today`
- 商品详情：`GET /internal/products/{id}/detail`
- 最近报告：`GET /internal/reports/latest`（内部语义整理，结构更稳定）

### 调用示例

1. 今日摘要

```bash
curl "http://127.0.0.1:8005/internal/summary/today"
```

2. 商品详情

```bash
curl "http://127.0.0.1:8005/internal/products/1/detail"
```

3. 最近报告（内部语义）

```bash
curl "http://127.0.0.1:8005/internal/reports/latest"
```

当前仍不做：

- 监控对象管理（pause/resume/delete）
- A/B 对接
- 飞书入口改造与按钮交互

## P7 第四轮：监控对象管理（最小版）

本轮新增“监控对象管理”最小接口，仍不进入 A/B 对接、不改飞书入口、不引入复杂状态机。

说明：

- 当前复用 `products` 表承接“正式监控对象（monitor targets）”语义
- `is_active=true` 表示参与后续监控任务
- `is_active=false` 表示暂停/停用（保留快照与报告留痕）
- `DELETE` 当前实现为“软删除/停用”，不做硬删

新增接口：

- `GET /internal/monitor/targets`
- `POST /internal/monitor/{id}/pause`
- `POST /internal/monitor/{id}/resume`
- `DELETE /internal/monitor/{id}`

### 调用示例

```bash
curl "http://127.0.0.1:8005/internal/monitor/targets"
curl "http://127.0.0.1:8005/internal/monitor/targets?include_inactive=false"

curl -X POST "http://127.0.0.1:8005/internal/monitor/1/pause"
curl -X POST "http://127.0.0.1:8005/internal/monitor/1/resume"
curl -X DELETE "http://127.0.0.1:8005/internal/monitor/1"
```

## Internal API 契约（给项目 A 调用）

internal API 的统一返回格式（`ok/data/error`）与接口清单见：

- `docs/internal-api-contract.md`

## P7 收尾：最小串联演示脚本

新增脚本（不接飞书入口，仅演示 internal API 串联）：

```bash
python3 scripts/run_p7_boss_flow_demo.py
```

可选参数示例：

```bash
python3 scripts/run_p7_boss_flow_demo.py --query "gaming keyboard" --limit 5 --pause-after --resume-after
```

## P7 演示稳定性收口

本项目已将老板需求流收口为可稳定演示的 4 个动作：

- 发现（discovery -> 候选池）
- 加入（候选项/URL -> 监控对象 + baseline）
- 查询（今日摘要/商品详情/最近报告）
- 管理（targets 列表 + pause/resume/delete）

并统一 internal API 返回风格为 `ok/data/error`，便于后续项目 A 作为入口层直接调用。

建议演示顺序：

1. `python scripts/run_demo_flow.py --reset-db`（跑通主链路并固化 demo_last_run.json）
2. 启动服务（8005）
3. `python3 scripts/run_p7_boss_flow_demo.py`（串联老板需求流）
4. `python scripts/check_p7_regression.py`（回归自检）
