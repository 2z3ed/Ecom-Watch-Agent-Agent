# AGENTS.md

# 项目名称
Ecom Watch Agent Demo

# 项目定位
这是一个“用于面试展示的最小可运行 Agent 闭环系统”，不是生产级大平台，也不是单纯爬虫脚本。

系统目标是围绕“电商竞品监控”场景，完成一条清晰可演示的最小业务闭环：

页面采集  
→ 快照留痕  
→ 变化检测  
→ LLM 分析  
→ 飞书通知  
→ 结果查询

本项目重点展示以下能力：

1. 数据采集能力
2. 页面字段抽取与标准化能力
3. 快照/差异检测能力
4. LLM 在真实业务链中的分析能力
5. 飞书接入与通知能力
6. 最小业务闭环设计能力

---

# 一、总原则

## 1.1 这是面试展示级 MVP，不是生产平台
所有开发决策必须优先满足：

- 先跑通
- 先可演示
- 先可讲清楚
- 先结构清晰
- 不要过度设计

不要为了“看起来高级”引入当前版本不必要的技术复杂度。

## 1.2 当前版本禁止过度平台化
当前版本不要主动引入以下内容，除非我明确要求：

- Redis
- Celery
- Postgres
- MinIO
- Docker 编排
- 微服务拆分
- 多 agent 编排
- 登录态复杂托管
- 分布式调度
- 复杂前端
- 消息队列
- changedetection.io 接入
- Scrapy 主框架
- scrapy-playwright
- SearXNG
- Crawl4AI

这些能力可以在文档中预留扩展位，但当前代码实现不要先做。

## 1.3 当前版本默认技术栈
除非我明确要求替换，否则默认使用：

- Python 3.11+
- FastAPI
- SQLite
- SQLAlchemy 或等价轻量 ORM
- Playwright
- Pydantic
- requests / httpx
- OpenAI 兼容接口
- 飞书 webhook

## 1.4 项目主角不是“爬虫”，而是“采集型 Agent 闭环”
任何代码和文档表述，不要把项目描述成：

- 爬虫系统
- 抓取工具
- 爬虫平台

要统一表述成：

- 电商竞品监控与分析 Agent Demo
- 数据采集型 Agent 闭环系统
- 采集 + 变化检测 + 分析 + 通知的最小业务系统

---

# 二、业务目标

## 2.1 核心业务问题
运营或选品人员需要持续关注竞品商品公开页面中的以下信息：

- 当前价格
- 库存状态
- 活动标签

手工查看效率低、易遗漏，因此需要一个轻量自动化系统：

- 定时或手动采集商品页面
- 自动识别页面关键字段变化
- 自动生成变化摘要
- 自动给出下一步建议
- 自动通过飞书提醒
- 支持留痕与回查

## 2.2 当前版本要证明的能力
当前版本只证明这 6 件事：

1. 我能采集公开页面核心信息
2. 我能做字段标准化
3. 我能做快照留痕
4. 我能做变化检测
5. 我能把 LLM 放进业务链条做分析
6. 我能把结果发到飞书并可回查

---

# 三、当前版本范围

## 3.1 本期必须完成
必须做出以下最小闭环：

1. 支持手动触发一次监控任务
2. 支持配置 3-5 个商品页面
3. 用 Playwright 采集页面
4. 提取并标准化以下字段：
   - 商品名
   - 商品链接
   - 当前价格
   - 库存状态
   - 活动标签
   - 抓取时间
   - 截图路径
5. 将快照写入 SQLite
6. 与上一次快照比对，识别：
   - `price_changed`
   - `stock_changed`
   - `promotion_changed`
7. 对变化事件调用 LLM，输出：
   - `summary`
   - `priority`
   - `suggested_action`
8. 用飞书 webhook 发送提醒
9. 提供 FastAPI 接口：
   - 触发任务
   - 查看最近任务
   - 查看任务详情
10. 提供 README
11. 提供一个 3-5 分钟演示说明文档

## 3.2 本期不要做
以下内容不要主动实现：

- 复杂反爬
- 绕过访问限制
- 验证码处理
- 账号池/代理池
- 多站点自动发现
- 登录电商后台
- 完整工单系统
- 完整管理后台
- 权限系统
- 复杂多租户
- 复杂调度系统
- 复杂消息总线
- 多模型切换平台
- 复杂插件系统

---

# 四、合法合规边界

## 4.1 仅做合法、合规、演示用途的数据采集
只能面向以下场景：

- 公开可访问页面
- 自建 mock 页面
- 明确授权的测试页面
- 可用于合法演示的公开商品详情页

## 4.2 禁止方向
不要实现或强调以下内容：

- 绕过权限控制
- 绕过验证码
- 破解登录限制
- 绕过访问频率限制
- 绕过付费墙
- 绕过明确禁止访问的技术保护
- 规避平台封禁机制

## 4.3 推荐演示策略
默认优先采用：

- 1 组 mock 页面作为稳定演示主链路
- 1-2 个公开商品页面作为补充说明

这样可以保证演示可控，减少现场翻车风险。

---

# 五、系统架构约束

## 5.1 当前版本系统分层
当前版本只实现以下 6 个模块：

1. `collector`
   - 使用 Playwright 获取页面信息与截图

2. `parser`
   - 提取价格、库存、活动、标题等字段

