#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 "$ROOT_DIR/data/registry/generate_synthetic_tables.py" "$@"
python3 "$ROOT_DIR/data/registry/validate_registry_example.py"
python3 "$ROOT_DIR/data/registry/load_synthetic_registry.py" --replace
