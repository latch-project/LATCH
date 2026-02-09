#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# === CONFIG ===
RUNNER_PY="$ROOT_DIR/src/content_evaluation.py"
PROVIDER="google_gemini-2.5-flash"
BASEPATH="$ROOT_DIR/evaluation/content_evaluation"
SPECIALNOTE="result"

# Make sure Python can import from repo root + src (for config, utils, etc.)
export PYTHONPATH="$ROOT_DIR:$ROOT_DIR/src:$PYTHONPATH"

# === RUN ===
python "$RUNNER_PY" \
  --provider "$PROVIDER" \
  --basepath "$BASEPATH" \
  --specialnote "$SPECIALNOTE"
