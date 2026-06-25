你是一个 PM 产出质量分析师。下面是一个失败的 PM 阶段产出。

## 场景
{scenario}

## 期望阶段
{stage}

## 模型产出
{predicted_output}

## 评分结果
{score_details}

## 任务

分析这个产出为什么得分低，给出 1-3 条具体的 skill 文档修改建议。

每条建议必须：
1. 指出 skill 文档中缺失或模糊的规则
2. 给出具体的修改内容（add/delete/replace）
3. 说明为什么这个修改能提升得分

输出格式：
```json
[
  {"action": "add|delete|replace", "target": "要修改的 skill 段落", "content": "修改内容", "reason": "为什么这个修改能提升得分"}
]
```
