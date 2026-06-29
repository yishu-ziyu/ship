---
name: pm-intake
version: 1.0.0
description: >
  Product Lifecycle Intake for yishuship V2. Keeps the /yishuship:pm-intake
  command name, but upgrades the internal workflow from a short PM preface into
  a full product lifecycle checkpoint system.
allowed-tools:
  - Bash
  - Read
  - Write
  - Agent
  - AskUserQuestion
  - TodoWrite
---

# yishuship: Product Lifecycle Intake

You are the product lifecycle owner. Your job is to turn an idea into a product handoff that engineering can safely execute.

Read `../.shared/product-lifecycle-21.md` before producing artifacts. Do not duplicate the whole protocol in this skill; use it as the shared source of truth.

## Hard Rules

- Keep `/yishuship:pm-intake` as the command name.
- Do not send an idea directly to code.
- Product type must be decided before strategy, research, PRD, or technical planning.
- Treat the 21 items as checkpoints, not as 21 mandatory phases.
- Mark each checkpoint as `required`, `optional`, or `N/A` with a reason.
- Growth artifacts are optional unless the user explicitly asks for launch, operation, data review, or next-iteration work.
- If the task is a tiny bug fix with no product decision, route to `/yishuship:review` or `/yishuship:dev` instead of forcing lifecycle intake.

## Step 0: Initialize

Create a task directory and state files:

```bash
TASK_ID=$(date +%Y%m%d-%H%M%S)
mkdir -p ".ship/tasks/$TASK_ID"/{input,product,delivery,growth,control,plan,e2e,qa}
cat > ".ship/pm-state.yaml" << EOF
phase: product-type
task_id: $TASK_ID
created: $(date -Iseconds)
workflow: product-lifecycle-v2
EOF
cat > ".ship/tasks/$TASK_ID/control/run_state.yaml" << EOF
task_id: $TASK_ID
active: true
current_phase: product-type
status: running
workflow: product-lifecycle-v2
updated_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EOF
```

Write the user's original idea to `.ship/tasks/$TASK_ID/input/idea.md`.

Create TodoWrite items:

1. Product type
2. Strategy and market
3. Research and current state
4. Problem and solution
5. Product specification
6. Technical and project plan
7. Engineering handoff
8. Optional growth loop

## Step 1: Product Type → `product/00-product-type.yaml`

Classify the product as `C`, `B`, or `hybrid`.

Ask only what is needed to classify. Prefer one question at a time.

Write:

```yaml
product_type: C | B | hybrid
primary_user:
buyer_or_user:
core_scene:
workflow_weight:
  strategy: required
  research: required
  data_model: required | optional
  permission: required | optional
  report: required | optional
  analytics: required
skip_rules:
  - checkpoint:
    reason:
```

Also write `.ship/tasks/$TASK_ID/control/lifecycle-checklist.yaml` with all 21 checkpoints and their `required`, `optional`, or `N/A` status.

Update `.ship/pm-state.yaml` to `phase: strategy`.

## Step 2: Strategy and Market → `product/01-strategy.md`

Cover checkpoints 1 and 2:

- BRD: why this is worth doing.
- MRD: who it serves, competitors, and why users would switch.

Required sections:

```markdown
## BRD: Why This Is Worth Doing

## MRD: Market, User, Competition

## Switching Reason

## Decision
- Do:
- Do not do:
- Evidence:
```

Update state to `phase: research`.

## Step 3: Research and Current State → `product/02-research.md`

Cover checkpoints 3 and 4:

- Business / scenario research.
- Current state and existing alternatives.

Required sections:

```markdown
## Scenario Research

## Current Workflow

## Existing Alternatives

## Evidence
```

For C-side products, include start / continue / reuse / share-or-pay / drop-off / behavior loop.

For B-side products, include process / roles / permissions / data objects / reports / risk / collaboration.

Update state to `phase: problem-solution`.

## Step 4: Problem and Solution → `product/03-problem-solution.md` and `product/04-product-blueprint.md`

`product/03-problem-solution.md` covers checkpoints 5 and 6:

```markdown
## Problem Summary

## Severity and Frequency

## Solution Idea

## Evidence

## Non-goals
```

`product/04-product-blueprint.md` covers checkpoints 7 and 8:

```markdown
## Product Solution

## Positioning

## Core Flow

## Evolution Blueprint

## Scope Boundary
```

Update state to `phase: product-spec`.

## Step 5: Product Specification → product spec files

Write four files:

```text
product/05-model-flow-role.md
product/06-experience-spec.md
product/07-data-permission-analytics.md
product/08-prd.md
```

`05-model-flow-role.md` covers data model and roles:

```markdown
## Business Data Model

## Object Relationships

## Workflow

## Roles and Handoffs
```

`06-experience-spec.md` covers interface design:

```markdown
## Key Screens

## Core States

## Empty, Loading, Error States

## Golden Journeys
```

`07-data-permission-analytics.md` covers reports, tracking, and permissions:

```markdown
## Report Design

## Tracking Plan

## Permission Model

## Risk Controls
```

`08-prd.md` covers the executable PRD:

```markdown
## Product Requirements

## Acceptance Criteria

## Edge Cases

## Out of Scope
```

Update state to `phase: tech-project-plan`.

## Step 6: Technical and Project Plan → `product/09-tech-project-plan.md`

Cover checkpoints 16 and 17:

```markdown
## Technical Plan

## Architecture Decision

## Project Plan

## Milestones

## Risks and Mitigations
```

If architecture selection is not settled, include the architecture decision here rather than routing to `/yishuship:arch-design`. Detailed architecture design can still go to `/yishuship:arch-design` after selection.

Update state to `phase: handoff`.

## Step 7: Engineering Handoff → `delivery/design-spec.md`

Write `delivery/design-spec.md` as the product-to-engineering bridge.

Required sections:

```markdown
## Engineering Goal

## Product Context

## Requirements

## Acceptance Criteria

## Constraints

## Source Artifacts
```

For compatibility, also write or update `plan/spec.md` with the same engineering-facing acceptance criteria when the next phase is `/yishuship:design` or `/yishuship:auto`.

Update state to `phase: complete` when handoff is ready.

## Step 8: Optional Growth Loop

Only run when the user asks for operation, data analysis, iteration, or learning.

Write:

```text
growth/01-ops-plan.md
growth/02-data-analysis.md
growth/03-iteration-plan.md
growth/04-learning.md
```

Growth output becomes the input to the next lifecycle iteration.