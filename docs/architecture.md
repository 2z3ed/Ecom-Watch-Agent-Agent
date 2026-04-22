# 架构说明（第二轮）

## 当前版本架构

当前采用单体 FastAPI 架构，按模块分层：

- `collector`：Playwright 采集与截图
- `parser + normalizer`：字段抽取与标准化
- `snapshot_service + diff_service`：快照存储与变化检测
- `analyzer`：变化事件分析（real LLM + fallback mock）
- `notifier`：飞书 webhook 通知（未配置时 dry-run）
- `monitor_runner`：编排整条任务链路

## 为什么选 FastAPI + SQLite + Playwright

- FastAPI：接口开发快，适合 Demo 展示
- SQLite：零运维，便于本地演示和回查
- Playwright：可稳定抓取并生成截图证据

## 为什么暂不引入 Redis/Celery/Postgres 等

当前目标是最小可运行闭环，不追求复杂调度或分布式能力。
引入这些组件会提高演示成本且超出本阶段目标。

## 第二轮新增能力

- 新增 `agent_reports` 表，存储结构化分析结果
- 新增 `analyzer`，支持 LLM 与 mock fallback
- 新增 `notifier`，支持 webhook 与 dry-run
- 新增任务/报告查询接口，支持任务与结果回查

## P6 发现层补充（第一轮）

- 新增 `discovery` 作为发现层，用于根据 query 获取候选 URLs
- discovery 当前仅作为辅助能力，不是主演示入口
- discovery 当前与主监控链路解耦，不接入 snapshot/diff/analyzer

## 为什么 discovery 不是主演示入口

- discovery 依赖外部搜索可用性，稳定性低于 mock + Playwright
- 当前面试演示主链路仍需保证“可控、可复现、可留痕”

## 为什么当前只做轻量接入

- P6 第一轮目标是最小可运行，不是平台重构
- 先证明“发现层可用”，后续再接 scrapy 与多源路由

## P6 多源分发补充（第三轮）

- `source_router`：负责 source_type 最小路由判断（`mock_playwright` / `discovery` / `static_scrapy`）
- `scrape_dispatcher`：负责调用各来源服务并输出统一摘要结构
- `run_multi_source_demo.py`：统一演示入口，分别展示三类来源的最小结果

当前阶段 `source_router` / `scrape_dispatcher` 只用于演示分发能力，不接入主监控链路。

## P6 桥接验证补充（第四轮）

- dispatcher 输出是“多源摘要结构”，用于统一观察不同来源结果
- bridge demo 会将摘要映射为“统一采集结构实验形态”，仅用于验证映射可行性
- 第四轮仍不把映射结果正式接入 snapshot/diff/analyzer

先做 bridge demo 的原因：

- 降低改动风险，避免影响前 1-6 轮稳定链路
- 在进入主链路前，先验证 discovery/scrapy/playwright 的字段可对齐程度

## P7 第一轮补充：候选池（Candidate Pool）

本轮在 discovery 与正式监控对象之间新增候选池层：

- `candidate_batches`：记录一次 discovery 业务查询批次
- `candidate_items`：记录该批次下的候选 URL 明细

候选池位置：

1. discovery 发现结果
2. 写入 candidate pool（批次 + 候选项）
3. 下一轮再从候选池进入正式监控对象

## 候选池与正式监控对象的区别

- 候选池：发现结果的暂存与筛选层，允许存在未选中项
- 正式监控对象：进入持续监控闭环的数据对象（当前轮次通过 `products` 承接）

当前先做候选池而不直接写正式监控对象，原因是：

- 避免 discovery 噪声直接污染正式监控集
- 保留发现过程可回查记录（老板可理解“这批候选从何而来”）
- 为下一轮“加入监控”动作提供稳定输入

## P7 第二轮补充：加入监控与 baseline

当前业务流新增：

1. 候选项（`candidate_items`）或 URL 直接输入
2. 转为正式监控对象（当前复用 `products`）
3. 触发最小 baseline（首次采集 + 首快照写入）
4. 进入后续可持续监控状态

新增接口：

- `POST /internal/monitor/add-from-candidates`
- `POST /internal/monitor/add-by-url`

当前 baseline 位置与边界：

- 位置：在“加入监控”动作之后，作为首个留痕节点
- 边界：仅做首次采集与首快照，不默认进入 diff/analyzer/notifier

## P7 第三轮补充：老板视角查询（summary / detail / report）

在完成“候选池 -> 加入监控 -> baseline”后，本轮补齐老板常用的查询动作：

1. `summary/today`：看今天整体变化与重点建议
2. `products/{id}/detail`：看单商品当前状态、最近变化、最新建议
3. `reports/latest`：快速拿到最近一条“可执行建议”，便于后续 A 调用

当前为什么先补查询能力再做 A/B 对接：

- 先把 B 侧“老板语义的稳定数据面”补齐，A 才能做入口编排而不关心底层细节
- 查询接口稳定后，飞书入口/交互卡片才能更低风险地对接与迭代

## P7 第四轮补充：监控对象管理（pause/resume/delete）

在“加入监控 + baseline + 查询能力”具备后，本轮补齐最小管理动作：

- list：查看当前监控对象集合
- pause/resume：通过 `is_active` 控制是否参与后续监控任务
- delete：当前实现为软删除/停用（保留历史留痕）

这样 B 侧形成完整的老板需求动作闭环（发现 -> 加入 -> 查询 -> 管理），但仍不进入 A/B 对接阶段。

## P7 收口后：B 在整体架构中的角色

P7 收口后，项目 B 的角色更清晰：

- B 是“业务服务层”：提供老板语义的 internal API（发现/加入/查询/管理）
- B 负责数据留痕与可回查（候选池、监控对象、快照、变化、报告）
- B 不负责入口编排与会话体验（那是未来项目 A 的职责）

因此，后续做 A/B 对接时，A 只需要调用 B 的 internal API 契约即可，
而不需要直接理解 Playwright/Scrapy/DB/diff/analyzer 等底层实现细节。

## 后续升级路线

1. 增加 `diff_service` 和 `analyzer` 单元测试
2. 增加任务失败重试和更细粒度错误分类
3. 在保持单体前提下增强任务触发与筛选能力
4. 评估再升级到消息队列与外部数据库
