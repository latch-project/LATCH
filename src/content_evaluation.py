#!/usr/bin/env python3


import argparse
import os
from datetime import datetime
import pandas as pd

import utils
from process import (
    FileManager,
    QueryParser,
)
import sys
from pathlib import Path

sys.path.append(str(Path.cwd().parents[0]))
from config import other_config, data_config, config


def build_paths(basepath: str, specialnote: str, provider: str):
    prefix = f"{specialnote}_" if specialnote else ""
    lookup_table = None  # os.path.join(basepath, f"{prefix}{provider}_lookuptable.csv")
    result_log = os.path.join(basepath, f"{prefix}{provider}_result_log.csv")
    llm_log = None  # os.path.join(basepath, f"{prefix}{provider}_llm_log.csv")
    return lookup_table, result_log, llm_log


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run evaluation over question components and log results."
    )
    p.add_argument(
        "--provider",
        required=True,
        help="LLM provider string (e.g., google_gemini-2.5-flash).",
    )
    p.add_argument(
        "--basepath", required=True, help="Directory where CSV outputs live."
    )
    p.add_argument(
        "--specialnote",
        default="",
        help="Optional prefix note. Produces {specialnote}_{provider}_*.csv (specialnote can be empty).",
    )

    p.add_argument(
        "--enable-lookup",
        action="store_true",
        help="Enable lookup behavior (default: enabled).",
    )
    p.add_argument(
        "--disable-lookup", action="store_true", help="Disable lookup behavior."
    )
    p.add_argument(
        "--enable-adding",
        action="store_true",
        help="Enable adding behavior (default: enabled).",
    )
    p.add_argument(
        "--disable-adding", action="store_true", help="Disable adding behavior."
    )

    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only run the first N questions (after --start).",
    )
    p.add_argument(
        "--start", type=int, default=1, help="1-based index of first question to run."
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    llm_provider = args.provider
    basepath = args.basepath
    specialnote = args.specialnote.strip()

    lookup_table, result_log, llm_log = build_paths(basepath, specialnote, llm_provider)

    enable_lookup = False
    enable_adding = False
    if args.enable_lookup:
        enable_lookup = True
    if args.disable_lookup:
        enable_lookup = False
    if args.enable_adding:
        enable_adding = True
    if args.disable_adding:
        enable_adding = False

    file = os.path.join(
        other_config.evaluation_path,
        "content_evaluation",
        "input_list.csv",
    )

    df = pd.read_csv(file)

    # Get Question column as list
    questions = df["Question"].tolist()

    start_idx = max(args.start, 1) - 1
    questions = questions[start_idx:]
    if args.limit is not None:
        questions = questions[: max(args.limit, 0)]

    print("Config:")
    print(f"  provider     : {llm_provider}")
    print(f"  basepath     : {basepath}")
    print(f"  specialnote  : {specialnote!r}")
    print(f"  lookup_table : {lookup_table}")
    print(f"  result_log   : {result_log}")
    print(f"  llm_log      : {llm_log}")
    print(f"  enable_lookup: {enable_lookup}")
    print(f"  enable_adding: {enable_adding}")
    print("")

    for n, question in enumerate(questions, start=start_idx + 1):
        time1 = datetime.now()

        title = utils.random_id()
        print(f"Processing question #{n} | title={title}")

        manager = FileManager(title, result_log, lookup_table, llm_log)

        try:
            parsed_query_info = QueryParser(
                title,
                question,
                llm_provider,
                llm_log,
            )
        except Exception as e:
            print(f"Failed on question #{n}: {e}")
            continue

        _question_parse_dict = parsed_query_info.question_parse

        time2 = datetime.now()
        timea = (time2 - time1).total_seconds()

        print("being saved here")
        print(manager.result_log)

        utils.log_manager_state_to_csv_1(
            manager.result_log,
            manager,
            parsed_query_info,
            timea,
            llm_provider,
        )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
