#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

RESULT_FOLDER="$ROOT_DIR/evaluation/one_step/results"
PROMPT_DIR="$ROOT_DIR/analyses/prompts/fig2_reproduction"
RUNNER_PY="$ROOT_DIR/src/run_latch_onestep.py"
LLM_PROVIDER="google_gemini-2.5-flash"

for PROMPT_FILE in "$PROMPT_DIR"/2*.txt; do
  BASENAME="$(basename "$PROMPT_FILE" .txt)"
  ANALYSIS_NAME="fig_2_${BASENAME}"

  for RUN_ID in {1..1}; do
    echo "======================================"
    echo "Running: $PROMPT_FILE"
    echo "Repetition: $RUN_ID"
    echo "Analysis name: $ANALYSIS_NAME"
    echo "ROOT_DIR: $ROOT_DIR"
    echo "Lookup table: $LOOKUP_TABLE"
    echo "======================================"

    python "$RUNNER_PY" \
      --result-folder "$RESULT_FOLDER" \
      --analysis-name "$ANALYSIS_NAME" \
      --llm-provider "$LLM_PROVIDER" \
      --lookup-table "$LOOKUP_TABLE" \
      --question "$(cat "$PROMPT_FILE")"
  done
done
