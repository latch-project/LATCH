#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

INPUT_DIRS=(
  "$ROOT_DIR/analyses/results/fig2_reproduction"

)

OUTPUT_DIR="$ROOT_DIR/evaluation/variable_rank/variable_n_rank"

echo "ROOT_DIR: $ROOT_DIR"
echo

for input_dir in "${INPUT_DIRS[@]}"; do
  echo "=================================================="
  echo "Folder: $input_dir"

  if [[ ! -d "$input_dir" ]]; then
    echo "ERROR: folder does not exist"
    continue
  fi

  find "$input_dir" -type f -name "*.csv" -print | sort
  csv_count="$(find "$input_dir" -type f -name "*.csv" | wc -l)"
  echo "CSV count: $csv_count"
  echo
done

mkdir -p "$OUTPUT_DIR"

python "$ROOT_DIR/src/variable_ranks.py" \
  --input-dirs "${INPUT_DIRS[@]}" \
  --output-dir "$OUTPUT_DIR" \
  --recursive