3. `normalizer`
   - 输出统一结构化结果

4. `diff_service`
   - 与最近一次快照比较，生成变化事件

5. `analyzer`
   - 调用 LLM 输出摘要、优先级、建议动作

6. `notifier`
   - 将结果发到飞书 webhook

7. `monitor_runner`
   - 串联整条业务链

## 5.2 当前版本不做复杂异步
当前任务量很小，默认允许串行执行。

如果实现异步，也只能是轻量异步，不要引入独立任务队列和消息系统。

## 5.3 当前版本默认单体结构
当前版本必须保持为单体应用，目录清晰即可，不要拆分微服务。

---

# 六、推荐目录结构

请默认使用如下目录结构，如需微调请保持语义一致：

```text
ecom-watch-agent/
├─ app/
│  ├─ api/
│  │  ├─ routes_health.py
│  │  ├─ routes_tasks.py
│  │  └─ routes_reports.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ logger.py
│  │  ├─ db.py
│  │  └─ constants.py
│  ├─ models/
│  │  ├─ product.py
│  │  ├─ monitor_task.py
│  │  ├─ snapshot.py
│  │  ├─ change_event.py
│  │  └─ agent_report.py
│  ├─ schemas/
│  │  ├─ task.py
│  │  ├─ snapshot.py
│  │  ├─ change_event.py
│  │  └─ report.py
│  ├─ services/
│  │  ├─ collector.py
│  │  ├─ parser.py
│  │  ├─ normalizer.py
│  │  ├─ snapshot_service.py
│  │  ├─ diff_service.py
│  │  ├─ analyzer.py
│  │  ├─ notifier.py
│  │  └─ monitor_runner.py
│  ├─ prompts/
│  │  └─ analyzer_prompt.py
│  └─ main.py
├─ data/
│  ├─ app.db
│  ├─ screenshots/
│  └─ mock_pages/
├─ scripts/
│  ├─ seed_products.py
│  ├─ run_demo_once.py
│  └─ init_db.py
├─ docs/
│  ├─ demo-script.md
│  └─ architecture.md
├─ tests/
├─ README.md
├─ requirements.txt
└─ .env.example

七、数据模型要求

请至少实现以下表：

7.1 products

监控目标表，字段建议：

id
product_name
product_url
source_site
is_active
created_at
updated_at
7.2 monitor_tasks

任务表，字段建议：

id
trigger_type 例如 manual
status 例如 running/succeeded/failed
started_at
finished_at
error_message
7.3 snapshots

快照表，字段建议：

id
task_id
product_id
title
price
stock_status
promotion_text
page_url
screenshot_path
collected_at
7.4 change_events

变化事件表，字段建议：

id
task_id
product_id
event_type
old_value
new_value
change_ratio
detected_at
7.5 agent_reports

分析表，字段建议：

id
task_id
product_id
summary
priority
suggested_action
raw_response
created_at
八、统一结构要求
8.1 采集后的统一结构

所有采集结果必须归一为统一结构，类似：

{
  "product_name": "示例商品",
  "product_url": "https://example.com/p/1",
  "price": 99.0,
  "stock_status": "in_stock",
  "promotion_text": "限时优惠",
  "collected_at": "2026-04-21T12:00:00",
  "screenshot_path": "data/screenshots/demo_001.png"
}
8.2 LLM 输出结构

LLM 必须输出固定结构，不允许随意发散：

{
  "summary": "该商品价格明显下降，同时新增促销标签，可能正在进行短期活动。",
  "priority": "high",
  "suggested_action": "建议人工复核该商品活动力度，并评估是否需要调整我方同类商品定价。"
}
九、变化检测规则

必须实现以下 3 类变化：

9.1 price_changed

规则：

当前价格与上一快照价格不同
可以计算百分比变化
9.2 stock_changed

规则：

库存状态从 in_stock 变成 out_of_stock
或从 out_of_stock 变成 in_stock
9.3 promotion_changed

规则：

活动标签文本不同
可接受空字符串与有值之间的变化
9.4 当前版本不要做复杂规则引擎

变化检测用清晰可读的 Python 逻辑实现即可，不要引入 DSL、策略注册中心等复杂设计。

十、采集实现约束
10.1 当前版本首选 Playwright

默认使用 Playwright 作为当前采集主力。

原因：

更适合动态页面
更适合保存截图
更适合演示
更直观
10.2 当前采集字段只抓核心字段

只抓以下字段：

商品标题
当前价格
库存状态
活动标签

不要扩展太多字段，不要做大而全的页面抽取。

10.3 采集失败时必须留痕

采集失败时至少要保留：

错误信息
任务失败状态
尽量保留截图或上下文
10.4 页面选择策略

优先支持：

mock 页面
少量公开页面

不要把目标定成通吃各种复杂电商站。

十一、LLM 分析约束
11.1 LLM 的职责

LLM 不负责抓页面，也不负责复杂决策编排。

它只负责：

解释变化
生成摘要
判断优先级
给出建议动作
11.2 当前版本禁止复杂 agent 化

不要实现：

多 agent 协作
工具路由
复杂规划
自反思链
自治长流程

当前只做单次结构化分析调用。

11.3 Prompt 必须结构化

Prompt 要尽量固定模板，输入为变化事件结构化数据，输出为固定 JSON 字段。

不要让 Prompt 写成大段空泛自然语言。

十二、飞书通知约束
12.1 当前版本只做轻量通知

默认使用飞书 webhook，优先保证消息送达。

12.2 通知内容建议

通知中建议包含：

商品名
变化类型
变化前后值
LLM 摘要
优先级
建议动作
12.3 当前版本不做复杂交互卡片

如果实现卡片也要保持极简，不要花大量时间在卡片样式和复杂回调上。

十三、API 约束

当前版本至少实现以下接口：

13.1 健康检查

GET /health

返回服务运行状态。

13.2 手动触发监控任务

POST /api/v1/tasks/run

作用：

创建任务
执行一次采集监控流程

返回：

task_id
status
13.3 查看最近任务

GET /api/v1/tasks/latest

作用：

查看最近一次任务结果摘要
13.4 查看任务详情

GET /api/v1/tasks/{task_id}

作用：

查看某次任务完整结果
返回快照、变化事件、分析结果
十四、工程实现风格
14.1 代码风格

要求：

模块职责单一
命名清晰
避免魔法值
避免一堆逻辑全塞在路由里
适度注释，不要注释废话
保持文件大小可读
14.2 不要过早抽象

如果当前只有一个实现，不要提前做一堆接口层和插件层。

例如：

当前只有一个 PlaywrightCollector，可以直接实现
当前只有一个 LLMAnalyzer，可以直接实现

可以预留替换空间，但不要过度设计成框架。

14.3 优先垂直切片

每一轮开发都优先做“从输入到输出能跑通的一条链”，而不是先搭很多空壳模块。

十五、文档要求

必须产出以下文档：

15.1 README.md

README 必须包含：

项目简介
当前能力范围
技术栈
目录结构
环境变量说明
安装依赖
初始化数据库
如何运行服务
如何手动触发任务
如何查看结果
如何演示 mock 页面变化
15.2 docs/demo-script.md

必须提供 3-5 分钟演示脚本，内容包括：

业务问题
系统怎么工作
现场如何操作
看到什么结果
这个 Demo 证明了什么能力
15.3 docs/architecture.md

简要说明：

当前版本架构
当前为什么选 Playwright + FastAPI + SQLite
为什么暂时不接 Scrapy / changedetection.io / Redis 等
后续升级路线
十六、测试与验证要求

当前版本至少做到以下验证：

16.1 基本手动验证

至少可手动验证：

任务可以触发
页面可以采集
快照可以入库
变化可以识别
LLM 可以输出结构化分析
飞书可以收到通知
接口可以查询结果
16.2 最小自动化测试建议

如果时间允许，至少补以下测试：

diff_service 的单元测试
normalizer 的单元测试
analyzer 输出结构解析测试
16.3 不要为了测试拖慢主线

测试重要，但当前项目优先级是先把 Demo 主链路跑通。

十七、开发阶段要求
P1：项目骨架

本阶段目标：

初始化项目结构
建立 FastAPI 服务
建立 SQLite 连接
建立数据表
建立日志模块
提供 /health

交付物：

基础项目结构
数据库 schema
基础配置
健康检查接口
P2：采集能力

本阶段目标：

用 Playwright 打通 3-5 个页面
提取核心字段
保存截图
统一结构输出

交付物：

collector.py
parser.py
normalizer.py
scripts/run_demo_once.py
P3：快照与变化检测

本阶段目标：

快照入库
与最近快照比较
生成变化事件

交付物：

snapshot_service.py
diff_service.py
P4：LLM 分析与飞书通知

本阶段目标：

接入 LLM
输出结构化分析
飞书 webhook 通知

交付物：

analyzer.py
notifier.py
P5：接口与文档

本阶段目标：

提供任务接口
提供结果查询接口
补齐 README
补齐 demo-script

交付物：

API 路由
README
docs
十八、执行策略
18.1 默认执行策略

当我要求你“继续开发”时，默认按以下原则执行：

优先完成当前阶段的可运行闭环
不要停在纯设计和空壳
做出可以运行和演示的最小实现
不要反复追问无关小细节
允许做合理假设，但要写清楚假设是什么
18.2 默认优先级

默认优先级如下：

能运行
能演示
结构清晰
文档可用
再考虑美化和扩展性
18.3 遇到不明确事项时的默认决策

如果没有进一步说明，请按以下默认：

先用 SQLite
先用 webhook
先用 Playwright
先用 mock 页面
先做手动触发
先做串行执行
先做最小字段集
先做最小 JSON 输出
先做本地截图存储
十九、每轮开发结果汇报格式

每一轮完成后，必须按以下格式汇报：

A. 本轮做了什么
修改/新增了哪些文件
每个文件作用是什么
当前完成到哪个阶段
B. 为什么这样改
这轮解决了什么问题
为什么当前实现是最小可行解
C. 现在怎么运行
启动命令
触发命令
查看结果的方法
D. 当前还缺什么
哪些点还没做
哪些点只是占位
哪些风险还没收口
E. 下一轮建议
下一轮最小目标是什么
不要泛泛而谈，要给明确下一步
F. 下一步可直接执行的提示词

每轮结束后，必须直接给出“下一轮可直接发给 agent 的提示词”，不要等我再总结。

二十、第一轮默认任务

如果我没有额外指定，请直接从这里开始做，不要只输出分析。

第一轮目标

一次性尽量完成 P1 + P2 + P3 的最小可运行版本：

建项目骨架
建 SQLite schema
建 FastAPI 基础服务
实现 Playwright 采集最小链路
实现统一结构输出
实现快照入库
实现 diff 逻辑
提供一个本地可运行脚本
提供基础 README
第一轮最低验收标准

本地至少可以做到：

运行一次采集脚本
采集到数据
入库成功
第二次运行时能检测出变化
输出变化事件
二十一、第二轮默认任务

如果第一轮完成，第二轮默认做：

接入 LLM 分析
接入飞书 webhook
提供任务触发接口
提供最近任务查询接口
补任务详情接口
补 demo-script
补 architecture 文档
二十二、第三轮默认任务

如果前两轮完成，第三轮默认做：

补 mock 页面
补截图证据
补失败处理
补最小测试
清理 README
清理配置项
优化演示稳定性
二十三、禁止事项

请不要做以下事情：

不要只写伪代码
不要只给目录不写实现
不要停留在纯分析，不落代码
不要一上来堆复杂架构
不要擅自把项目改成前端主导
不要擅自改成 Node.js 主栈
不要把当前 Demo 变成平台重构项目
不要为了“以后扩展”写大量当前用不到的抽象
不要引入不必要的大依赖
不要在没有说明的情况下接入高风险采集逻辑
二十四、成功标准

如果当前版本成功，应满足以下结果：

这是一个能跑通的最小业务系统
不是只有采集，没有分析
不是只有分析，没有通知
不是只有通知，没有留痕
不是只有代码，没有 README
不是只有 mock，没有真实页面扩展空间
面试时可展示“采集 → 检测 → 分析 → 通知 → 回查”的完整链路
二十五、给 coding agent 的最后指令

从现在开始，默认你是本项目的 coding agent。
你的任务不是讨论“大而全方案”，而是在最少轮次内完成当前版本最重要的可运行闭环。

请优先做出：
P1 + P2 + P3 的最小可运行版本。

除非我明确要求，否则不要停下来反复提问。
可以做合理假设，但要在结果中明确说明。
优先交付可运行代码、基础文档和下一轮可直接执行的提示词。

# 二十六、当前阶段补充约束（飞书企业自建应用静态卡片版）

## 26.1 当前新增目标
在不改变前 5 轮核心闭环的前提下，为项目新增“飞书企业自建应用机器人静态卡片展示入口”。

当前新增主线是：

监控结果  
→ 读取 demo_last_run.json 或最近一次任务结果  
→ 组装飞书静态卡片  
→ 发送到飞书群聊或单聊

这一阶段重点是“展示入口补齐”，不是重做业务主链路。

## 26.2 当前阶段只做静态卡片
由于当前环境没有公网回调地址，本阶段禁止实现以下内容：

- 按钮交互卡片
- 卡片交互回调
- 基于回调的重新跑任务
- 卡片更新回写
- 长连接事件回调消费重构
- 与项目 A 的正式联动

本阶段只允许实现：
- 企业自建应用机器人身份发送消息
- 飞书静态卡片发送
- 群聊发送
- 单聊发送
- 基于 demo_last_run.json 的结果展示

## 26.3 飞书接入边界
当前项目 B 只负责：
- 生成结果
- 生成静态卡片
- 发送静态卡片

当前项目 B 不负责：
- 飞书长连接入口总控
- 多项目共享同一应用的事件路由
- 消息事件分发
- 按钮交互回调分发

长期方案中，项目 A 预留为飞书统一入口层，项目 B 预留为业务服务层；
但当前阶段不要提前实现 A/B 对接。

## 26.4 当前推荐数据源
静态卡片优先使用以下数据源，优先级如下：

1. data/demo_last_run.json
2. 最近一次任务结果（数据库 / API）
3. 仅在前两者不可用时，才直接拼装运行结果

默认优先使用 demo_last_run.json，理由：
- 结果稳定
- 便于演示
- 不依赖临时数据库查询
- 适合离线展示兜底

## 26.5 飞书卡片展示范围
当前静态卡片只展示以下内容：

- 本次运行时间
- baseline 结果摘要
- changed 结果摘要
- 每个商品的：
  - product_name
  - summary
  - priority
  - suggested_action

当前阶段禁止把过多技术字段直接暴露到卡片：
- 不展示原始数据库主键
- 不展示内部错误堆栈
- 不展示调试日志
- 不展示无关配置项

## 26.6 当前发送目标
当前必须支持两种发送目标：

1. 群聊发送
   - 基于 chat_id

2. 单聊发送
   - 基于 open_id 或当前项目可用的用户标识

默认优先先实现群聊发送，再补单聊发送。

## 26.7 当前环境变量要求
新增飞书相关配置时，统一使用以下字段名：

- FEISHU_APP_ID
- FEISHU_APP_SECRET
- FEISHU_ENABLE_APP_BOT
- FEISHU_DEFAULT_CHAT_ID
- FEISHU_DEFAULT_OPEN_ID
- FEISHU_USE_DEMO_LAST_RUN
- FEISHU_ENABLE_SEND

除非我明确要求，否则不要自行发明新的配置命名风格。

## 26.8 当前阶段禁止事项
请不要做以下事情：

1. 不要把当前静态卡片版直接扩成按钮交互版
2. 不要要求我先提供公网回调地址
3. 不要擅自接入项目 A
4. 不要改动前 5 轮已通过的主链路
5. 不要把 notifier 全量替换成飞书应用机器人，应该采用增量方式支持新发送模式
6. 不要跳过 demo_last_run.json，重复造一套结果固化逻辑
7. 不要为了飞书接入重构数据库
8. 不要引入 Redis/Celery/Postgres/消息队列

## 26.9 当前阶段推荐实现方式
当前推荐做法：

1. 新增飞书应用机器人发送服务
2. 先打通“发送测试文本消息”
3. 再打通“发送静态卡片”
4. 先做群聊
5. 再做单聊
6. 保留 dry-run / mock 模式，避免飞书配置不完整时阻断本地开发

## 26.10 当前阶段最低验收标准
完成后至少应满足：

1. 可使用企业自建应用机器人成功发送一条测试消息
2. 可成功发送一张静态卡片到飞书群聊
3. 可成功发送一张静态卡片到飞书单聊
4. 卡片内容来自 demo_last_run.json 或等价最近结果
5. README 已补充飞书静态卡片接入说明
6. 不影响前 5 轮既有功能

## 26.11 本阶段后的下一阶段预留
下一阶段才考虑：

- 按钮交互卡片
- 卡片回调
- 项目 A 作为统一飞书入口层
- 项目 B 作为业务服务层
- A/B 对接

# 二十七、P6 阶段补充约束（多源采集轻量升级版）

## 27.1 当前阶段名称
P6：项目 B 多源采集轻量升级

## 27.2 当前阶段目标
在不破坏前 1-6 轮已通过能力的前提下，为项目 B 增加：

1. 轻量发现层（SearXNG）
2. 轻量静态采集层（Scrapy）
3. 与现有主链路兼容的统一数据契约

当前阶段目标不是把项目重做成完整采集平台，而是完成：

- 可讲清楚
- 可演示
- 可扩展
- 不破坏现有闭环

的轻量升级。

---

## 27.3 当前阶段必须保持不变的能力
以下能力已经通过验收，当前阶段不得破坏：

1. mock 页面演示链路
2. Playwright 采集与截图
3. snapshot / diff / analyzer 主链路
4. demo_last_run.json 固化结果
5. run_demo_flow.py 一键演示
6. smoke_api.py 自检
7. 飞书企业自建应用静态卡片：
   - 群聊文本发送
   - 群聊静态卡片发送
   - 单聊文本发送
   - 单聊静态卡片发送

除非我明确要求，否则不得重构这些已通过能力。

---

## 27.4 当前阶段的定位
这一阶段是“轻量接入版”，不是“平台重构版”。

所以当前只允许：

- 增加 discovery 能力
- 增加 scrapy 静态采集能力
- 增加 source abstraction
- 把新结果统一进现有契约

当前不允许：

- 推翻原有结构
- 重写原 notifier / analyzer / snapshot 主链路
- 把 B 改造成大而全爬虫平台
- 把 discovery 变成主演示入口

---

## 27.5 当前阶段的分层职责

### A. 发现层（SearXNG）
职责：
- 输入 query
- 输出候选 seed URLs
- 提供最小去重与过滤

不负责：
- 正文抓取
- 页面字段提取
- 页面动作
- 业务分析
- diff

### B. 静态采集层（Scrapy）
职责：
- 采集 1 类静态页面
- 提取结构化字段
- 输出统一字段结构

不负责：
- 动态点击
- 截图留痕
- 复杂页面交互
- analyzer
- 飞书发送

### C. 动态采集层（Playwright）
职责保持不变：
- mock 页面
- 截图
- 现有稳定演示主链路
- 动态页补位

### D. 后处理层
继续沿用现有能力：
- normalizer
- snapshot
- diff
- analyzer
- demo 固化
- 飞书展示

当前阶段不要重复发明第二套后处理流程。

---

## 27.6 当前阶段核心原则

### 原则 1：SearXNG 只是发现层，不是主演示入口
当前 discovery 只能作为：
- 辅助搜索能力
- seed URL 发现能力
- 架构补齐能力

禁止让 discovery 成为：
- 当前 demo 唯一入口
- 当前面试演示主路径
- 当前飞书展示主依赖

原因：
搜索结果有波动，会降低演示稳定性。

### 原则 2：Scrapy 不替代 Playwright
Scrapy 与 Playwright 必须分工清晰：

- Scrapy：静态页、稳定页、轻量批量采集
- Playwright：mock、动态页、截图、演示稳定链路

禁止将当前 Playwright 主链路直接替换成 Scrapy。

### 原则 3：统一数据契约比接工具更重要
当前阶段最重要的不是“接上 SearXNG / Scrapy”本身，
而是它们的输出能否统一进入现有结构。

必须优先保证：
- 字段统一
- 结构统一
- 后处理统一

### 原则 4：保持现有演示稳定
任何新增能力都不能影响以下现有脚本的正常使用：

- scripts/run_demo_flow.py
- scripts/send_demo_static_card.py
- scripts/send_app_bot_test_text.py
- scripts/smoke_api.py
- scripts/check_demo_ready.py

---

## 27.7 当前阶段必须实现的能力

### 27.7.1 discovery 最小能力
至少应实现：

1. 可配置 SearXNG base URL
2. 可输入 query
3. 可返回候选 URL 列表
4. 可设置 limit
5. 可做最小去重
6. 可做最小域名过滤

建议输出字段：
- title
- url
- domain
- snippet
- rank

### 27.7.2 scrapy 最小能力
至少应实现：

1. 建立最小 Scrapy 运行能力
2. 至少支持 1 类静态页面采集
3. 输出统一字段
4. 能单独 demo 运行
5. 能进入 snapshot / diff 主链路

### 27.7.3 source abstraction 最小能力
必须让系统内部能识别至少三类 source：

- mock_playwright
- static_scrapy
- discovery_then_scrapy

但当前阶段不要求做很复杂的插件系统或注册中心。

---

## 27.8 当前阶段新增目录与文件约束

建议在现有项目中新增以下结构，保持语义一致：

```text
app/
├─ services/
│  ├─ discovery.py
│  ├─ scrapy_runner.py
│  ├─ scrape_dispatcher.py
│  └─ source_router.py
├─ scrapers/
│  └─ scrapy_project/
│     ├─ spiders/
│     │  └─ product_spider.py
│     ├─ items.py
│     └─ settings.py
scripts/
├─ run_discovery_demo.py
├─ run_scrapy_demo.py
└─ run_multi_source_demo.py
docs/
└─ p6-multi-source-plan.md
如果因实现方式需要微调目录，可以调整，但必须保持：

