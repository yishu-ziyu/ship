"""yishuship PM benchmark rollout.

运行 target model 通过 PM 阶段，用 pm_scorer 评分。
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from skillopt.model import chat_target

# 把 yishuship benchmarks 目录加到 path，导入 pm_scorer
_BENCH_DIR = Path(__file__).resolve().parents[4] / "benchmarks"
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))


def _build_prompt(item: dict, skill_content: str) -> tuple[str, str]:
    """构建 system + user prompt。"""
    system = skill_content
    user = (
        f"## 产品场景\n\n{item['scenario']}\n\n"
        f"## 背景信息\n\n{item.get('context', '无额外上下文。')}\n\n"
        f"## 任务\n\n"
        f"请为这个场景完成 **{item['stage']}** 阶段的产出。\n"
        f"严格遵循 skill 文档中的模板格式和退出标准。\n"
    )
    return system, user


def _score(output: str, item: dict) -> tuple[int, float]:
    """用 pm_scorer 评分，返回 (hard, soft)。

    hard: 是否通过合格线 (0/1)
    soft: 归一化得分 (0.0-1.0)
    """
    try:
        # 尝试导入 pm_scorer
        from pm_scorer import score_stage
    except ImportError:
        # fallback: 用关键词匹配
        keywords = item.get("ground_truth_keywords", [])
        if not keywords:
            return 0, 0.0
        hits = sum(1 for kw in keywords if kw.lower() in output.lower())
        soft = hits / len(keywords)
        return int(soft >= 0.6), soft

    stage = item.get("stage", "discover")
    # 映射 stage 名到 pm_scorer 的 key
    stage_map = {
        "发现": "discover", "discover": "discover",
        "定义": "define", "define": "define",
        "设计": "design", "design": "design",
        "验证": "validate", "validate": "validate",
        "实现": "build", "build": "build",
        "发布": "release", "release": "release",
        "观察": "observe", "observe": "observe",
        "学习": "learn", "learn": "learn",
    }
    scorer_key = stage_map.get(stage, stage)

    try:
        result = score_stage(scorer_key, output)
        total = result["total"]
        max_score = result["max"]
        passed = result["passOrFail"]
        soft = total / max_score if max_score > 0 else 0.0
        return int(passed), soft
    except Exception:
        return 0, 0.0


def _rollout_one(item: dict, skill_content: str,
                 *, max_completion_tokens: int) -> dict:
    system, user = _build_prompt(item, skill_content)
    prediction, _usage = chat_target(
        system=system,
        user=user,
        max_completion_tokens=max_completion_tokens,
    )
    hard, soft = _score(prediction, item)
    return {
        "id": str(item["id"]),
        "hard": hard,
        "soft": soft,
        "predicted_output": prediction,
        "scenario": item.get("scenario", ""),
        "stage": item.get("stage", "discover"),
        "task_type": item.get("task_type", "discover"),
    }


def run_batch(*, items: list[dict], skill_content: str, out_root: str,
              workers: int = 4, max_completion_tokens: int = 4096) -> list[dict]:
    os.makedirs(out_root, exist_ok=True)
    results = [
        _rollout_one(item, skill_content,
                     max_completion_tokens=max_completion_tokens)
        for item in items
    ]
    Path(out_root, "rollouts.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2)
    )
    return results
