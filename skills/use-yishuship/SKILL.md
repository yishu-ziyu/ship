---
name: use-yishuship
version: 0.2.0
description: >
  yishuship 路由脑：判断请求需要 PM 调研、单个 skill、phase bundle 还是全流程。
  在会话开始、用户说"做个功能"、或意图模糊时使用。
  v0.2.0 新增：架构选型 vs 架构详细设计的入口分流，避免把选型错分到 arch-design。
allowed-tools:
  - Read
  - Bash
  - Agent
  - TodoWrite
  - AskUserQuestion
---

# yishuship: 路由脑

你是一个有产品判断力的超级个体。收到请求后，选择最小有用的路由。

## 路由规则

**第一步：判断是不是新功能/产品方向**

如果请求涉及"加个功能"、"做个特性"、"我想实现"、"要不要做"——
这是产品决策，先走 PM Intake，不直接进工程。

```
新功能 / 产品方向 → /yishuship:pm-intake → /yishuyishuship:design
Bug / 小修复      → /yishuyishuship:review 或直接修
纯技术重构        → /yishuyishuship:design (refactor scope)
不确定           → 问用户："这是新功能还是修复？"
```

## 完整路由表

| 请求 | 路由 | 说明 |
|------|------|------|
| "我想做个功能" / "加个特性" | `/yishuship:pm-intake` → `/yishuyishuship:design` | **先调研再设计** |
| "帮我规划一下" | `/yishuyishuship:design` | 对抗式设计 |
| "实现这个功能" | `/yishuyishuship:design` → `/yishuyishuship:dev` | 设计 + 实现 |
| "实现已有计划" | `/yishuyishuship:dev` | 只做实现 |
| "检查这段代码" | `/yishuyishuship:review` | bug 审查 |
| "测试一下" | `/yishuyishuship:qa` | 独立 QA |
| "加 E2E 测试" | `/yishuyishuship:e2e` | 测试固化 |
| "发布" | `/yishuyishuship:handoff` | PR + CI fix loop |
| "重构这段" | `/yishuyishuship:refactor` | 四镜头扫描 |
| "全量交付" | `/yishuyishuship:auto` | 完整流程 |
| "看看竞品" | `/yishuship:pm-intake` | 调研模式 |
| "做个产品" / "用 X 框架做" | `/yishuship:pm-intake` | **架构选型走 pm-intake Step 1.5** |
| "选个架构" / "用什么架构" | `/yishuship:pm-intake` → Step 1.5 | 架构选型决策（不直接做详细设计）|
| "做个系统设计" / "详细架构设计" | `/yishuship:arch-design` | **已知架构后的详细设计**（选型请走 pm-intake）|
| "写文档" | `/yishuship:write-docs` | 文档生成 |
| "设计视觉系统" | `/yishuship:visual-design` | DESIGN.md |

### 关键路由规则：架构选型 vs 架构详细设计

**架构选型**（"做什么形态、用什么架构"）走 PM 层：
- 触发词：选架构 / 用什么技术栈 / X 还是 Y / 单仓还是多仓
- 路由：`/yishuship:pm-intake` → Step 1.5（架构选型子阶段）
- 产出：`pm/01.5-architecture-decision.md` + 沉淀 `docs/decisions/DEC-NNNN.md`
- 理由：选错架构会导致后面所有工作重做，必须在 PM 层决策

**架构详细设计**（"已经定了 X 架构，现在做详细设计"）走工程层：
- 触发词：详细设计 / 系统设计 / ADRs / API 计划
- 路由：`/yishuship:arch-design`
- 产出：通过 `/yishuship:write-docs` 写 design 文档
- 前提：用户已经知道用什么架构，或上游 pm-intake Step 1.5 已经做完

**意图模糊时**，问用户：「这是要选架构（多个候选挑一个），还是已经定好架构做详细设计？」

不要默认跳过这一步——架构选型属于 PM 层决策，不属于工程层。

## 与原版 Ship 的区别

原版 Ship 是纯工程 harness。yishuship 在它前面加了一层 **PM 能力**：

```
原版 Ship:  需求 → 设计 → 实现 → 测试 → 发布
yishuship:  调研 → 判断 → 决策 → 设计 → 实现 → 测试 → 发布
            ─────────────
            PM 层（新增）
```

PM 层回答"做不做"，工程层回答"怎么做"。两层独立运作，PM 层在上，工程层在下。

## 默认选择

意图模糊时，路由到有界 bundle 而不是全流程：

- "帮我看看" → 先问"看什么？代码？竞品？还是产品方向？"
- "优化一下" → 先问"优化什么？性能？体验？还是代码质量？"
- "修一下" → `/yishuyishuship:review` 找问题，再决定怎么修

## 产出物

所有产出物存放在项目的 `.ship/tasks/<task_id>/` 目录：

```text
.ship/tasks/<task_id>/
  input/requirement.md    ← 原始需求
  pm/research.md          ← PM 调研报告
  pm/decision.md          ← PM 产品决策
  plan/spec.md            ← 对抗式设计 spec
  plan/peer-spec.md       ← peer 独立 spec
  plan/plan.md            ← 可执行计划
  plan/diff-report.md     ← 分歧解决记录
  control/run_state.yaml  ← 状态机
  e2e/report.md           ← E2E 测试报告
  dev-context.md          ← 实现上下文
```

决策沉淀到项目的 `docs/decisions/DEC-NNNN.md`。
