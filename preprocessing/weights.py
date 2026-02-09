#!/usr/bin/env python3

import os
import json
import argparse
import pandas as pd
import os
import json
import pandas as pd

target_weights = {
    # Dietary
    "dietary_day_one_sample_weight": "dietary_day_one",
    "dietary_day_one_4_year_sample_weight": "dietary_day_one",
    "dietary_two_day_sample_weight": "dietary_day_two",
    # Subsample A
    "subsample_a_weights": "subsample_a",
    "subsample_a_weights_pre_pandemic": "subsample_a",
    # Fasting
    "fasting_subsample_2_year_mec_weight": "fasting",
    "fasting_subsample_weight": "fasting",
    # Environmental
    "environmental_b_2_year_weights": "environmental",
    # Subsample C
    "two_year_mec_weights_of_subsample_c": "subsample_c",
    # VOC
    "voc_subsample_weight": "voc",
    "voc_subsample_weight_pre_pandemic": "voc",
    "voc_subsample_4_yr_mec_weight": "voc",
    # OGTT
    "ogtt_subsample_2_year_mec_weight": "ogtt",
    # Full Sample MEC
    "full_sample_2_year_mec_exam_weight": "full_sample_mec",
    "full_sample_4_year_mec_exam_weight": "full_sample_mec",
    "full_sample_mec_exam_weight": "full_sample_mec",
    # Full Sample Interview
    "full_sample_2_year_interview_weight": "full_sample_interview",
    "full_sample_4_year_interview_weight": "full_sample_interview",
    "full_sample_interview_weight": "full_sample_interview",
    # Smoking
    "two_year_smoking_weights": "smoking",
    # Phlebotomy
    "phlebotomy_2_year_weight": "phlebotomy",
    # Audiometry
    "audiometry_subsample_2_year_mec_weight": "audiometry",
    "audiometry_subsample_4_year_mec_weight": "audiometry",
    # SSMUMP + SSCMV
    "ssmump_and_sscmv_2_year_weights": "ssmump_sscmv",
    "ssmump_and_sscmv_4_year_weights_99_02": "ssmump_sscmv",
    # CIDI
    "cidi_subsample_2_year_mec_weight": "cidi",
    "cidi_subsample_4_year_mec_weight": "cidi",
}

weight_years = {
    "dietary_day_one_sample_weight": 2,
    "dietary_day_one_4_year_sample_weight": 4,
    "dietary_two_day_sample_weight": 2,
    "subsample_a_weights": 2,
    "subsample_a_weights_pre_pandemic": 3.2,
    "fasting_subsample_2_year_mec_weight": 2,
    "fasting_subsample_weight": 3.2,
    "environmental_b_2_year_weights": 2,
    "two_year_mec_weights_of_subsample_c": 2,
    "voc_subsample_weight": 2,
    "voc_subsample_weight_pre_pandemic": 3.2,
    "voc_subsample_4_yr_mec_weight": 4,
    "ogtt_subsample_2_year_mec_weight": 2,
    "full_sample_2_year_mec_exam_weight": 2,
    "full_sample_4_year_mec_exam_weight": 4,
    "full_sample_mec_exam_weight": 3.2,
    "full_sample_2_year_interview_weight": 2,
    "full_sample_4_year_interview_weight": 4,
    "full_sample_interview_weight": 3.2,
    "two_year_smoking_weights": 2,
    "phlebotomy_2_year_weight": 2,
    "audiometry_subsample_2_year_mec_weight": 2,
    "audiometry_subsample_4_year_mec_weight": 4,
    "ssmump_and_sscmv_2_year_weights": 2,
    "ssmump_and_sscmv_4_year_weights_99_02": 4,
    "cidi_subsample_2_year_mec_weight": 2,
    "cidi_subsample_4_year_mec_weight": 4,
}


def apply_weight_table_filter(df):
    deleted_log = []

    def filter_table_names(row):
        col_name = row["Weight Column Name"]
        tables = row["Table Names"]
        kept = []
        deleted = []

        for table in tables:
            remove = False

            # General deletion rule
            if (("_b" in table) or ("_a" in table) or ("_" not in table)) and not (
                "4_year" in col_name or "4_yr" in col_name
            ):
                remove = True

            # Special cases
            if col_name == "dietary_day_one_sample_weight" and any(
                x in table.lower() for x in ["dr2", "ds2"]
            ):
                remove = True

            if col_name == "dietary_two_day_sample_weight" and any(
                x in table.lower() for x in ["dr1", "ds1"]
            ):
                remove = True

            if remove:
                deleted.append(table)
            else:
                kept.append(table)

        if deleted:
            deleted_log.append(
                {"Weight Column Name": col_name, "Deleted Tables": deleted}
            )

        return kept

    # Apply filter
    df = df.copy()
    df["Table Names"] = df.apply(filter_table_names, axis=1)
    df["Table Count"] = df["Table Names"].apply(len)

    return df, deleted_log