发现层
采集层
路由/分发层
demo 脚本

四类结构清晰分离。

27.9 数据结构与统一契约要求
27.9.1 统一采集输出结构

无论来源于：

Playwright
Scrapy
Discovery + Scrapy

最终都必须统一为同类结构，例如：

{
  "product_name": "Example Product",
  "product_url": "https://example.com/product/1",
  "price": 199.0,
  "stock_status": "in_stock",
  "promotion_text": "Flash Sale",
  "collected_at": "2026-04-22T12:00:00",
  "screenshot_path": null,
  "source_type": "scrapy"
}
27.9.2 当前必须新增 source_type

当前阶段新增来源标记字段：

mock_playwright
static_scrapy
discovery_then_scrapy

后续 snapshot / report / demo 中允许带出该字段，但不要让它污染飞书卡片展示主内容。

27.9.3 当前 screenshot_path 允许为空

Scrapy 结果默认允许：

screenshot_path = null

不要为了和 Playwright 完全一致，强行给 Scrapy 生成伪截图。

27.10 discovery 实现约束
必须做到
配置项集中管理，不要把 SearXNG 地址写死在代码里
HTTP 请求失败时要有清晰错误信息
支持 limit 参数
支持基础去重
支持 allowed_domains 过滤（可选参数）
不要做
不要做复杂搜索排序优化
不要做多轮搜索重写
不要做 AI query expansion
不要做复杂召回评估
不要把 discovery 结果直接当成最终业务结果
27.11 scrapy 实现约束
必须做到
只先支持 1 类静态页面
只提取最小字段：
product_name
product_url
price
stock_status
promotion_text
collected_at
可独立运行 demo
可被当前业务主链复用
不要做
不要接入 scrapy-playwright
不要做多 spider 多站点大规模适配
不要做复杂 pipeline 平台化
不要引入分布式调度
不要急着做大规模批量抓取
当前阶段推荐

