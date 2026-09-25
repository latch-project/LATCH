#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "ROOT_DIR: $ROOT_DIR"

export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

RESULT_ROOT="$ROOT_DIR/analyses/results/registry"
PROMPT_ROOT="$ROOT_DIR/analyses/prompts/registry"
RUNNER_PY="$ROOT_DIR/src/run_latch_registry.py"

LLM_PROVIDER="google_gemini-2.5-flash"

RESULT_FOLDER="$RESULT_ROOT/result"
SQL_FOLDER="$RESULT_ROOT/sql"

mkdir -p "$RESULT_FOLDER" "$SQL_FOLDER"

python3 "$RUNNER_PY" \
    --prompt_folder "$PROMPT_ROOT" \
    --result_folder "$RESULT_FOLDER" \
    --sql_folder "$SQL_FOLDER" \
    --analysis_name registry_test \
    --llm_provider "$LLM_PROVIDER"
