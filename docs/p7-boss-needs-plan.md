# P7：老板需求补足层（规划）

## 1. 阶段目标

P7 的目标是在不进入 A/B 对接的前提下，把项目 B 从“技术闭环 Demo”补足为“老板可理解的业务服务层”。

本阶段聚焦 5 类需求：

1. 发现商品
2. 加入监控
3. 查看今日变化摘要
4. 查看商品详情
5. 管理监控对象

## 2. 第一轮范围（当前已做）

第一轮只做“候选池”：

- discovery search 结果落库为候选批次（candidate batch）
- 候选批次下保存候选项（candidate items）
- 提供查询批次接口供后续“加入监控”复用

对应接口：

- `POST /internal/discovery/search`
- `GET /internal/discovery/batches/{batch_id}`

## 3. 第二轮范围（当前已做）

第二轮在第一轮基础上新增：

- 从候选项加入监控：`POST /internal/monitor/add-from-candidates`
- 从 URL 直接加入监控：`POST /internal/monitor/add-by-url`
- 最小 baseline 建立：创建 monitor task 并写入首快照

当前“正式监控对象层”采用复用 `products` 表承接，并通过业务服务语义区分：

- `candidate_items`：候选项
- `products`：正式监控对象（monitor target）

## 4. 当前不做什么

本轮明确不做：

- 今日摘要
- 商品详情
- 监控对象管理
- A/B 对接
- 飞书入口改造、按钮交互、回调

## 5. 候选池在老板需求流中的作用

候选池是“发现 -> 选择 -> 加入监控”之间的缓冲层：

1. 先通过 discovery 获取候选 URL
2. 把结果稳定落到批次和候选项
3. 通过“加入监控”动作从候选池挑选正式监控对象

## 6. baseline 在老板需求流中的作用

当前 baseline 只做首次采集与首快照写入，目标是完成“对象已进入监控并有初始留痕”。

本轮 baseline 明确不做：

- diff 检测
- analyzer 分析
- notifier 通知

这样可以避免 discovery 结果直接污染正式监控对象，并保留可回查的发现留痕。

## 7. 下一轮预告

第三轮将实现：

- 今日摘要能力：`GET /internal/summary/today`
- 商品详情能力：`GET /internal/products/{id}/detail`
- 最近报告能力：`GET /internal/reports/latest`

这些能力用于老板视角“看今天有什么变化、重点看哪些商品、每个商品发生了什么”的查询动作。

仍不进入 A/B 对接与飞书入口改造。

## 第四轮范围（当前已做）：监控对象管理（最小版）

第四轮补齐“老板可操作的管理动作”（最小版）：

- 监控对象列表：`GET /internal/monitor/targets`
- 暂停：`POST /internal/monitor/{id}/pause`
- 恢复：`POST /internal/monitor/{id}/resume`
- 删除：`DELETE /internal/monitor/{id}`（当前实现为软删除/停用）

当前仍不做：

- 多租户/权限系统
- 复杂状态机与审计
- A/B 对接与飞书入口改造
