#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

RESULT_FOLDER="$ROOT_DIR/analyses/results/fig3_extension"
PROMPT_DIR="$ROOT_DIR/analyses/prompts/fig3_extension"
RUNNER_PY="$ROOT_DIR/src/run_latch.py"
LLM_PROVIDER="google_gemini-2.5-flash"

for PROMPT_FILE in "$PROMPT_DIR"/3*.txt; do
  BASENAME="$(basename "$PROMPT_FILE" .txt)"
  ANALYSIS_NAME="fig_3_${BASENAME}"

  echo "======================================"
  echo "Running: $PROMPT_FILE"
  echo "Analysis name: $ANALYSIS_NAME"
  echo "ROOT_DIR: $ROOT_DIR"
  echo "======================================"

  python "$RUNNER_PY" \
    --result-folder "$RESULT_FOLDER" \
    --analysis-name "$ANALYSIS_NAME" \
    --llm-provider "$LLM_PROVIDER" \
    --question "$(cat "$PROMPT_FILE")"
done