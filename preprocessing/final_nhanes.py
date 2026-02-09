#!/usr/bin/env python3
import argparse
from pathlib import Path

import data_prep


def main():
    parser = argparse.ArgumentParser(
        description="Run NHANES ETL pipeline end-to-end (schema fixed to 'nhanes')."
    )
    parser.add_argument(
        "--datafolder",
        required=True,
        help="Base folder to store intermediate and final outputs",
    )
    args = parser.parse_args()

    datafolder = str(Path(args.datafolder).expanduser().resolve())
    schema_name = "nhanes"  # fixed

    print(f"datafolder: {datafolder}")
    print(f"schema_name: {schema_name}")

    # 15 mins: metadata
    data_prep.metadata_process(datafolder)

    # 30 mins: download NHANES data
    data_prep.download_nhanes_data(datafolder)

    # 10 mins: convert XPT -> CSV
    data_prep.convert_xpt_to_csv(datafolder)

    # mortality processing
    data_prep.mortality_data_process(datafolder)

    # load CSVs into Postgres (your comment says ~20 min)
    data_prep.csv_to_psql(datafolder, schema_name)

    # schema steps
    data_prep.create_schema(datafolder, schema_name)
    data_prep.update_schema_mortality(datafolder)
    data_prep.final_schema(datafolder)

    print("NHANES pipeline completed successfully.")


if __name__ == "__main__":
    main()
