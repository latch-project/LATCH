#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROMPT_DIR="$ROOT_DIR/analyses/prompts/registry"
RESULT_FOLDER="$ROOT_DIR/analyses/results/registry/full_analysis"
RUNNER_PY="$ROOT_DIR/src/run_latch_log.py"
LLM_PROVIDER="${LLM_PROVIDER:-google_gemini-2.5-flash}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

echo "ROOT_DIR: $ROOT_DIR"
python3 "$ROOT_DIR/data/registry/validate_registry_example.py"
mkdir -p "$RESULT_FOLDER"

for PROMPT_FILE in "$PROMPT_DIR"/*.txt; do
    [ -f "$PROMPT_FILE" ] || continue

    BASENAME="$(basename "$PROMPT_FILE" .txt)"
    ANALYSIS_NAME="registry_${BASENAME}"

    echo "======================================"
    echo "Running full registry analysis: $PROMPT_FILE"
    echo "Analysis name: $ANALYSIS_NAME"
    echo "Result folder: $RESULT_FOLDER"
    echo "======================================"

    "$PYTHON_BIN" "$RUNNER_PY" \
        --result-folder "$RESULT_FOLDER" \
        --analysis-name "$ANALYSIS_NAME" \
        --llm-provider "$LLM_PROVIDER" \
        --question "$(<"$PROMPT_FILE")"
done
