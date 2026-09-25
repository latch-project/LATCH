#!/usr/bin/env python3

import sys
import json
import csv
import argparse
import time
from pathlib import Path
from datetime import datetime
import copy
import pandas as pd
import utils_extended as utils
import prompts
from process import (
    FileManager,
    QueryParser,
    QueryParser_Onestep,
    VariableMatcher,
    SQLGenerator,
    ProcessStats,
    ResultLogger,
)
 

def parse_args():
    parser = argparse.ArgumentParser(description="Run LLM-to-SQL processing pipeline")

    parser.add_argument("--result-folder", type=str, required=True)
    parser.add_argument("--analysis-name", type=str, required=True)
    parser.add_argument("--llm-provider", type=str, required=True)
    parser.add_argument("--question", type=str, required=True)
    parser.add_argument("--lookup-table",type=str, default=None)

    return parser.parse_args()


def upsert_row_to_csv(csv_path, headers, values, key_field="Title"):
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    if csv_path.exists():
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    clean_values = {}
    for h in headers:
        v = values.get(h, "")

        if v is None:
            clean_values[h] = ""
        else:
            clean_values[h] = str(v)

    key_value = str(clean_values.get(key_field, ""))

    updated = False
    new_rows = []

    for row in rows:
        if str(row.get(key_field, "")) == key_value:
            if not updated:
                new_rows.append(clean_values)
                updated = True
            # skip duplicate old rows with same Title
        else:
            new_rows.append(row)

    if not updated:
        new_rows.append(clean_values)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(new_rows)


