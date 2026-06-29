from __future__ import annotations

import unittest

from pm_scorer import (
    CHECKPOINTS,
    CHECKPOINT_DEFINITIONS,
    QUALITY_DIMENSIONS,
    score_full_pipeline,
    score_lifecycle_artifact,
    score_lifecycle_pipeline,
    score_stage,
)


def rich_artifact(checkpoint: str) -> str:
    label = CHECKPOINT_DEFINITIONS[checkpoint]["label"]
    return f"""
# {label}

## Context
This section covers {label} for a real yishuship product task.
Evidence: https://example.com/research/{checkpoint}
User feedback sample: N=12, 7 repeated the same problem.
Competitor comparison: Existing tool A solves part of the workflow but misses the core scenario.

## Decision
Owner: PM
Action: convert this checkpoint into the next product or engineering artifact.
Acceptance criteria:
- Given the artifact exists, When engineering reads it, Then they can identify scope, constraints, and next steps.
- Risk: unclear ownership. Mitigation: assign one owner and one review gate.
"""


class LifecycleScorerTests(unittest.TestCase):
    def test_lifecycle_contract_stays_189_points(self) -> None:
        self.assertEqual(len(CHECKPOINTS), 21)
        self.assertEqual(QUALITY_DIMENSIONS, ("presence", "evidence", "actionability"))

        outputs = {checkpoint: rich_artifact(checkpoint) for checkpoint in CHECKPOINTS}
        result = score_lifecycle_pipeline(outputs)

        self.assertEqual(result["max"], 189)
        self.assertTrue(result["all_pass"])
        self.assertEqual(set(result["checkpoints"].keys()), set(CHECKPOINTS))

    def test_each_checkpoint_scores_three_quality_dimensions(self) -> None:
        result = score_lifecycle_artifact("prd", rich_artifact("prd"))

        self.assertEqual(result["max"], 9)
        self.assertEqual(result["pass_threshold"], 6)
        self.assertTrue(result["passOrFail"])
        self.assertEqual(set(result["details"].keys()), {"presence", "evidence", "actionability"})

    def test_missing_checkpoint_fails_without_reducing_total_max(self) -> None:
        outputs = {checkpoint: rich_artifact(checkpoint) for checkpoint in CHECKPOINTS if checkpoint != "permission"}
        result = score_lifecycle_pipeline(outputs)

        self.assertEqual(result["max"], 189)
        self.assertFalse(result["all_pass"])
        self.assertEqual(result["checkpoints"]["permission"]["total"], 0)
        self.assertFalse(result["checkpoints"]["permission"]["passOrFail"])

    def test_legacy_stage_api_still_works(self) -> None:
        stage_result = score_stage("discover", rich_artifact("scenario_research"))
        self.assertGreater(stage_result["max"], 0)
        self.assertIn("details", stage_result)

        pipeline_result = score_full_pipeline({"discover": rich_artifact("scenario_research")})
        self.assertGreater(pipeline_result["max"], 0)
        self.assertIn("stages", pipeline_result)

    def test_full_pipeline_accepts_lifecycle_outputs(self) -> None:
        outputs = {checkpoint: rich_artifact(checkpoint) for checkpoint in CHECKPOINTS}
        result = score_full_pipeline(outputs)

        self.assertEqual(result["max"], 189)
        self.assertIn("checkpoints", result)
        self.assertTrue(result["all_pass"])


if __name__ == "__main__":
    unittest.main()