如果 Scrapy 原生项目管理过重，可以做最小化封装，但不要失去“这是 Scrapy 采集层”的语义。

27.12 source router / dispatcher 约束
必须有一个明确入口

新增 source 后，必须有一个明确的采集分发层，例如：

source_router.py
scrape_dispatcher.py

其职责是：

根据 source_type 决定走哪条链路
不承担具体采集细节
不承担 analyzer 和 notifier 逻辑
不允许
把所有 source 逻辑都塞进 monitor_runner.py
把 discovery / scrapy / playwright 判断写成一长串 if-else 散落在多个文件里
27.13 与现有主链路兼容约束
monitor_runner

当前 monitor_runner 可以增量支持新 source，但必须满足：

老的 mock + Playwright 逻辑仍正常
新的 Scrapy 结果也能进入：
normalizer
snapshot
diff
analyzer
错误分类统计仍然保留：
collector_errors_count
analyzer_errors_count
notifier_errors_count
successful_products_count
analyzer

当前 analyzer 不需要因为 discovery / scrapy 接入而重写。

notifier / 飞书

当前飞书发送能力不应被 discovery / scrapy 接入影响。

27.14 当前阶段新增配置项约束

如需新增配置项，请统一放在 app/core/config.py，并同步更新 .env.example。

建议新增的配置项命名风格如下：

