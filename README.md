# yishuship — Ship 增强版

> 在原版 Ship 基础上叠加 PM 能力的 AI 产品开发 harness。
> PM 层回答"做不做"，工程层回答"怎么做"。用 SkillOpt 数据驱动优化 skill 文档。

[开发日志](DEVLOG.md) · [原版 Ship](https://github.com/heliohq/ship) · [SkillOpt](https://github.com/microsoft/SkillOpt)

## 核心架构

```
PM 层（yishuship 新增）
  发现 → 定义 → 设计 → 验证
                          ↓
工程层（原版 Ship）
  对抗式设计 → 实现 → 测试 → QA → 发布
                          ↓
PM 层
  观察 → 学习 → 下一迭代
```

## 与原版 Ship 的区别

| 维度 | 原版 Ship | yishuship |
|------|----------|-----------|
| 定位 | 工程 harness | PM + 工程一体化 |
| 入口 | `/ship:use-ship` | `/yishuship:use-yishuship` |
| 新功能 | 直接进 design | **先走 pm-intake（8 阶段）** |
| 竞品调研 | 无 | pm-intake 内置 |
| 决策记录 | 无 | 自动沉淀 DEC-NNNN |
| 评分框架 | 无 | 63 维度 pm_scorer（189 分满分） |
| 自动优化 | 无 | SkillOpt 训练循环 |
| 设计 | 对抗式 | 同原版 |
| 实现 | host + peer | 同原版 |

## 技能清单

| Skill | 命令 | 说明 |
|-------|------|------|
| 路由脑 | `/yishuship:use-yishuship` | 判断请求走哪条路 |
| PM Intake | `/yishuship:pm-intake` | **新增**：8 阶段 PM 全流程 |
| 评分标准 | `/yishuship:pm-eval` | **新增**：63 维度评分框架 |
| 对抗式设计 | `/yishuship:design` | host + peer 并行调查，diff 辩论 |
| 实现 | `/yishuship:dev` | host 写代码 + peer 交叉验证 |
| E2E 测试 | `/yishuship:e2e` | 验收标准固化为持久化测试 |
| Bug 审查 | `/yishuship:review` | 只找 bug，不评风格 |
| 独立 QA | `/yishuship:qa` | 启动真实应用，探索性测试 |
| 重构 | `/yishuship:refactor` | 四镜头扫描，按风险分类 |
| 发布 | `/yishuship:handoff` | PR + CI fix loop，不绿不停 |
| 全流程 | `/yishuship:auto` | pm-intake → design → dev → e2e → review → qa → handoff |
| 系统设计 | `/yishuship:arch-design` | 架构决策 |
| 视觉设计 | `/yishuship:visual-design` | DESIGN.md 视觉系统 |
| 文档 | `/yishuship:write-docs` | 项目文档生成 |

## SkillOpt 训练

yishuship 的 skill 文档通过 [SkillOpt](https://github.com/microsoft/SkillOpt) 数据驱动优化：

```bash
cd /tmp/skillopt
python scripts/train.py --config configs/yishuship/default.yaml
```

训练循环：rollout（model 用 skill 产出 PM 文档）→ score（pm_scorer 63 维度评分）→ reflect（optimizer 分析低分）→ update（修改 skill）→ gate（验证集提升才接受）

## 安装

```bash
# 在 Claude Code 中：
/plugin install yishuship@local
```

## 核心机制

- **需求在磁盘上**：`.ship/tasks/<task_id>/` 存放所有产物
- **阶段隔离**：reviewer 没看过实现，QA 只看 spec + diff + 运行中的应用
- **对抗式设计**：host + peer 各写 spec，diff 辩论
- **证据分级**：L1（截图/curl）> L2（HTTP 200）> L3（"应该能跑"=FAIL）
- **状态机**：可暂停/恢复，stop-gate 阻止中途退出
- **PM 全流程**：8 阶段 × 63 维度 × 退出标准
- **自动优化**：SkillOpt 训练循环驱动 skill 文档迭代

## License

MIT（原版 Ship 为 MIT）