import pandas as pd


def extract_exam_lab_tables(csv_path):
    """
    Extracts unique 'data file name' values from NHANES variable codebook
    where the component is 'Examination' or 'Laboratory'.

    Args:
        csv_path (str): Path to the NHANES metadata CSV file.

    Returns:
        List[str]: Sorted list of unique data file names.
    """
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    # Filter for Examination or Laboratory components
    component_mask = df["component"].isin(["Examination", "Laboratory"])

    # Extract unique, sorted data file names
    exam_lab_tables = sorted(df.loc[component_mask, "data file name"].dropna().unique())

    print(
        f"Found {len(exam_lab_tables)} unique data files with 'Examination' or 'Laboratory' components.\n"
    )
    exam_lab_tables = set(t.lower().strip().split(".")[-1] for t in exam_lab_tables)
    return exam_lab_tables


def split_mixed_p_tables(df):
    """
    Splits rows with mixed 'p_' and non-'p_' table names into separate rows.
    Keeps original 'Years Covered' for 'p_' tables, and assigns 3.2 for non-'p_' tables.

    Args:
        df (pd.DataFrame): DataFrame with 'Table Names', 'Weight Column Name',
                           'Weight Group', and 'Years Covered'.

    Returns:
        pd.DataFrame: Expanded DataFrame with mixed tables split into separate rows.
    """
    split_rows = []

    for _, row in df.iterrows():
        tables = row["Table Names"]
        if not tables:
            continue

        # Identify p_ and non-p_ tables properly
        p_tables = [t for t in tables if t.startswith("p_") or ".p_" in t]
        non_p_tables = [t for t in tables if not (t.startswith("p_") or ".p_" in t)]

        if p_tables and non_p_tables:
            # 1. p_ tables: keep original years
            split_rows.append(
                {
                    "Weight Column Name": row["Weight Column Name"],
                    "Table Names": p_tables,
                    "Table Count": len(p_tables),
                    "Weight Group": row["Weight Group"],
                    "Years Covered": row["Years Covered"],
                }
            )

            # 2. non-p_ tables: override years covered to 3.2
            split_rows.append(
                {
                    "Weight Column Name": row["Weight Column Name"],
                    "Table Names": non_p_tables,
                    "Table Count": len(non_p_tables),
                    "Weight Group": row["Weight Group"],
                    "Years Covered": 3.2,
                }
            )
        else:
            # No mix → keep as-is
            split_rows.append(row.to_dict())

    final_weights_df = pd.DataFrame(split_rows)
    final_weights_df.sort_values(
        by=["Weight Column Name", "Years Covered"], inplace=True, ignore_index=True
    )

    excluded_groups = ["full_sample_interview", "full_sample_mec"]

    # 1. Keep everything except the excluded groups
    non_full_sample_df = final_weights_df[
        ~final_weights_df["Weight Group"].isin(excluded_groups)
    ].copy()

    # 2. Create a separate DataFrame for the excluded groups
    full_sample_df = final_weights_df[
        final_weights_df["Weight Group"].isin(excluded_groups)
    ].copy()

    # Sort both (optional)
    non_full_sample_df.sort_values(
        by=["Weight Group", "Weight Column Name"], inplace=True, ignore_index=True
    )
    full_sample_df.sort_values(
        by=["Weight Group", "Weight Column Name"], inplace=True, ignore_index=True
    )
    full_sample_df

    return full_sample_df, non_full_sample_df


