#!/usr/bin/env python3

import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd

import utils
import prompts

from process import (
    FileManager,
    QueryParser,
    VariableMatcher,
    SQLGenerator,
    ProcessStats,
    ResultLogger,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run LLM-to-SQL processing pipeline")

    parser.add_argument(
        "--result-folder",
        type=str,
        required=True,
        help="Output directory for logs and result files",
    )

    parser.add_argument(
        "--analysis-name",
        type=str,
        required=True,
        help="Analysis name prefix (ex: fig4)",
    )

    parser.add_argument(
        "--llm-provider",
        type=str,
        required=True,
        help="LLM provider name (ex: google_gemini-2.5-flash)",
    )

    parser.add_argument(
        "--question",
        type=str,
        required=True,
        help="Input question to process",
    )

    return parser.parse_args()


import time


def main() -> int:
    MAX_RETRIES = 3
    RETRY_SLEEP_SECONDS = 2

    last_err: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            args = parse_args()

            # ---- CLI Inputs ----
            result_folder = args.result_folder
            analysis_name = args.analysis_name
            llm_provider = args.llm_provider
            question = args.question

            lookup_table = (
                None  # f"{result_folder}/{analysis_name}_{llm_provider}_lookup.csv"
            )
            result_log = (
                f"{result_folder}/{analysis_name}_{llm_provider}_result_log.csv"
            )
            llm_log = (
                None  # f"{result_folder}/{analysis_name}_{llm_provider}_llm_log.csv"
            )

            enable_lookup = False
            enable_adding = False

            # Create output directory
            Path(result_folder).mkdir(parents=True, exist_ok=True)

            start_time = datetime.now()

            title = utils.random_id()
            print(f"Processing question # title={title}")

            manager = FileManager(title, result_log, lookup_table, llm_log)

            # ---------------- Query Parsing ----------------
            try:
                parsed_query_info = QueryParser(
                    title,
                    question,
                    llm_provider,
                    llm_log,
                )
            except Exception as e:
                print(f"[ERROR] QueryParser failed: {e}")
                last_err = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1

            # ---------------- Variable Matching ----------------
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
            except Exception as e:
                print(f"[ERROR] VariableMatcher failed: {e}")
                last_err = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1

            # ---------------- SQL Generation ----------------
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

            except Exception as e:
                print(f"[ERROR] SQL failed: {e}")
                last_err = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1
            # ---------------- Stats Processing ----------------
            try:
                stats = ProcessStats(
                    sql.dataframe,
                    parsed_query_info.analysis,
                    parsed_query_info.schema,
                )
            except Exception as e:
                print(f"[ERROR] STAT failed: {e}")
                last_err = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP_SECONDS)
                    continue
                return 1

            total_time = (datetime.now() - start_time).total_seconds()

            # ---------------- Result Logging ----------------
            ResultLogger(
                title,
                parsed_query_info.schema,
                parsed_query_info.question,
                parsed_query_info.question_structured,
                parsed_query_info.question_parse,
                variable_matcher.summary,
                sql.weight,
                sql.total_sql,
                sql.cohort,
                stats.shape,
                stats.R,
                stats.variable,
                stats.stats_summary,
                stats.impute_r,
                stats.impute_stats_summary,
                stats.impute_variable,
                parsed_query_info.analysis,
                parsed_query_info.period,
                parsed_query_info.years,
                parsed_query_info.llm_provider,
                parsed_query_info.safeguard1,
                variable_matcher.safeguard2,
                sql.safeguard,
                total_time,
                [parsed_query_info.cost, variable_matcher.cost, sql.cost],
                sql.error,
                sql.attempts,
                lookup_table,
                result_log,
                llm_log,
            )

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
