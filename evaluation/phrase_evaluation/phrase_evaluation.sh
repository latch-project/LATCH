#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_DIR="$ROOT_DIR/src"
RUNNER_PY="$SRC_DIR/phrase_evaluation.py"

# === CONFIG ===
SPECIAL="result"
LLM_PROVIDER="google_gemini-2.5-flash"
BASEFOLDER="$ROOT_DIR/evaluation/phrase_evaluation"
SCHEMA="nhanes"

export PYTHONPATH="$ROOT_DIR:$ROOT_DIR/src:$PYTHONPATH"

python "$RUNNER_PY" \
  --special "$SPECIAL" \
  --llm-provider "$LLM_PROVIDER" \
  --basefolder "$BASEFOLDER" \
  --schema "$SCHEMA"