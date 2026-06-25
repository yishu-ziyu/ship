#!/usr/bin/env bash
set -u

# yishuship PM init — initialize PM workflow state.
# Usage: bash pm-init.sh [task_description]
#
# Creates:
#   .ship/pm-state.yaml          — workflow state
#   .ship/tasks/<task_id>/pm/    — PM artifacts directory

CWD="${1:-.}"
DESC="${2:-}"

TASK_ID=$(date +%Y%m%d-%H%M%S)
TASK_DIR="$CWD/.ship/tasks/$TASK_ID"
PM_DIR="$TASK_DIR/pm"

mkdir -p "$PM_DIR"

cat > "$CWD/.ship/pm-state.yaml" << EOF
phase: discover
task_id: $TASK_ID
created: $(date -Iseconds)
description: "$DESC"
EOF

# Write raw input
if [ -n "$DESC" ]; then
  mkdir -p "$TASK_DIR/input"
  echo "$DESC" > "$TASK_DIR/input/requirement.md"
fi

echo "PM workflow initialized."
echo "  State: $CWD/.ship/pm-state.yaml"
echo "  Task:  $TASK_DIR"
echo "  Phase: discover"
