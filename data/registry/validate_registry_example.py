#!/usr/bin/env python3
"""Validate the registry metadata and checked-in example SQL."""

import csv
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUMMARY = PROJECT_ROOT / "data/registry/schema_summary/schema_summary.csv"
SQL_DIR = PROJECT_ROOT / "analyses/results/registry/sql"
TABLE_DIR = PROJECT_ROOT / "data/registry/tables"


def main():
    with SUMMARY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    fields = {(row["table_name"], row["column_name"]) for row in rows}
    errors = []
    if not any(column == "patient_id" for _, column in fields):
        errors.append("schema summary does not define patient_id")

    expected_tables = {row["table_name"] for row in rows}
    for table in sorted(expected_tables):
        path = TABLE_DIR / f"{table}.csv"
        if not path.exists():
            errors.append(f"missing fictional table {path.relative_to(PROJECT_ROOT)}")
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            row_count = sum(1 for _ in reader)
        expected_columns = {"patient_id"} | {
            column for row_table, column in fields if row_table == table
        }
        if set(header) != expected_columns:
            errors.append(f"{path.name}: columns do not match schema summary")
        if row_count != 5000:
            errors.append(f"{path.name}: expected 5000 rows, found {row_count}")

    pattern = re.compile(
        r'SELECT patient_id, "([^"]+)" AS "[^"]+"\s+'
        r'FROM registry\.([A-Za-z0-9_]+)'
    )
    for path in sorted(SQL_DIR.glob("example_prompt_*_sql.sql")):
        for column, table in pattern.findall(path.read_text(encoding="utf-8")):
            if (table, column) not in fields:
                errors.append(f"{path.name}: unknown registry field {table}.{column}")

    if errors:
        raise SystemExit("Registry example validation failed:\n- " + "\n- ".join(errors))
    print("Registry example metadata and saved SQL are consistent.")


if __name__ == "__main__":
    main()
