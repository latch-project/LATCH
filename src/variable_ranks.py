#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import pandas as pd
import utils_extended as utils


REQUIRED_INPUT_COLUMNS = [
    "Parsed Question",
    "Schema Incorportation",
]

OUTPUT_COLUMNS = [
    "Search Keyword",
    "Cycle",
    "Expected Table",
    "Expected Column",
    "Found",
    "Candidate Rank",
    "Matched Variable",
    "Matched Table",
    "Similarity Score",
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Process all CSV files from multiple input folders and save "
            "variable-rank reports into one output folder."
        )
    )

    parser.add_argument(
        "--input-dirs",
        nargs="+",
        required=True,
        type=Path,
        help="Input folders containing CSV files.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Folder where output CSV files will be saved.",
    )

    parser.add_argument(
        "--top-n",
        type=int,
        default=40,
        help="Number of candidates to retrieve. Default: 40.",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for CSV files recursively inside subfolders.",
    )

    return parser.parse_args()


def parse_record(schema_value: object) -> dict:
    if pd.isna(schema_value):
        raise ValueError("Schema Incorportation is missing.")

    if isinstance(schema_value, str):
        record = ast.literal_eval(schema_value)
    else:
        record = schema_value

    if not isinstance(record, dict):
        raise TypeError(
            "Parsed Schema Incorportation value is not a dictionary."
        )

    return record


def find_csv_files(
    input_dirs: list[Path],
    recursive: bool,
) -> list[tuple[Path, Path]]:
    csv_files: list[tuple[Path, Path]] = []

    for input_dir in input_dirs:
        input_dir = input_dir.expanduser().resolve()

        if not input_dir.exists():
            print(
                f"Warning: input folder does not exist: {input_dir}",
                file=sys.stderr,
            )
            continue

        if not input_dir.is_dir():
            print(
                f"Warning: input path is not a folder: {input_dir}",
                file=sys.stderr,
            )
            continue

        pattern = "**/*.csv" if recursive else "*.csv"

        for csv_path in sorted(input_dir.glob(pattern)):
            csv_files.append((input_dir, csv_path))

    return csv_files


def choose_output_path(
    output_dir: Path,
    input_dir: Path,
    input_path: Path,
    used_names: set[str],
) -> Path:
    """
    Preserve the original filename when possible.

    If two input folders contain the same filename, prefix the later file
    with its source folder name to prevent overwriting.
    """
    output_name = input_path.name

    if output_name in used_names or (output_dir / output_name).exists():
        output_name = f"{input_dir.name}_{input_path.name}"

    counter = 2
    candidate_name = output_name

    while candidate_name in used_names or (output_dir / candidate_name).exists():
        candidate_name = (
            f"{Path(output_name).stem}_{counter}{Path(output_name).suffix}"
        )
        counter += 1

    used_names.add(candidate_name)
    return output_dir / candidate_name


def process_csv(
    input_path: Path,
    top_n: int,
) -> pd.DataFrame:
    df = pd.read_csv(
        input_path,
        usecols=REQUIRED_INPUT_COLUMNS,
    )

    if df.empty:
        raise ValueError("CSV file is empty.")

    schema_value = df.iloc[0]["Schema Incorportation"]
    record = parse_record(schema_value)

    candidates_df = utils.retrieve_candidates(
        top_n=top_n,
        record=record,
    )

    rank_report = utils.find_expected_candidate_ranks(
        record=record,
        candidates_df=candidates_df,
    )

    missing_columns = [
        column
        for column in OUTPUT_COLUMNS
        if column not in rank_report.columns
    ]

    if missing_columns:
        raise KeyError(
            "Rank report is missing required columns: "
            + ", ".join(missing_columns)
        )

    return rank_report.loc[:, OUTPUT_COLUMNS].copy()


def main() -> int:
    args = parse_arguments()

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = find_csv_files(
        input_dirs=args.input_dirs,
        recursive=args.recursive,
    )

    if not csv_files:
        print("No CSV files were found.", file=sys.stderr)
        return 1

    used_names: set[str] = set()

    processed = 0
    failed = 0

    print(f"Found {len(csv_files)} CSV file(s).")
    print(f"Output folder: {output_dir}\n")

    for input_dir, input_path in csv_files:
        try:
            rank_report = process_csv(
                input_path=input_path,
                top_n=args.top_n,
            )

            output_path = choose_output_path(
                output_dir=output_dir,
                input_dir=input_dir,
                input_path=input_path,
                used_names=used_names,
            )

            rank_report.to_csv(output_path, index=False)

            print(f"Saved: {output_path}")
            processed += 1

        except Exception as exc:
            print(
                f"Failed: {input_path}\n"
                f"  Reason: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            failed += 1

    print("\nFinished.")
    print(f"Processed: {processed}")
    print(f"Failed:    {failed}")

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
