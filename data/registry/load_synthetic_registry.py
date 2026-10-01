#!/usr/bin/env python3
"""Load fictional registry-style CSV tables into PostgreSQL.

The records are entirely synthetic. They are not derived from, calibrated to,
or intended to reproduce the AAO IRIS Registry.
"""

import argparse
import ast
import csv
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_SUMMARY = PROJECT_ROOT / "data/registry/schema_summary/schema_summary.csv"
DATABASE_SCHEMA = "registry"
TABLE_DIR = PROJECT_ROOT / "data/registry/tables"


def load_project_env():
    """Load simple KEY=VALUE entries without overriding the shell environment."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table-dir", type=Path, default=TABLE_DIR)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Required safety flag: replace tables in the local registry schema.",
    )
    return parser.parse_args()


def load_metadata():
    tables = {}
    with SCHEMA_SUMMARY.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            column = row["column_name"]
            if column == "patient_id":
                continue
            values = ast.literal_eval(row["values"])
            tables.setdefault(row["table_name"], []).append((column, values))
    return tables


def numeric_values(values):
    try:
        return [float(value) for value in values]
    except (TypeError, ValueError):
        return None


def column_type(values):
    return "DOUBLE PRECISION" if numeric_values(values) is not None else "TEXT"


def connect():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "latch"),
        user=os.getenv("POSTGRES_USER", "latchuser"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "10010")),
    )


def main():
    args = parse_args()
    if not args.replace:
        raise SystemExit(
            "Refusing to modify PostgreSQL without --replace. Use only with the "
            "local demonstration database; never target a real registry database."
        )
    load_project_env()
    tables = load_metadata()
    loaded_rows = None

    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                sql.Identifier(DATABASE_SCHEMA)
            )
        )
        for table_name, columns in tables.items():
            cursor.execute(
                sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                    sql.Identifier(DATABASE_SCHEMA), sql.Identifier(table_name)
                )
            )
            definitions = [
                sql.SQL("{} TEXT PRIMARY KEY").format(sql.Identifier("patient_id"))
            ]
            definitions.extend(
                sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(column_type(values)))
                for name, values in columns
            )
            cursor.execute(
                sql.SQL("CREATE TABLE {}.{} ({})").format(
                    sql.Identifier(DATABASE_SCHEMA),
                    sql.Identifier(table_name),
                    sql.SQL(", ").join(definitions),
                )
            )

            names = ["patient_id"] + [name for name, _ in columns]
            csv_path = args.table_dir / f"{table_name}.csv"
            with csv_path.open(newline="", encoding="utf-8") as handle:
                records = [[row[name] for name in names] for row in csv.DictReader(handle)]
            if loaded_rows is None:
                loaded_rows = len(records)
            elif len(records) != loaded_rows:
                raise ValueError(f"Row-count mismatch in {csv_path}")
            statement = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
                sql.Identifier(DATABASE_SCHEMA),
                sql.Identifier(table_name),
                sql.SQL(", ").join(map(sql.Identifier, names)),
            )
            execute_values(cursor, statement.as_string(connection), records, page_size=500)

    print(
        f"Loaded {len(tables)} fictional registry-style CSV tables with "
        f"{loaded_rows} participants into schema '{DATABASE_SCHEMA}'."
    )


if __name__ == "__main__":
    main()
