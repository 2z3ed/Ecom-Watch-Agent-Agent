# Internal API 契约（给项目 A 调用）

本文件描述项目 B 对外暴露的 **internal API 契约**，用于后续项目 A 作为入口层调用。

约束：

- 当前不做 A/B 对接实现，只提供稳定可调用的 B 侧接口
- 不改飞书入口主流程
- 统一端口：`8005`

## Base URL

- `http://127.0.0.1:8005`

## 统一返回 Envelope

所有 `/internal/*` 接口统一返回：

```json
{
  "ok": true,
  "data": { },
  "error": null
}
```

失败时：

```json
{
  "ok": false,
  "data": null,
  "error": {
    "message": "product not found",
    "code": "HTTP_404",
    "status_code": 404,
    "request_id": "optional",
    "timestamp": "2026-04-22T12:00:00"
  }
}
```

说明：

- `error.code` 当前最小约定：`HTTP_<status>` 或 `VALIDATION_ERROR`
- `request_id` 可由调用方通过 `X-Request-Id` 传入；未传时服务端会生成

## 能力分层语义（重要）

- `candidate_items`：候选项（发现结果）
- `products`：正式监控对象（monitor targets）
  - `is_active=true` 参与后续监控任务
  - `is_active=false` 暂停/停用（保留历史留痕）
  - `DELETE` 当前实现为软删除/停用

## API 列表（P7）

### Discovery（候选池）

- `POST /internal/discovery/search`
- `GET /internal/discovery/batches/{batch_id}`

### 加入监控 + baseline

- `POST /internal/monitor/add-from-candidates`
- `POST /internal/monitor/add-by-url`

### 老板查询

- `GET /internal/summary/today`
- `GET /internal/products/{id}/detail`
- `GET /internal/reports/latest`

### 监控对象管理（最小版）

- `GET /internal/monitor/targets`
- `POST /internal/monitor/{id}/pause`
- `POST /internal/monitor/{id}/resume`
- `DELETE /internal/monitor/{id}`

## 典型调用链（演示用）

1. discovery：创建候选批次
2. add：加入监控（建立最小 baseline）
3. query：summary/detail/report
4. manage：pause/resume

对应最小演示脚本见：`scripts/run_p7_boss_flow_demo.py`

### 示例调用链（最小）

1) 发现候选：

- `POST /internal/discovery/search` -> `data.batch_id` 与 `data.candidates[*].candidate_id`

2) 加入监控（两种方式二选一）：

- 候选加入：`POST /internal/monitor/add-from-candidates`
- URL 加入：`POST /internal/monitor/add-by-url`

3) 查询：

- `GET /internal/summary/today`
- `GET /internal/products/{id}/detail`

4) 管理：

- `POST /internal/monitor/{id}/pause`
- `POST /internal/monitor/{id}/resume`
