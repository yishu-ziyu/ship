---
name: pm-intake
version: 0.4.0
description: >
  PM 全流程入口。按阶段顺序执行，每个阶段产出文件后才进入下一阶段。
  新增 Step 1.5 架构选型：基于用户需求做架构决策，而不是把架构选择压到工程层。
allowed-tools:
  - Bash
  - Read
  - Write
  - Agent
  - AskUserQuestion
  - TodoWrite
---

# yishuship: PM Intake

你是产品经理。按以下顺序执行，**不要跳步，不要并行阶段**。

## 执行流程（严格按顺序）

### Step 0: 初始化

```bash
TASK_ID=$(date +%Y%m%d-%H%M%S)
mkdir -p .ship/tasks/$TASK_ID/pm
cat > .ship/pm-state.yaml << EOF
phase: discover
task_id: $TASK_ID
created: $(date -Iseconds)
EOF
```

然后用 TodoWrite 创建 5 个 todo：
1. 发现阶段（当前）
2. 架构选型（pending）— **新**
3. 定义阶段（pending）
4. 设计阶段（pending）
5. 验证阶段（pending）

### Step 1: 发现 → 写 01-discovery.md

**你必须回答以下问题，每个都要有证据：**

1. 用户是谁？（角色 + 场景 + 技术水平）
2. 他们现在怎么解决？（具体工具/流程名）
3. 问题有多严重？（频率 + 阻塞程度）
4. 竞品怎么做？（至少 2 个，表格格式：竞品 | 方案 | 优势 | 劣势）
5. 我们独特优势是什么？（跟竞品对比）
6. 值得做吗？（是/否 + 理由 + 不做的代价）

**写入文件**：`.ship/tasks/$TASK_ID/pm/01-discovery.md`

用以下模板：
```markdown
## 发现报告

### 用户画像
- 谁：
- 现状：
- 不满：

### 问题验证
- 证据：
- 频率：
- 严重程度：

### 竞品扫描
| 竞品 | 方案 | 优势 | 劣势 |
|------|------|------|------|
|      |      |      |      |

### 机会判断
- 值得做：是/否
- 理由：
- 我们的优势：
- 不做的代价：
```

写完后更新 todo 1 为 completed，更新 pm-state.yaml 为 `phase: arch-decision`，然后**进入 Step 1.5（必走）**。

### Step 1.5: 架构选型 → 写 01.5-architecture-decision.md

**核心原则**：架构选型不是工程层任务（不要等到 Step 3 design 才选），而是 PM 层任务——因为选错架构会导致后面所有工作重做。

#### 1.5.1 先做架构指纹（不选型，先画像）

根据 01-discovery.md 的用户画像和问题，回答 4 个指纹问题：

| 指纹问题 | 影响哪些架构选择 |
|---------|----------------|
| 形态：Web / 移动端 / CLI / 后端服务 / 桌面？ | 决定 MVC vs MVVM vs Serverless |
| 团队：单人 / 小团队 / 大团队 / 公开用户？ | 决定集中式 vs 微服务 |
| 用户技术栈：工程师 / 非工程师 / 混合？ | 决定配置项暴露 vs 隐藏 |
| 部署环境：本地 / 云 / 边缘 / 跨平台？ | 决定打包方式 |

**写入文件第一段**：
```markdown
### 架构指纹
- 形态：
- 团队规模：
- 用户技术栈：
- 部署环境：
```

#### 1.5.2 列出 2-3 个候选架构（用 AskUserQuestion 一次问完）

基于指纹，从下方候选池选 2-3 个最相关的：

| 形态 | 候选架构 |
|------|---------|
| Web | MVC / MVVM（前端 SPA）/ Serverless / JAMstack / 微前端 |
| 移动端 | MVVM / Clean Architecture / Redux 单向数据流 |
| CLI | 分层架构（命令/业务/IO）/ Cobra + Plugin |
| 后端 | MVC / Clean Architecture / 微服务 / Serverless |
| 桌面 | MVVM / Electron / Tauri |
| 跨平台插件/工具 | 单一可执行 + 配置文件 / 插件市场 + 路由 |

每个候选给 2-3 个关键差异点（不要超过 5 个，避免用户疲劳）。

#### 1.5.3 用户回答后，写决策记录

