#!/usr/bin/env python3
import subprocess
import sys
import argparse
from pathlib import Path

RETINAL_THICKNESS_REL = Path("formatted_dataset") / "retinal_layer_thickness.csv"


def run_command(command, description):
    print(f"\n--- Running: {description} ---")
    print(f"Command: {' '.join(map(str, command))}")
    try:
        subprocess.run(list(map(str, command)), check=True)
        print(f"--- Success: {description} ---")
    except subprocess.CalledProcessError:
        print(f"--- FAILED: {description} ---")
        sys.exit(1)


def is_dir_missing_or_empty(p: Path) -> bool:
    return (
        (not p.exists())
        or (not p.is_dir())
        or (not any(f for f in p.iterdir() if f.name != ".gitignore"))
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run full LATCH Diabetes preprocessing pipeline."
    )
    parser.add_argument(
        "--aireadi-dir", required=True, help="Base directory for AI-READI data"
    )
    parser.add_argument(
        "--nhanes-dir", required=True, help="Base directory for NHANES data"
    )
    parser.add_argument(
        "--schema", default="aireadi", help="Postgres schema name for AI-READI"
    )
    args = parser.parse_args()

    aireadi_dir = Path(args.aireadi_dir).resolve()
    nhanes_dir = Path(args.nhanes_dir).resolve()

    script_dir = Path(__file__).parent

    # =========================
    # 1) NHANES FIRST
    # =========================
    nhanes_converted_dir = nhanes_dir / "converted_tables"

    if nhanes_converted_dir.exists():
        csv_files = list(nhanes_converted_dir.rglob("*.csv"))
        if csv_files:
            print(
                f"\n--- Skipping NHANES: CSV files already exist in {nhanes_converted_dir} ---"
            )
        else:
            run_command(
                [
                    sys.executable,
                    script_dir / "final_nhanes.py",
                    "--datafolder",
                    nhanes_dir,
                ],
                "NHANES Full Pipeline",
            )
    else:
        run_command(
            [
                sys.executable,
                script_dir / "final_nhanes.py",
                "--datafolder",
                nhanes_dir,
            ],
            "NHANES Full Pipeline",
        )

    nhanes_weights_dir = nhanes_dir / "weights"

    csv_files = (
        list(nhanes_weights_dir.rglob("*.csv"))
        if nhanes_weights_dir.exists()
        else []
    )

    if csv_files:
        print(
            f"\n--- Skipping NHANES Weights: CSV files already exist in {nhanes_weights_dir} ---"
        )
    else:
        run_command(
            [sys.executable, script_dir / "weights.py", nhanes_dir],
            "NHANES Weights Generation",
        )

    # =========================
    # 2) AI-READI (conditional)
    # =========================
    aireadi_dataset_dir = aireadi_dir / "dataset"
    if is_dir_missing_or_empty(aireadi_dataset_dir):
        print("\n--- Skipping AI-READI: aireadi/dataset folder is missing or empty ---")
    else:
        # Skip segmentation if thickness file already exists
        thickness_file = aireadi_dir / RETINAL_THICKNESS_REL
        if thickness_file.exists():
            print(
                f"\n--- Skipping AI-READI Segmentation: already found {thickness_file} ---"
            )
        else:
            run_command(
                [
                    sys.executable,
                    script_dir / "process_segmentation.py",
                    "--base-dir",
                    aireadi_dir,
                ],
                "AI-READI Segmentation Processing",
            )

        # Continue AI-READI conversion + post-conversion
        formatted_dir = aireadi_dir / "formatted_dataset"
        expected_files = [
            "person.csv",
            "condition_occurrence.csv",
            "measurement.csv",
            "observation.csv",
            "participants.csv",
            "retinal_layer_thickness.csv",
        ]
        files_exist = all((formatted_dir / f).exists() for f in expected_files)

        if files_exist:
            print(
                f"\n--- Skipping AI-READI Conversion: all formatted files already exist in {formatted_dir} ---"
            )
        else:
            run_command(
                [
                    sys.executable,
                    script_dir / "convert_aireadi.py",
                    "--root-folder",
                    aireadi_dir,
                ],
                "AI-READI Conversion",
            )

        run_command(
            [
                sys.executable,
                script_dir / "post_conversion.py",
                aireadi_dir,
                "--schema-name",
                args.schema,
            ],
            "AI-READI Post-Conversion (DB Upload & Schema)",
        )

    print("\n" + "=" * 40)
    print("ALL PREPROCESSING STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 40)


if __name__ == "__main__":
    main()
