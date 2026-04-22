# P6 多源采集轻量升级计划（第一、二、三、四轮）

## 1. P6 阶段目标

在不破坏现有稳定演示链路的前提下，为项目补充“多源采集的轻量能力入口”。

## 2. 当前轮只做什么

当前第一轮只做 discovery 最小接入：

- 输入 query
- 调用 SearXNG
- 返回候选 seed URLs
- 做最小 URL 去重
- 做最小域名过滤
- 提供独立 demo 脚本 `run_discovery_demo.py`

## 3. discovery / scrapy / playwright 三层关系

- `discovery`：发现层，负责找候选 URL，不负责主链路采集
- `scrapy`：静态采集补充层（后续轮次接入）
- `playwright`：当前最稳定主演示采集层，保留不动

## 4. 当前不做什么

- 不接 Scrapy
- 不接 snapshot/diff/analyzer 主链路
- 不改 run_demo_flow 主流程
- 不改飞书静态卡片主流程
- 不引入 Redis/Celery/Postgres
- 不做复杂评分与 query expansion

## 5. 第二轮新增（已接入）

当前第二轮只做独立 Scrapy demo：

- 新增 `scrapy_adapter` 最小静态采集能力
- 新增 `scripts/run_scrapy_demo.py`
- 输出最小统一结构字段（与现有结构兼容）
- 支持 fixture/mock 兜底，不依赖外网

## 6. 第二轮当前不做什么

- 不接 snapshot / diff / analyzer 主链路
- 不修改 run_demo_flow 主流程
- 不改飞书发送主流程
- 不做 discovery + scrapy 串联
- 不做多 spider 平台化

## 7. 第三轮新增（已接入）

当前第三轮只做统一分发演示入口：

- 新增 `source_router`（只做 source_type 路由与校验）
- 新增 `scrape_dispatcher`（调用 discovery / scrapy / mock_playwright）
- 新增 `scripts/run_multi_source_demo.py`
- 输出统一摘要结构：`source_type` / `source_mode` / `records_count` / `preview_items`

## 8. 第三轮当前不做什么

- 不接 snapshot / diff / analyzer 主链路
- 不改 run_demo_flow 与飞书主流程
- 不做 discovery + scrapy 复杂联动编排
- 不做平台化插件系统

## 9. 第四轮新增（已接入）

当前第四轮只做桥接验证，不做正式接入：

- 新增 `run_multi_source_bridge_demo.py`
- 展示 dispatcher 原始摘要与统一结构映射结果
- 明确 discovery 仅映射为 candidate，不伪装完整商品快照
- 新增 `check_p6_regression.py` 进行最小回归检查

## 10. 第四轮当前不做什么

- 不接 snapshot / diff / analyzer 正式链路
- 不改 monitor_runner 主流程
- 不改飞书主发送流程

## 11. 下一轮要接什么

下一轮最小目标：

- 评估局部将 bridge 映射结果接入主链路的安全范围
- 优先做可回滚的实验入口，而非替换现有稳定演示链路