def main() -> int:
    MAX_RETRIES = 3
    RETRY_SLEEP_SECONDS = 2

    last_err: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            args = parse_args()

            result_folder = args.result_folder
            analysis_name = args.analysis_name
            llm_provider = args.llm_provider
            question = args.question
            

            lookup_table = args.lookup_table
            result_log = f"{result_folder}/{analysis_name}_{llm_provider}_result_log.csv"
            llm_log = None

            enable_lookup = bool(lookup_table)
            enable_adding = bool(lookup_table)

            Path(result_folder).mkdir(parents=True, exist_ok=True)

            start_time = datetime.now()

            title = utils.random_id()
            print(f"Processing question # title={title}")

            headers = [
                "Title",
                "Schema",
                "Question",
                "Structured Question",
                "Initial Parsed Question",
                "Parsed Question",
                "Schema Incorportation",
                "Weight",
                "SQL",
                "Cohort",
                "Dataframeshape",
                "R",
                "Variables",
                "Statistics",
                "Impute R",
                "Impute Stats",
                "Impute Variable",
                "Analysis",
                "Period",
                "Years",
                "LLM provider",
                "Safeguard1",
                "Safeguard2",
                "Safeguard3",
                "Total Time",
                "Total Cost",
                "SQL Error",
                "SQL Attempts",
                "Lookup Table",
                "Result Log",
                "LLM Log",
                "Status",
                "Error",
            ]

            run_values = {h: "" for h in headers}
            run_values.update(
                {
                    "Title": title,
                    "Question": question,
                    "LLM provider": llm_provider,
                    "Lookup Table": lookup_table,
                    "Result Log": result_log,
                    "LLM Log": llm_log,
                    "Status": "Started",
                }
            )

            upsert_row_to_csv(result_log, headers, run_values)

            manager = FileManager(title, result_log, lookup_table, llm_log)

            try:
                parsed_query_info = QueryParser_Onestep(
                    title,
                    question,
                    llm_provider,
                    llm_log,
                )
                initial_parsed_question = copy.deepcopy(parsed_query_info.question_parse)
                run_values.update(
                    {
                        "Schema": parsed_query_info.schema,
                        "Structured Question": parsed_query_info.question_structured,
                        "Initial Parsed Question":initial_parsed_question,
                        "Parsed Question": parsed_query_info.question_parse,
                        "Analysis": parsed_query_info.analysis,
                        "Period": parsed_query_info.period,
                        "Years": parsed_query_info.years,
                        "Safeguard1": parsed_query_info.safeguard1,
                        "Total Cost": [parsed_query_info.cost],
                        "Status": "Query Parsing Complete",
                        
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

            except Exception as e:
                print(f"[ERROR] QueryParser failed: {e}")
                last_err = e
                run_values.update(
                    {
                        "Status": "Failed: Query Parsing",
                        "Error": str(e),
                      
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1

            try:
                variable_matcher = VariableMatcher(
                    title=title,
                    question_parse=parsed_query_info.question_parse,
                    dictionary_path=parsed_query_info.dictionary,
                    schema_path=parsed_query_info.schema_folder,
                    years=parsed_query_info.years,
                    schema=parsed_query_info.schema,
                    question=question,
                    enable_lookup=enable_lookup,
                    enable_adding=enable_adding,
                    llm_provider=llm_provider,
                    lookup_table=manager.lookup_table,
                    llm_log=llm_log,
                )

                run_values.update(
                    {
                        "Schema Incorportation": variable_matcher.summary,
                        "Safeguard2": variable_matcher.safeguard2,
                        "Total Cost": [
                            parsed_query_info.cost,
                            variable_matcher.cost,
                        ],
                        "Status": "Variable Matching Complete",
                       
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

            except Exception as e:
                print(f"[ERROR] VariableMatcher failed: {e}")
                last_err = e
                run_values.update(
                    {
                        "Status": "Failed: Variable Matching",
                        "Error": str(e),
                    
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1

            try:
                sql = SQLGenerator(
                    title,
                    parsed_query_info.schema,
                    question,
                    parsed_query_info.analysis,
                    variable_matcher.final_source_value_dictionary,
                    parsed_query_info.years,
                    parsed_query_info.question_parse,
                    variable_matcher.summary,
                    llm_provider,
                    llm_log,
                )

                run_values.update(
                    {
                        "Weight": sql.weight,
                        "SQL": sql.total_sql,
                        "Cohort": sql.cohort,
                        "Safeguard3": sql.safeguard,
                        "SQL Error": sql.error,
                        "SQL Attempts": sql.attempts,
                        "Total Cost": [
                            parsed_query_info.cost,
                            variable_matcher.cost,
                            sql.cost,
                        ],
                        "Status": "SQL Generation Complete",
                        
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

            except Exception as e:
                print(f"[ERROR] SQL failed: {e}")
                last_err = e
                run_values.update(
                    {
                        "Status": "Failed: SQL Generation",
                        "Error": str(e),
                        
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1

            try:
                stats = ProcessStats(
                    sql.dataframe,
                    parsed_query_info.analysis,
                    parsed_query_info.schema,
                )

                run_values.update(
                    {
                        "Dataframeshape": stats.shape,
                        "R": stats.R,
                        "Variables": (
                            stats.variable.to_dict(orient="records")
                            if hasattr(stats.variable, "to_dict")
                            else stats.variable
                        ),
                        "Statistics": (
                            stats.stats_summary.to_dict(orient="records")
                            if hasattr(stats.stats_summary, "to_dict")
                            else stats.stats_summary
                        ),
                        "Impute R": stats.impute_r,
                        "Impute Stats": (
                            stats.impute_stats_summary.to_dict(orient="records")
                            if hasattr(stats.impute_stats_summary, "to_dict")
                            else stats.impute_stats_summary
                        ),
                        "Impute Variable": (
                            stats.impute_variable.to_dict(orient="records")
                            if hasattr(stats.impute_variable, "to_dict")
                            else stats.impute_variable
                        ),
                        "Status": "Stats Processing Complete",
                        
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

            except Exception as e:
                print(f"[ERROR] STAT failed: {e}")
                last_err = e
                run_values.update(
                    {
                        "Status": "Failed: Stats Processing",
                        "Error": str(e),
            
                    }
                )
                upsert_row_to_csv(result_log, headers, run_values)

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1

            total_time = (datetime.now() - start_time).total_seconds()

            run_values.update(
                {
                    "Total Time": total_time,
                    "Total Cost": [
                        parsed_query_info.cost,
                        variable_matcher.cost,
                        sql.cost,
                    ],
                    "Status": "Finished Successfully",
                   
                    "Error": "",
                }
            )

            upsert_row_to_csv(result_log, headers, run_values)

            print(f"Finished successfully. Run ID: {title}")
            print(f"Total time: {total_time:.2f} seconds")

            return 0

        except Exception as e:
            print(f"[ERROR] Unhandled failure on attempt {attempt}/{MAX_RETRIES}: {e}")
            last_err = e

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP_SECONDS)
                continue

            return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())