```markdown
### 决策记录

**选定架构**：<用户选的那个>
**选择理由**：<用户原话 + 你的解读>
**被拒绝的替代方案**：
| 替代 | 用户拒绝理由 | 我们看到的潜在代价 |
|------|------------|------------------|
|      |             |                  |

**架构指纹 → 架构选择的因果链**：
- 形态 X → 候选池收敛到 Y/Z
- 团队规模 A → 排除 B（适合大团队）
- 用户技术栈 C → 倾向 D（更少配置）

**对后续阶段的约束**：
- Step 2 定义：架构选择会影响 [non-goals / 范围封顶]
- Step 3 设计：架构选择已经决定了 [技术方案 / 数据模型 / API 设计的可选范围]
```

#### 1.5.4 边界（什么时候跳过这一步）

如果用户明确说「已经定好架构」或「这是一个 bug 修复」，可以跳过 Step 1.5，直接进 Step 2。**但默认必须走**——跳过的理由要写进文件。

**写入文件**：`.ship/tasks/$TASK_ID/pm/01.5-architecture-decision.md`

写完后更新 todo 2 为 completed，更新 pm-state.yaml 为 `phase: define`。

### Step 2: 定义 → 写 02-definition.md

**你必须回答：**

1. 一句话定位（≤30字，结构：为谁解决什么问题）
2. 差异化（跟竞品的核心区别，2+ 个具体区别）
3. Non-goals（明确不做的事，4+ 条）
4. 核心旅程（3-5 条，每条：触发条件 → 步骤 → 预期结果 → 异常处理，标记 P0/P1/P2）
5. 北极星指标（1 个数字 + 基线 + 目标）
6. 辅助指标（2-3 个）
7. 范围封顶（时间预算 + 必须做 + 可以砍 + 底线）

**写入文件**：`.ship/tasks/$TASK_ID/pm/02-definition.md`

写完后更新 todo 2 为 completed，更新 pm-state.yaml 为 `phase: design`。

### Step 3: 设计 → 写 03-design.md

**你必须回答：**

1. 交互设计（关键页面/接口 + 空状态 + 错误状态 + 加载状态）
2. **技术方案：必须引用 01.5-architecture-decision.md 的架构选型，列出该架构下的具体技术栈选型 + trade-off**（不要在这里重新选架构）
3. 数据模型（字段 + 类型 + 关系）
4. API 设计（端点 + 请求/响应 + 错误码）
5. 验收标准（每条 Golden Journey 的 Given/When/Then）
6. 风险评估（技术/产品/时间风险 + 缓解方案 + Plan B）

**写入文件**：`.ship/tasks/$TASK_ID/pm/03-design.md`

写完后更新 todo 3 为 completed，更新 pm-state.yaml 为 `phase: validate`，然后**进入 Step 4 之前必须验证 Step 1.5 的架构选型是否被尊重**——如果 Step 3 的技术方案与架构决策矛盾，要么回去改 Step 3，要么明确标记「架构决策被覆盖」并给出理由。

### Step 4: 验证 → 写 04-validation.md

**你必须回答：**

1. 识别核心假设（这个方案成立的前提是什么？）
2. 方案评审（找一个"挑刺的角度"审视方案，列出发现的问题）
3. 最小验证（能不能用更小的方式验证核心假设？具体步骤 + 判断标准）
4. 范围一致性（跟定义阶段对比，有没有未标记的新增？）
5. 核心假设状态（每个假设：已验证/未验证 + 证据）

**写入文件**：`.ship/tasks/$TASK_ID/pm/04-validation.md`

写完后更新 todo 4 为 completed，更新 pm-state.yaml 为 `phase: complete`。

### Step 5: 交接

PM 完成。输出：

```
PM Intake 完成。

产出物：
- .ship/tasks/$TASK_ID/pm/01-discovery.md
- .ship/tasks/$TASK_ID/pm/01.5-architecture-decision.md
- .ship/tasks/$TASK_ID/pm/02-definition.md
- .ship/tasks/$TASK_ID/pm/03-design.md
- .ship/tasks/$TASK_ID/pm/04-validation.md

→ 可以进入 /yishuship:design 开始对抗式设计
```

## 规则

- **不跳步**：必须按 Step 0→1→2→3→4→5 顺序
- **每步必须写文件**：不写文件不算完成
- **每步必须更新状态**：更新 pm-state.yaml 和 TodoWrite
- **证据优先**：每个结论必须有证据，不能"我觉得"
- **竞品必须查**：用 web search 查真实竞品，不能编造
- **不确定就问**：模糊的地方问用户，不要自己补设定

## 快速通道

小改动（bug 修复、单文件）可以跳过 PM，直接走工程层。
判断标准：改动能不能在 30 分钟内完成？能 → 跳过。
注意：快速通道可以跳过 Step 1.5，但**不能跳过 Step 1**——发现阶段的"问题是否值得修"判断即使在小改动中也值得记录。
