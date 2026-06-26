# DEC-0001: yishuship 采用「单一插件 + 多 skill + 路由脑」架构

> 日期: 2026-06-26
> 任务: 20260626-044005
> 阶段: 架构选型
> 评分: 15/15（arch-decision stage 满分）
> 状态: 已接受

## 背景

yishuship 是 Claude Code 插件，给非工程师 + 工程师混合用户提供"产品 PM 全流程 → 工程实现"一体化能力。需要决定 PM 层与工程层怎么拆。

## 决策

**单一 Claude Code 插件 + 13 skill + 路由脑（use-yishuship）**

- 1 个 plugin 仓 `~/Developer/yishuship/`
- 13 个 skill 通过 `use-yishuship` 路由脑按需加载
- 4 个 hook 在 plugin 粒度注册
- 状态 `.ship/tasks/<task_id>/` 在同 plugin 内共享

## 候选方案

### 候选 A：单一插件 + 多 skill（已选）

1 个仓、13 skill、路由脑、4 hook。装一次能用全部能力，PM 评分独立。

### 候选 B：多插件 + sub-agent 调度

拆 4-5 个独立 plugin，按需 `install`。**拒绝理由**：非工程师用户要在多个 plugin 之间切换、PM 训练数据需跨 plugin 归一化。

### 候选 C：极简拆分（PM 内嵌）

删 pm-intake 独立 skill，PM 流程嵌入路由脑。**拒绝理由**：PM 流程不能独立评分 → SkillOpt 训练循环无法运行 → 失去 63 维度评分这一最大差异化。

## 决策依据

1. **用户技术栈差异**：工程师 + 非工程师 PM 共享同一 `yishuship:` 命令空间，避免非工程师用户在多 plugin 间切换
2. **PM 阶段独立优化是核心壁垒**：63 维度评分 + SkillOpt 训练循环是跟原版 Ship 的唯一差异化
3. **跨 skill 状态共享**：`.ship/tasks/<task_id>/` 在同 plugin 内天然共享
4. **状态机一致性**：hook 按 plugin 粒度注册，拆插件后边界要重画

## 架构指纹 → 因果链

| 指纹 | 影响 |
|------|------|
| 形态 = 跨平台插件 | 候选池收敛到 A/B/C |
| 团队 = 单人开发 + 公开用户 | 排除微服务/独立部署 |
| 用户技术栈 = 工程师+非工程师混合 | 倾向 A（统一命令空间）|
| 部署 = 本地 + 跨平台 | 排除 Serverless/云端 |

## 约束（对后续阶段）

- Step 2 定义必须把"不做多插件拆分"列入 Non-goals
- Step 3 设计技术方案必须基于「Plugin 规范 + Skill + Hook + Script」四件套
- Step 4 验证必须包含"Claude Code 插件规范 1-2 年内不变"这一架构假设
- Plan B：若 plugin 规范大改，yishuship 可降级为「Skill 集合 + 手动调用」，不依赖 marketplace.json

## 重新评估条件

- Claude Code 官方宣布 plugin 规范废弃 → 立刻重评
- 13 skill 增到 25+、单 plugin > 50MB → 重评候选 B 局部重启
- SkillOpt 训练循环证明对 PM 评分无增益 → 考虑候选 C

## 关联

- 任务: `.ship/tasks/20260626-044005/`
- 完整决策过程: `.ship/tasks/20260626-044005/pm/01.5-architecture-decision.md`
- 上下文: `.ship/tasks/20260626-044005/pm/01-discovery.md`
