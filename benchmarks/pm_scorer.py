"""yishuship PM scorer — deterministic lifecycle scoring for SkillOpt and manual QA.

V2 scoring model:
21 product checkpoints × 3 quality dimensions × 3 points = 189.
"""
from __future__ import annotations

import re

QUALITY_DIMENSIONS = ("presence", "evidence", "actionability")

CHECKPOINT_DEFINITIONS: dict[str, dict[str, object]] = {
    "product_type": {"label": "产品类型判断", "keywords": ["产品类型", "product_type", "C", "B", "hybrid", "skip_rules"]},
    "brd": {"label": "BRD", "keywords": ["BRD", "为什么值得做", "商业价值", "值得做", "不做的代价"]},
    "mrd": {"label": "MRD", "keywords": ["MRD", "市场", "竞品", "竞争", "切换", "目标用户"]},
    "scenario_research": {"label": "业务 / 场景调研", "keywords": ["场景", "业务", "调研", "使用场景", "scenario"]},
    "current_state": {"label": "现状梳理", "keywords": ["现状", "当前", "现在", "已有方案", "替代方案", "current"]},
    "problem_summary": {"label": "问题总结", "keywords": ["问题", "痛点", "严重", "频率", "阻塞", "problem"]},
    "solution_idea": {"label": "解决思路", "keywords": ["解决思路", "方案思路", "solution", "假设", "路径"]},
    "product_solution": {"label": "产品方案", "keywords": ["产品方案", "产品形态", "范围", "功能", "solution"]},
    "product_blueprint": {"label": "产品定位 / 核心流程 / 演进蓝图", "keywords": ["定位", "核心流程", "蓝图", "roadmap", "演进"]},
    "data_model": {"label": "业务数据建模", "keywords": ["数据模型", "对象", "字段", "关系", "data model"]},
    "flow_role": {"label": "流程和角色", "keywords": ["流程", "角色", "handoff", "协作", "workflow"]},
    "interface_design": {"label": "界面设计", "keywords": ["界面", "页面", "screen", "状态", "交互"]},
    "report_design": {"label": "报表设计", "keywords": ["报表", "报告", "看板", "dashboard", "决策"]},
    "tracking": {"label": "数据埋点", "keywords": ["埋点", "事件", "指标", "tracking", "analytics"]},
    "permission": {"label": "权限管理", "keywords": ["权限", "角色", "访问", "permission", "risk"]},
    "prd": {"label": "PRD", "keywords": ["PRD", "需求", "验收", "acceptance", "Given"]},
    "technical_plan": {"label": "技术方案", "keywords": ["技术方案", "架构", "接口", "API", "technical"]},
    "project_management": {"label": "项目管理", "keywords": ["项目计划", "里程碑", "owner", "风险", "milestone"]},
    "delivery": {"label": "研发 / 测试 / 上线", "keywords": ["研发", "测试", "上线", "E2E", "QA", "release"]},
    "operations": {"label": "运营管理", "keywords": ["运营", "发布后", "告警", "监控", "operation"]},
    "iteration_analytics": {"label": "迭代优化 / 数据分析", "keywords": ["迭代", "数据分析", "复盘", "learning", "next iteration"]},
}

CHECKPOINTS: tuple[str, ...] = tuple(CHECKPOINT_DEFINITIONS.keys())

LEGACY_STAGE_CHECKPOINTS: dict[str, tuple[str, ...]] = {
    "discover": ("brd", "mrd", "scenario_research", "current_state", "problem_summary"),
    "arch-decision": ("product_type", "technical_plan"),
    "define": ("solution_idea", "product_solution", "product_blueprint", "tracking"),
    "design": ("data_model", "flow_role", "interface_design", "report_design", "permission", "prd", "technical_plan", "project_management"),
    "validate": ("problem_summary", "solution_idea", "prd"),
    "build": ("delivery",),
    "release": ("delivery", "operations"),
    "observe": ("operations", "iteration_analytics"),
    "learn": ("iteration_analytics",),
}

EVIDENCE_PATTERNS = [
    r"https?://",
    r"来源[:：]",
    r"证据[:：]",
    r"用户.*反馈",
    r"N\s*=\s*\d+",
    r"\d+%",
    r"\d+\s*(人|次|天|周|月)",
    r"竞品|竞争|对比|调研|数据|样本|案例",
]

ACTIONABILITY_PATTERNS = [
    r"Owner|负责人|责任人",
    r"下一步|行动|执行|交付|里程碑",
    r"验收|acceptance|Given.*When.*Then",
    r"风险|缓解|mitigation|Plan\s*B",
    r"必须|应该|需要|shall|must",
]

STRUCTURE_PATTERNS = [r"^#", r"^-\s+", r"^\d+\.", r"^\|.*\|", r"```"]


def _count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL))


def _has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL) for pattern in patterns)


def _clamp_score(value: int | float) -> float:
    return float(max(0, min(3, int(value))))


def _keyword_patterns(checkpoint: str) -> list[str]:
    definition = CHECKPOINT_DEFINITIONS[checkpoint]
    return [re.escape(str(keyword)) for keyword in definition["keywords"]]