SEARXNG_BASE_URL
SEARXNG_TIMEOUT
SEARXNG_DEFAULT_LIMIT
SEARXNG_ALLOWED_DOMAINS
ENABLE_DISCOVERY
ENABLE_SCRAPY
SCRAPY_DEFAULT_SOURCE
SCRAPY_FIXTURE_DIR

要求：

命名统一
不要随意混用大写和小写风格
不要把真实环境值写进 .env.example
真实敏感配置只允许放本地 .env
27.15 文档要求

本阶段必须补齐以下文档：

README.md

新增说明：

discovery 能力做什么
scrapy 能力做什么
discovery / scrapy / playwright 的分工
如何运行：
run_discovery_demo.py
run_scrapy_demo.py
run_multi_source_demo.py
当前阶段不做什么
docs/architecture.md

补充：

discovery / scrapy / playwright 三层结构
为什么 discovery 不是主演示入口
为什么 scrapy 不替代 playwright
为什么当前只做轻量接入
docs/p6-multi-source-plan.md

本阶段新增计划与约束文档，内容应与本节保持一致，不允许跑偏。

27.16 测试与验收要求
必须保留现有测试

现有测试不能因本阶段接入失败。

当前阶段建议新增的最小测试

如时间允许，可增加：

discovery 结果去重测试
source_router 分发测试
scrapy 输出 normalizer 兼容测试
当前阶段最低验收标准