def find_weight_columns(folder_path):
    """
    Scans a folder of NHANES-style JSON files to find all column names
    containing '_weight'.

    Args:
        folder_path (str): The path to the folder containing the JSON files.

    Returns:
        pandas.DataFrame: A DataFrame with the table name and the identified
                          weight column name.
    """
    # A list to store our findings
    weights_found = []

    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at '{folder_path}'")
        return pd.DataFrame()

    # Loop through every file in the specified folder
    for filename in os.listdir(folder_path):
        # Process only if it's a JSON file
        if filename.lower().endswith(".json"):
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, "r") as f:
                    # Load the JSON content from the file
                    # The user's JSON is a list containing one dictionary
                    data_list = json.load(f)

                    if not data_list or not isinstance(data_list, list):
                        continue

                    # Get the main dictionary from the list
                    data = data_list[0]

                    table_name = data.get("table")
                    columns = data.get("columns", {})

                    if not table_name:
                        continue

                    # Iterate through all the column names
                    for column_name in columns.keys():
                        # Check if '_weight' is in the column name (case-insensitive)
                        excluded_keywords = [
                            "jack_knife",
                            "consider",
                            "heaviest",
                            "gain",
                            "loss",
                            "mg",
                            "own",
                            "child",
                            "control",
                            "check",
                            "lost",
                            "food",
                            "lose",
                            "pound",
                            "teased",
                            "tried",
                            "trying",
                            "weighting",
                            "reduce",
                        ]
                        if "_weight" in column_name.lower() and not any(
                            keyword in column_name.lower()
                            for keyword in excluded_keywords
                        ):
                            # If it is, add the table and column name to our list
                            weights_found.append(
                                {
                                    "Table Name": table_name,
                                    "Weight Column Name": column_name,
                                }
                            )

            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON from file: {filename}")
            except Exception as e:
                print(f"An error occurred with file {filename}: {e}")

    # Convert the list of findings into a pandas DataFrame for nice printing
    all_weights_df = pd.DataFrame(weights_found)

    all_weights_df.sort_values(
        by=["Table Name", "Weight Column Name"], inplace=True, ignore_index=True
    )

    grouped_weights = (
        all_weights_df.groupby("Weight Column Name")["Table Name"]
        .apply(list)  # List of tables per weight
        .reset_index()
        .rename(columns={"Table Name": "Table Names"})
    )

    # Add a count column to sort by number of tables
    grouped_weights["Table Count"] = grouped_weights["Table Names"].apply(len)

    # Sort by number of tables descending
    grouped_weights = grouped_weights.sort_values(by="Table Count", ascending=False)
    grouped_weights["Table Names"] = grouped_weights["Table Names"].apply(
        lambda table_list: [name.replace("nhanes.", "") for name in table_list]
    )
    filtered_weights = grouped_weights[
        grouped_weights["Weight Column Name"].isin(target_weights.keys())
    ].copy()

    # Map new columns
    filtered_weights["Weight Group"] = filtered_weights["Weight Column Name"].map(
        target_weights
    )
    filtered_weights["Years Covered"] = filtered_weights["Weight Column Name"].map(
        weight_years
    )

    # Sort for clarity
    filtered_weights.sort_values(
        by=["Weight Group", "Years Covered", "Weight Column Name"],
        inplace=True,
        ignore_index=True,
    )

    return filtered_weights


def build_weights(nhanes_path: str):
    """
    Build NHANES weight artifacts:
    - weights/subset_weights.csv
    - weights/exam_tables.json
    """

    # Paths
    schema_dir = os.path.join(nhanes_path, "schema")
    schema_summary_csv = os.path.join(nhanes_path, "metadata", "schema_summary.csv")
    weights_dir = os.path.join(nhanes_path, "weights")

    # Create output directory
    os.makedirs(weights_dir, exist_ok=True)

    # Run pipeline
    filtered_weights = find_weight_columns(schema_dir)
    filtered_weights, deleted_log = apply_weight_table_filter(filtered_weights)
    _, non_full_sample_df = split_mixed_p_tables(filtered_weights)

    exam_lab_tables = extract_exam_lab_tables(schema_summary_csv)
    exam_lab_tables = list(exam_lab_tables)

    # Output paths
    subset_weights_path = os.path.join(weights_dir, "subset_weights.csv")
    exam_tables_path = os.path.join(weights_dir, "exam_tables.json")

    # Save outputs
    non_full_sample_df.to_csv(subset_weights_path, index=False)

    with open(exam_tables_path, "w") as f:
        json.dump(exam_lab_tables, f, indent=4)

    print("✅ Weight artifacts created:")
    print(f" - {subset_weights_path}")
    print(f" - {exam_tables_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Build NHANES weight files (subset_weights.csv, exam_tables.json)"
    )
    parser.add_argument(
        "nhanes_path",
        type=str,
        help="Path to NHANES base directory (e.g. /home/.../data/nhanes)",
    )

    args = parser.parse_args()
    build_weights(args.nhanes_path)


if __name__ == "__main__":
    main()