def score_presence(checkpoint: str, text: str) -> float:
    """0=absent, 1=mentioned, 2=structured, 3=structured and substantial."""
    stripped = text.strip()
    if not stripped:
        return 0.0

    has_keyword = _has_any(stripped, _keyword_patterns(checkpoint))
    has_structure = _has_any(stripped, STRUCTURE_PATTERNS)
    has_substance = len(stripped) >= 240

    score = 0
    if has_keyword:
        score += 1
    if has_structure:
        score += 1
    if has_substance:
        score += 1
    return _clamp_score(score)


def score_evidence(checkpoint: str, text: str) -> float:
    """0=no support, 1=context only, 2=one evidence class, 3=multiple evidence classes."""
    stripped = text.strip()
    if not stripped:
        return 0.0

    hits = sum(1 for pattern in EVIDENCE_PATTERNS if re.search(pattern, stripped, re.IGNORECASE | re.DOTALL))
    if hits >= 3:
        return 3.0
    if hits >= 1:
        return 2.0
    if re.search(r"因为|所以|基于|context|背景", stripped, re.IGNORECASE):
        return 1.0
    return 0.0


def score_actionability(checkpoint: str, text: str) -> float:
    """0=not actionable, 1=intent, 2=action path, 3=owner/criteria/risk ready."""
    stripped = text.strip()
    if not stripped:
        return 0.0

    hits = sum(1 for pattern in ACTIONABILITY_PATTERNS if re.search(pattern, stripped, re.IGNORECASE | re.DOTALL))
    if hits >= 3:
        return 3.0
    if hits >= 2:
        return 2.0
    if hits >= 1:
        return 1.0
    return 0.0


def score_lifecycle_artifact(checkpoint: str, text: str) -> dict:
    if checkpoint not in CHECKPOINT_DEFINITIONS:
        raise KeyError(f"Unknown lifecycle checkpoint: {checkpoint}")

    presence = score_presence(checkpoint, text)
    evidence = score_evidence(checkpoint, text)
    actionability = score_actionability(checkpoint, text)

    total = presence + evidence + actionability
    return {
        "total": total,
        "max": 9,
        "pass_threshold": 6,
        "passOrFail": total >= 6.0,
        "details": {
            "presence": presence,
            "evidence": evidence,
            "actionability": actionability
        }
    }


def score_lifecycle_pipeline(outputs: dict[str, str]) -> dict:
    results = {}
    total = 0.0
    all_pass = True

    for checkpoint in CHECKPOINTS:
        if checkpoint in outputs:
            result = score_lifecycle_artifact(checkpoint, outputs[checkpoint])
        else:
            result = {
                "total": 0.0,
                "max": 9,
                "pass_threshold": 6,
                "passOrFail": False,
                "details": {
                    "presence": 0.0,
                    "evidence": 0.0,
                    "actionability": 0.0
                }
            }
        results[checkpoint] = result
        total += result["total"]
        all_pass = all_pass and result["passOrFail"]

    return {
        "checkpoints": results,
        "total": total,
        "max": 189,
        "all_pass": all_pass
    }


def _combine_stage_output(stage: str, output: str) -> dict[str, str]:
    checkpoints = LEGACY_STAGE_CHECKPOINTS[stage]
    return {checkpoint: output for checkpoint in checkpoints}


def score_stage(stage: str, output: str) -> dict:
    """Score one legacy stage or one lifecycle checkpoint."""
    if stage in CHECKPOINT_DEFINITIONS:
        return score_lifecycle_artifact(stage, output)

    if stage not in LEGACY_STAGE_CHECKPOINTS:
        raise KeyError(f"Unknown PM stage: {stage}")

    stage_outputs = _combine_stage_output(stage, output)
    checkpoint_results = {checkpoint: score_lifecycle_artifact(checkpoint, text) for checkpoint, text in stage_outputs.items()}
    total = sum(result["total"] for result in checkpoint_results.values())
    max_score = len(checkpoint_results) * 9
    pass_threshold = max(1, len(checkpoint_results) * 6)

    return {
        "total": total,
        "max": float(max_score),
        "pass_threshold": float(pass_threshold),
        "passOrFail": total >= pass_threshold,
        "details": checkpoint_results,
    }


def _looks_like_lifecycle_outputs(outputs: dict[str, str]) -> bool:
    return bool(outputs) and all(key in CHECKPOINT_DEFINITIONS for key in outputs.keys())


def score_full_pipeline(outputs: dict[str, str]) -> dict:
    """Score lifecycle outputs or legacy stage outputs.

    Lifecycle input shape:
        {"product_type": "...", "brd": "...", ...}

    Legacy input shape:
        {"discover": "...", "define": "...", ...}
    """
    if _looks_like_lifecycle_outputs(outputs):
        return score_lifecycle_pipeline(outputs)

    results = {}
    total = 0.0
    max_total = 0.0
    all_pass = True

    for stage, checkpoints in LEGACY_STAGE_CHECKPOINTS.items():
        if stage in outputs:
            result = score_stage(stage, outputs[stage])
        else:
            max_score = len(checkpoints) * 9
            result = {
                "total": 0.0,
                "max": float(max_score),
                "pass_threshold": float(max(1, len(checkpoints) * 6)),
                "passOrFail": False,
                "details": {},
            }
        results[stage] = result
        total += result["total"]
        max_total += result["max"]
        all_pass = all_pass and result["passOrFail"]

    return {
        "stages": results,
        "total": total,
        "max": max_total,
        "all_pass": all_pass,
    }