必须满足：

SearXNG 可返回候选 URLs
Scrapy 至少可完成 1 类静态页面采集
Scrapy 输出可进入现有 snapshot 结构
Scrapy 结果可触发 diff / analyzer
mock + Playwright 原链路不受影响
飞书静态卡片原能力不受影响
README 已补充多源采集说明
27.17 当前阶段禁止事项

请不要做以下事情：

不要把 discovery 变成主演示入口
不要移除 mock 页面
不要移除 Playwright 主演示链路
不要直接引入 scrapy-playwright
不要接入 Crawl4AI
不要接入 changedetection.io
不要引入 Redis/Celery/Postgres
不要做分布式爬虫平台
不要重构 notifier / 飞书发送能力
不要开始做 A/B 对接
不要做交互卡片和回调
不要为了 discovery / scrapy 接入而重做数据库模型
不要写大量当前用不到的插件抽象
27.18 当前阶段默认开发顺序

如果我没有额外指定，本阶段默认按以下顺序推进：

第一轮
discovery 最小接入
run_discovery_demo.py
最小 URL 去重与过滤
第二轮
scrapy 最小接入
run_scrapy_demo.py
输出统一字段结构
第三轮
接入现有 snapshot / diff / analyzer 链路
source_router / scrape_dispatcher
run_multi_source_demo.py
第四轮
README / architecture / p6 文档
最小回归验证
确保飞书展示不受影响
27.19 每轮汇报格式继续沿用

