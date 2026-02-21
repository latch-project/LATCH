#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# === CONFIG ===

RUNNER_PY="$ROOT_DIR/src/logic_evaluation.py"
LLM_PROVIDER="google_gemini-2.5-flash"
BASEFOLDER="$ROOT_DIR/evaluation/logic_evaluation"
SPECIAL="result"

export PYTHONPATH="$ROOT_DIR:$ROOT_DIR/src:$PYTHONPATH"

# === RUN ===
python3 "$RUNNER_PY" \
  --special "$SPECIAL" \
  --llm_provider "$LLM_PROVIDER" \
  --basefolder "$BASEFOLDER" \
  --print_config