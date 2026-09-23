#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "ROOT_DIR: $ROOT_DIR"

export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

RESULT_ROOT="$ROOT_DIR/analyses/results/iteration"
PROMPT_ROOT="$ROOT_DIR/analyses/prompts/iteration"
RUNNER_PY="$ROOT_DIR/src/run_latch_log.py"
LLM_PROVIDER="google_gemini-2.5-flash" 

PROMPT_GROUPS=(
  "exploratory_1"
  "exploratory_2"
  "exploratory_3"
  "extension_1"
  "extension_2"
  "reproduction_1"
  "reproduction_2"
  "reproduction_3"
)

for GROUP in "${PROMPT_GROUPS[@]}"; do

  PROMPT_DIR="$PROMPT_ROOT/$GROUP"
  RESULT_FOLDER="$RESULT_ROOT/$GROUP"

  mkdir -p "$RESULT_FOLDER"

  echo "======================================"
  echo "PROMPT GROUP: $GROUP"
  echo "PROMPT DIR: $PROMPT_DIR"
  echo "RESULT DIR: $RESULT_FOLDER"
  echo "======================================"

  for PROMPT_FILE in "$PROMPT_DIR"/*.txt; do

    [ -f "$PROMPT_FILE" ] || continue

    BASENAME="$(basename "$PROMPT_FILE" .txt)"
    ANALYSIS_NAME="${BASENAME}"

    for RUN_ID in {1..1}; do

      echo "======================================"
      echo "Group: $GROUP"
      echo "Running: $PROMPT_FILE"
      echo "Repetition: $RUN_ID"
      echo "Analysis name: $ANALYSIS_NAME"
      echo "Result folder: $RESULT_FOLDER"
      echo "======================================"

      python "$RUNNER_PY" \
        --result-folder "$RESULT_FOLDER" \
        --analysis-name "$ANALYSIS_NAME" \
        --llm-provider "$LLM_PROVIDER" \
        --question "$(cat "$PROMPT_FILE")"

    done
  done
done