每轮完成后，仍必须严格按以下格式汇报：

A. 本轮做了什么
B. 为什么这样改
C. 现在怎么运行
D. 当前还缺什么
E. 下一轮建议
F. 下一步可直接执行的提示词

不得省略 F。

27.20 当前阶段成功标准

如果本阶段成功，应满足以下结果：

项目 B 已从单一采集源升级为多源采集轻量版本
discovery 能力存在但不破坏演示稳定性
scrapy 能力存在且能进入现有业务链
Playwright 主链仍是当前最稳定演示链路
飞书展示入口仍可正常使用
项目整体更接近后续 A/B 对接的业务服务形态
27.21 给 coding agent 的当前阶段最后指令

从现在开始，本项目进入 P6：多源采集轻量升级阶段。

你的任务不是重构平台，而是在最少轮次内完成：

discovery 最小接入
scrapy 最小接入
统一数据契约接入
保持现有闭环与飞书展示能力不被破坏

请优先保证：

现有能力不退化
新能力可演示
结构清晰
文档可讲清楚

# 二十八、P7 阶段补充约束（老板需求补足层）

## 28.1 当前阶段名称
P7：老板需求补足层

## 28.2 当前阶段目标
在不进行 A/B 对接的前提下，把项目 B 从“技术闭环 Demo”进一步整理成“老板需求型业务服务层”。

当前阶段重点是补足以下 5 类老板需求：

1. 发现商品
2. 加入监控
3. 查看今日变化摘要
4. 查看商品详情
5. 管理监控对象

---

## 28.3 当前阶段必须保持不变的能力
以下能力已通过验收，当前阶段不得破坏：

1. mock + Playwright 演示链路
2. snapshot / diff / analyzer 主链路
3. demo_last_run.json
4. run_demo_flow.py
5. smoke_api.py
6. 飞书静态卡片发送（群聊 / 单聊）
7. P6 discovery / scrapy / source_router / bridge demo 能力

除非我明确要求，否则不得重构这些已通过能力。

---

## 28.4 当前阶段定位
本阶段是“产品语义补足层”，不是“飞书入口层对接阶段”。

所以本阶段只允许：

- 增加老板需求型业务对象
- 增加老板需求型业务接口
- 增加候选池、监控对象、摘要、详情能力
- 整理面向 A 的业务服务边界

本阶段不允许：

- 进入 A/B 对接
- 做飞书消息编排
- 做卡片按钮交互
- 做公网回调
- 做共享数据库

---

## 28.5 当前阶段核心原则

### 原则 1：候选池与正式监控对象必须分开
discovery 结果不能直接当正式监控对象。

必须有清晰区分：
- candidate batch / candidate items
- monitor target / formal product target

### 原则 2：先做产品动作，不做入口动作
当前阶段只做 B 的“业务服务能力”。
不要提前做 A 的飞书入口逻辑。

### 原则 3：老板需求优先于技术命名
新接口、新服务、新文档命名和语义应尽量贴近：
- search
- add monitor
- summary
- detail
- manage targets

而不是继续偏：
- test
- demo
- raw pipeline
- experimental bridge

