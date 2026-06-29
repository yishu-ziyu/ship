---
name: auto
version: 0.2.0
description: >
  Run Ship's full production workflow from raw requirement to PR: pm-intake(product lifecycle) → PM Gate → design → dev → e2e → review → qa → refactor → handoff. Growth Loop is optional continuation after handoff, not mandatory. Use only for explicit /yishuship:auto,
  auto pipeline requests, or end-to-end delivery.
allowed-tools:
  - Bash
  - Read
  - Agent
  - TodoWrite
---

# Ship: Auto

Full staged workflow for explicit end-to-end production delivery.
pm-intake(product lifecycle) → PM Gate → design → dev → e2e → review → qa → refactor → handoff

Growth Loop is optional continuation after handoff, not mandatory.

## Execution

Resolve `../../scripts/auto-orchestrate.sh` relative to this skill file, then
run the shared stage-aware orchestrator:

```bash
SHIP_ORCH="../../scripts/auto-orchestrate.sh"
if [ -f .ship/ship-auto.local.md ]; then
  "$SHIP_ORCH" resume
else
  "$SHIP_ORCH" init '<user requirement goes here>'
fi
```

Then follow the `/yishuship:auto` dispatch loop: read `PROMPT_FILE`, dispatch the
agent, classify the report card, and call `complete <PHASE>`.

## Compatibility Note

The underlying orchestrator still dispatches the engineering state machine. V2 product lifecycle artifacts are enforced by PM Gate and by the handoff generated from `/yishuship:pm-intake`.

## Standalone Skill Boundary

`/yishuship:auto` is only for full production workflow runs. If the user asks for a
specific phase such as design, development, E2E, review, QA, refactor, or
handoff, invoke that standalone `/yishuship:*` skill directly instead of routing
through auto.
