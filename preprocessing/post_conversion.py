import os
import json
import argparse
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
import sys
from pathlib import Path

import sys
from pathlib import Path

# sys.path.append(str(Path.cwd().parents[0]))
sys.path.append(str(Path.cwd()))
from config import other_config, data_config, config


def create_db_engine(db_config):
    user = db_config.get("user", "")
    password = db_config.get("password")
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    database = db_config.get("database", "")

    auth = user
    if password is not None:
        auth += f":{password}"
    conn_str = f"postgresql+psycopg2://{auth}@{host}:{port}/{database}"
    return create_engine(conn_str)


def csv_to_psql_schema(csv_folder, schema_name, db_config):
    csv_files = []
    for root, dirs, files in os.walk(csv_folder):
        for file in files:
            if file.endswith(".csv") and "long" not in file:
                csv_files.append(os.path.join(root, file))

    engine = create_db_engine(db_config)
    print(f"Connecting to: {engine.url}")

    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;'))
        connection.execute(text(f'CREATE SCHEMA "{schema_name}";'))

        for csv_filepath in tqdm(csv_files, desc="Uploading CSVs to DB"):
            table_name = os.path.splitext(os.path.basename(csv_filepath))[0]
            df = pd.read_csv(csv_filepath)

            df.to_sql(
                table_name,
                connection,
                schema=schema_name,
                if_exists="replace",
                index=False,
            )


def extract_schema_and_samples(engine, table, schema_name):
    schema_data = []
    with engine.connect() as connection:
        columns_query = text(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = :schema
              AND table_name = :table
            """
        )
        columns_info = connection.execute(
            columns_query, {"schema": schema_name, "table": table}
        ).fetchall()

        table_schema = {"table": f"{schema_name}.{table}", "columns": {}}

        for col_name, col_type in columns_info:
            sample_values_query = text(
                f"""
                SELECT DISTINCT "{col_name}"
                FROM "{schema_name}"."{table}"
                WHERE "{col_name}" IS NOT NULL
                LIMIT 20
                """
            )
            try:
                sample_values = [
                    str(row[0])
                    for row in connection.execute(sample_values_query).fetchall()
                ]
            except Exception as e:
                sample_values = [f"[Error: {e}]"]

            while len(sample_values) < 10:
                sample_values.append("")

            table_schema["columns"][col_name] = {
                "data_type": col_type,
                "sample_values": sample_values,
            }

        schema_data.append(table_schema)

    return schema_data


def make_schema(schema_name, schema_folder, converted_data_folder, db_config):
    os.makedirs(schema_folder, exist_ok=True)

    table_names = []
    for root, dirs, files in os.walk(converted_data_folder):
        for file in files:
            table_name, ext = os.path.splitext(file)
            if ext == ".csv" and "long" not in file:
                table_names.append(table_name)

    engine = create_db_engine(db_config)

    for table in tqdm(table_names, desc="Processing tables", total=len(table_names)):
        schema_data = extract_schema_and_samples(engine, table, schema_name)
        output_file_path = os.path.abspath(f"{schema_folder}/{table}.json")
        with open(output_file_path, "w") as f:
            json.dump(schema_data, f, indent=4)


def make_combined_schema(schema_folder, output_combined_schema):
    os.makedirs(os.path.dirname(output_combined_schema), exist_ok=True)

    all_rows = []
    for file in os.listdir(schema_folder):
        if file.endswith(".json"):
            file_path = os.path.join(schema_folder, file)
            with open(file_path, "r") as f:
                data = json.load(f)

            for table_entry in data:
                table_name = table_entry["table"]
                columns = table_entry["columns"]

                for column_name, column_info in columns.items():
                    values = column_info.get("sample_values", [])
                    all_rows.append(
                        {
                            "column_name": column_name,
                            "column_description": "",
                            "table_name": table_name,
                            "values": values,
                        }
                    )

    df = pd.DataFrame(all_rows)
    df.to_csv(output_combined_schema, index=False)
    print(f"Wrote schema summary: {output_combined_schema}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="Root folder containing formatted_dataset/")
    ap.add_argument(
        "--schema-name", default="aireadi", help="Postgres schema name to create"
    )
    ap.add_argument("--db-name", default=config.DB_NAME, help="Postgres database name")
    ap.add_argument("--db-user", default=config.DB_USER, help="Postgres user")
    ap.add_argument(
        "--db-password", default=config.DB_PASSWORD, help="Postgres password"
    )
    ap.add_argument("--db-host", default=config.DB_HOST, help="Postgres host")
    ap.add_argument("--db-port", type=int, default=config.DB_PORT, help="Postgres port")

    args = ap.parse_args()

    db_config = {
        "database": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
        "host": args.db_host,
        "port": args.db_port,
    }

    converted_data_folder = os.path.join(args.root, "formatted_dataset")
    schema_folder = os.path.join(args.root, "schema")
    output_combined_schema = os.path.join(
        args.root, "schema_summary", "schema_summary.csv"
    )

    if not os.path.exists(converted_data_folder):
        raise FileNotFoundError(f"Missing: {converted_data_folder}")

    csv_to_psql_schema(converted_data_folder, args.schema_name, db_config)
    make_schema(args.schema_name, schema_folder, converted_data_folder, db_config)
    make_combined_schema(schema_folder, output_combined_schema)


if __name__ == "__main__":
    main()