### 原则 4：保持已有主链路不退化
P7 过程中不得影响：
- run_demo_flow
- smoke_api
- send_demo_static_card
- 多源采集 P6

---

## 28.6 当前阶段必须实现的业务能力

### 28.6.1 发现商品能力
至少应支持：
- 根据 query 发起 discovery
- 生成 candidate batch
- 保存 candidate items
- 查询某一批候选结果

### 28.6.2 加入监控能力
至少应支持：
- 从候选项加入监控
- 从 URL 直接加入监控
- 建立 baseline
- 返回正式加入监控结果

### 28.6.3 今日摘要能力
至少应支持：
- 今日监控商品数
- 今日变化商品数
- 高优先级数
- Top 商品摘要
- 建议动作摘要

### 28.6.4 商品详情能力
至少应支持：
- 商品基础信息
- 最近变化
- 最近报告
- 详情摘要

### 28.6.5 监控对象管理能力
至少应支持：
- 列表
- 暂停
- 恢复
- 删除

---

## 28.7 当前阶段建议新增对象

建议新增以下对象语义：

### candidate_batches
记录一次 discovery 查询批次

### candidate_items
记录候选项

### monitor_targets
记录正式监控对象

如果复用已有表，也必须通过命名、文档或 service 语义清楚区分这些角色。

---

## 28.8 当前阶段接口约束

### discovery 相关接口
- `POST /internal/discovery/search`
- `GET /internal/discovery/batches/{batch_id}`

### 加入监控相关接口
- `POST /internal/monitor/add-from-candidates`
- `POST /internal/monitor/add-by-url`

### 监控对象管理接口
- `GET /internal/monitor/targets`
- `POST /internal/monitor/{id}/pause`
- `POST /internal/monitor/{id}/resume`
- `DELETE /internal/monitor/{id}`

### 老板摘要与详情接口
- `GET /internal/summary/today`
- `GET /internal/products/{id}/detail`
- `GET /internal/reports/latest`

如果已有近似接口，可以增量整理，但必须让语义更稳定、更像产品接口。

---

## 28.9 当前阶段新增服务约束

建议增加清晰的服务层，例如：

- `discovery_business_service`
- `monitor_target_service`
- `summary_service`
- `product_detail_service`

要求：
1. service 职责单一
2. 不要把大量业务逻辑堆在 route 里
3. 不要把 A 的会话逻辑提前写进 B

---

## 28.10 当前阶段文档要求

必须补齐：

### README.md
新增：
- P7 老板需求补足层说明
- 当前 B 支持的老板需求型接口
- 当前仍不做 A/B 对接

### docs/p7-boss-needs-plan.md
新增：
- P7 阶段目标
- 当前业务动作
- 当前范围边界
- 下一阶段预留

### docs/architecture.md
补充：
- 候选池 -> 监控对象 -> 摘要/详情 的关系
- B 在未来 A/B 结构中的角色

---

## 28.11 当前阶段不要做的内容

请严格不要做：

1. 不要开始 A/B 对接
2. 不要开始飞书消息入口改造
3. 不要开始按钮交互卡片
4. 不要做公网回调
5. 不要做共享数据库
6. 不要引入 Redis/Celery/Postgres
7. 不要重构前 1-6 轮主链路
8. 不要把 discovery 结果直接写成正式监控对象
9. 不要为了 P7 重做 P6 多源采集结构
10. 不要开始复杂权限系统

---

## 28.12 当前阶段默认开发顺序

如果我没有额外指定，本阶段默认按以下顺序推进：

### 第一轮
- 候选池能力
- discovery search -> candidate batch
- 查询候选批次

### 第二轮
- 从候选项加入监控
- 从 URL 加入监控
- baseline 建立

### 第三轮
- 今日摘要能力
- 商品详情能力

### 第四轮
- 监控对象管理能力
- 文档补齐
- 回归检查

---

## 28.13 当前阶段最低验收标准

必须满足：

1. 可生成 candidate batch
2. 可查询 candidate batch
3. 可从候选项加入监控
4. 可从 URL 加入监控
5. 可返回今日摘要
6. 可返回商品详情
7. 可管理监控对象
8. 现有 run_demo_flow / smoke_api / 飞书静态卡片 / P6 能力不退化

---

## 28.14 每轮汇报格式继续沿用

每轮完成后，仍必须严格按以下格式汇报：

### A. 本轮做了什么
### B. 为什么这样改
### C. 现在怎么运行
### D. 当前还缺什么
### E. 下一轮建议
### F. 下一步可直接执行的提示词

不得省略 F。

---

## 28.15 当前阶段成功标准
如果 P7 成功，应满足以下结果：

1. B 不再只是技术 Demo
2. B 已具备老板需求型业务能力
3. 后续 A 只需做飞书入口和交互编排
4. A 不需要了解 B 的底层采集细节
5. 项目整体更接近真正的企业内应用结构

---

## 28.16 给 coding agent 的当前阶段最后指令
从现在开始，本项目进入 P7：老板需求补足层。

你的任务不是继续堆底层能力，也不是开始 A/B 对接，而是在最少轮次内完成：

- 候选池
- 加入监控
- 今日摘要
- 商品详情
- 监控对象管理

请优先保证：
1. 产品语义清晰
2. 业务动作可演示
3. 现有主链路不退化
4. 文档能讲清楚