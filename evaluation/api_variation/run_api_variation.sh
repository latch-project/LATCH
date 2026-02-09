#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

RESULT_FOLDER="$ROOT_DIR/evaluation/api_variation/results"
PROMPT_DIR="$ROOT_DIR/analyses/prompts/variation_api"
RUNNER_PY="$ROOT_DIR/src/run_latch.py"
LLM_PROVIDERS=(
  "anthropic_claude-sonnet-4-5-20250929"
  "anthropic_claude-3-7-sonnet-20250219"
  "google_gemini-2.0-flash"
  "openai_gpt-4.1-2025-04-14"
  "openai_gpt-5.1-2025-11-13"
)

for LLM_PROVIDER in "${LLM_PROVIDERS[@]}"; do

  for PROMPT_FILE in "$PROMPT_DIR"/2*.txt; do
    BASENAME="$(basename "$PROMPT_FILE" .txt)"
    ANALYSIS_NAME="fig_2${BASENAME}"

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
done