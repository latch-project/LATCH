#!/usr/bin/env python3
"""Generate inspectable fictional registry-style CSV tables."""

import argparse
import ast
import csv
import math
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_SUMMARY = PROJECT_ROOT / "data/registry/schema_summary/schema_summary.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "tables"


def load_metadata():
    tables = {}
    with SCHEMA_SUMMARY.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["column_name"] == "patient_id":
                continue
            tables.setdefault(row["table_name"], []).append(
                (row["column_name"], ast.literal_eval(row["values"]))
            )
    return tables


def numeric_values(values):
    try:
        return [float(value) for value in values]
    except (TypeError, ValueError):
        return None


def generic_value(rng, values):
    numbers = numeric_values(values)
    if numbers is None:
        return rng.choice(values)
    return round(rng.uniform(min(numbers), max(numbers)), 2)


def patient_values(index, rng):
    age = rng.randint(21, 90)
    diabetes_type = rng.choices(
        ["Type 2", "Type 1", "Gestational", "Other"], weights=[75, 17, 3, 5]
    )[0]
    insulin_probability = 0.55 if diabetes_type == "Type 2" else 0.75
    insulin = "Yes" if rng.random() < insulin_probability else "No"
    hdl = round(max(20, min(90, rng.gauss(47, 13))), 1)
    systolic = round(max(90, min(190, rng.gauss(128 + (age - 50) * 0.35, 17))), 1)
    duration = round(max(0.2, min(age - 1, rng.gauss(10 + (age - 50) * 0.12, 7))), 1)
    risk_logit = -2.2 + 0.035 * (age - 50) + 0.055 * (50 - hdl) + 0.035 * duration
    risk = 1 / (1 + math.exp(-risk_logit))
    return {
        "patient_id": f"SYN-DM-{index:05d}",
        "age": age,
        "sex_at_birth": rng.choice(["Female", "Male", "Intersex", "Unknown"]),
        "race_group": rng.choice(["Asian", "Black", "White", "Other", "Unknown"]),
        "insurance_type": rng.choices(
            ["Commercial", "Medicare", "Medicaid", "Self-pay"], weights=[52, 27, 16, 5]
        )[0],
        "smoking_status": rng.choices(
            ["Never", "Former", "Current", "Unknown"], weights=[50, 29, 16, 5]
        )[0],
        "diabetes_type": diabetes_type,
        "diabetes_duration_years": duration,
        "insulin_use_status": insulin,
        "hdl_cholesterol_mg_dl": hdl,
        "systolic_blood_pressure_mm_hg": systolic,
        "microaneurysm_status": "Present" if rng.random() < risk else "Absent",
    }


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2001)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.rows < 100:
        raise SystemExit("--rows must be at least 100 so the example model is estimable.")

    rng = random.Random(args.seed)
    tables = load_metadata()
    patients = [patient_values(index, rng) for index in range(1, args.rows + 1)]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for table_name, columns in tables.items():
        path = args.output_dir / f"{table_name}.csv"
        names = ["patient_id"] + [name for name, _ in columns]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=names)
            writer.writeheader()
            for patient in patients:
                row = {"patient_id": patient["patient_id"]}
                for name, values in columns:
                    row[name] = patient.get(name, generic_value(rng, values))
                writer.writerow(row)

    print(
        f"Generated {len(tables)} fictional registry-style CSV tables with "
        f"{args.rows} participants in {args.output_dir}."
    )


if __name__ == "__main__":
    main()
