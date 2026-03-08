import pandas as pd
import nhanes_process as n
from tqdm import tqdm
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import convert_utils
import ast
import numpy as np
from sqlalchemy import create_engine, text
import json
import data_prep
from pathlib import Path
import urllib.request
import json


def create_project_subfolders(base_folder):
    """
    Creates required subfolders in the given base folder.

    Subfolders:
        - conversion_log
        - converted_tables
        - metadata
        - schema
        - tables

    Parameters:
        base_folder (str): The path to the base directory where subfolders will be created.
    """
    subfolders = ["conversion_log", "converted_tables", "metadata", "schema", "tables"]

    for subfolder in subfolders:
        path = os.path.join(base_folder, subfolder)
        os.makedirs(path, exist_ok=True)
        print(f"Created or already exists: {path}")


def download_metatdata(datafolder):
    categories = [
        "Demographics",
        "Dietary",
        "Examination",
        "Laboratory",
        "Questionnaire",
    ]
    metadatapath = f"{datafolder}/metadata"
    for key in categories:
        df = n.get_all_variables(key)
        df.to_csv(f"{metadatapath}/{key}_variables.csv", index=False)

    keywords = ["Demographics", "Dietary", "Examination", "Laboratory", "Questionnaire"]

    for key in keywords:
        var_path = f"{metadatapath}/{key}_variables.csv"

        try:
            df = pd.read_csv(var_path)

            before = len(df)
            df = df.drop_duplicates()
            after = len(df)
            print("")

            # print(f"{key}: {before} rows → {after} rows after dropping duplicates.")

            # Optionally save cleaned file (overwrite original)
            df.to_csv(var_path, index=False)
        except Exception as e:
            print("")
            # print(f"Error processing {key}: {e}")


def clean_html_formatting(text):
    """
    Removes HTML-style formatting characters like \r, \n, \t and excessive whitespace.
    """
    if not isinstance(text, str):
        return text  # leave non-strings untouched

    # Replace \r, \n, \t with a single space
    text = re.sub(r"[\r\n\t]+", " ", text)
    # Collapse multiple spaces into one
    text = re.sub(r"\s{2,}", " ", text)
    # Trim leading/trailing spaces
    return text.strip()


def get_codebook_with_error_handling(codebookurl, metadatapath):
    """
    Retrieves a codebook from a URL, handling potential errors.

    Args:
        codebookurl (str): The URL of the codebook.
        metadatapath (str): Path to the metadata directory where the error log will be saved.

    Returns:
        dict or None: The codebook, or None if an error occurred.
    """

    os.makedirs(metadatapath, exist_ok=True)

    error_file = os.path.join(metadatapath, "codebook_error.txt")
    with open(error_file, "w") as f:
        pass

    try:
        codebook = n.nhanes_codebook_from_url(codebookurl)
        return codebook
    except Exception as e:
        with open(error_file, "a") as f:
            f.write(f"Error retrieving codebook from {codebookurl}: {e}\n")
        print("")
        # print(f"Error retrieving codebook from {codebookurl}: {e}")
        return None


def process_codebooks_and_save(df, keyword, metadatapath):
    """
    Processes codebooks from a DataFrame and saves the combined data to a CSV.

    Args:
        df (pd.DataFrame): DataFrame containing file information.
        keyword (str): Keyword for the output CSV file name.
    """
    all_codebook_data = []

    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        file_name = row["Data File Name"]
        year = row["Begin Year"]

        codebookurl = f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{file_name}.htm"
        codebook = get_codebook_with_error_handling(codebookurl, metadatapath)

        if codebook:
            keys = list(codebook.keys())

            rows = []

            for key in keys:
                entry = codebook[key]
                row_data = {
                    "Variable": key,
                    "Data File Name": file_name,
                    "Begin Year": year,
                    "Variable Name": clean_html_formatting(
                        entry.get("Variable Name:", "")
                    ),
                    "SAS Label": clean_html_formatting(entry.get("SAS Label:", "")),
                    "English Text": clean_html_formatting(
                        entry.get("English Text:", "")
                    ),
                    "Target": clean_html_formatting(entry.get("Target:", "")),
                    "Values": clean_html_formatting(entry.get("values", "")),
                }
                rows.append(row_data)

            codebook_df = pd.DataFrame(rows)

            all_codebook_data.append(codebook_df)
        else:
            continue

    if all_codebook_data:
        final_df = pd.concat(all_codebook_data, ignore_index=True)
        final_df.to_csv(f"{metadatapath}/{keyword}_codebook.csv", index=False)
        print(f"Codebook data saved to ./{keyword}_codebook.csv")
    else:
        print("No codebook data was successfully processed.")


def download_codebooks(datafolder):
    metadatapath = f"{datafolder}/metadata"
    keywords = ["Demographics", "Dietary", "Examination", "Laboratory", "Questionnaire"]

    for keyword in keywords:
        df = pd.read_csv(f"{metadatapath}/{keyword}_variables.csv")
        df = n.get_unique_file_year_combinations(df)
        process_codebooks_and_save(df, keyword, metadatapath)

    for key in keywords:
        var_path = f"{metadatapath}/{key}_codebook.csv"

        try:
            df = pd.read_csv(var_path)

            before = len(df)
            df = df.drop_duplicates()
            after = len(df)

            print(f"{key}: {before} rows → {after} rows after dropping duplicates.")

            df.to_csv(var_path, index=False)
        except Exception as e:
            print("")
            # print(f"Error processing {key}: {e}")


def merge_metadata(datafolder):
    metadatapath = f"{datafolder}/metadata"
    keywords = ["Demographics", "Dietary", "Examination", "Laboratory", "Questionnaire"]

    for keyword in keywords:
        var_path = f"{metadatapath}/{keyword}_variables.csv"
        codebook_path = f"{metadatapath}/{keyword}_codebook.csv"
        output_path = f"{metadatapath}/{keyword}_combined_variable_codebook.csv"

        try:
            df_vars = pd.read_csv(var_path)
            df_codebook = pd.read_csv(codebook_path)

            merge_cols = ["Variable Name", "Data File Name", "Begin Year"]
            df_combined = pd.merge(df_vars, df_codebook, on=merge_cols, how="left")

            df_combined.to_csv(output_path, index=False)
            print(f"Merged and saved: {output_path}")

        except Exception as e:
            print("")
            # print(f"Failed for {keyword}: {e}")

    merged_files = [
        f"{metadatapath}/{k}_combined_variable_codebook.csv" for k in keywords
    ]

    all_dfs = []

    for file in merged_files:
        try:
            df = pd.read_csv(file)
            all_dfs.append(df)
        except Exception as e:
            print("")
            # print(f"Failed to read {file}: {e}")

    if all_dfs:
        df_all = pd.concat(all_dfs, ignore_index=True)
        df_all.to_csv(
            f"{metadatapath}/ALL_combined_variable_codebook_all.csv", index=False
        )
        print(
            "All files successfully combined and saved to data/ALL_combined_variable_codebook_all.csv"
        )
    else:
        print("No files were loaded.")


def variable_name_clean(datafolder):
    metadatapath = f"{datafolder}/metadata"
    df = pd.read_csv(f"{metadatapath}/ALL_combined_variable_codebook_all.csv")
    df["Variable Name"] = df["Variable Name"].str.upper()
    df["SAS Label"] = df["SAS Label"].fillna("").str.strip().str.lower()
    label_variants = (
        df.groupby("Variable Name")["SAS Label"]
        .nunique()
        .reset_index()
        .rename(columns={"SAS Label": "Unique SAS Label Count"})
    )

    variant_vars = label_variants[label_variants["Unique SAS Label Count"] > 1]

    variant_details = df[df["Variable Name"].isin(variant_vars["Variable Name"])]

    variant_details_sorted = variant_details.sort_values(
        ["Variable Name", "Begin Year"]
    )

    priority_cols = [
        "Variable Name",
        "SAS Label",
        "Data File Name",
        "Begin Year",
        "EndYear",
    ]
    other_cols = [
        col for col in variant_details_sorted.columns if col not in priority_cols
    ]

    final_cols = priority_cols + other_cols

    variant_details_sorted.to_csv(
        f"{metadatapath}/variable_label_variants.csv",
        columns=final_cols,
        index=False,
    )
    print(
        "Number of unique Variable Names with multiple SAS Labels:",
        variant_details_sorted["Variable Name"].nunique(),
    )


def process_sas_labels(datafolder):
    csv_path = f"{datafolder}/metadata/ALL_combined_variable_codebook_all.csv"
    df = pd.read_csv(csv_path)
    df["Variable Name"] = df["Variable Name"].str.upper()
    df["SAS Label"] = df["SAS Label"].fillna("").str.strip().str.lower()

    label_variants = (
        df.groupby("Variable Name")["SAS Label"]
        .nunique()
        .reset_index()
        .rename(columns={"SAS Label": "Unique SAS Label Count"})
    )
    variant_vars = label_variants[label_variants["Unique SAS Label Count"] > 1]

    variant_details = df[df["Variable Name"].isin(variant_vars["Variable Name"])]

    harmonization_dict = {}
    for var_name, group in variant_details.groupby("Variable Name"):
        label_counts = group["SAS Label"].value_counts()
        top_labels = label_counts[label_counts == label_counts.max()].index.tolist()
        harmonized_label = sorted(top_labels)[0]
        harmonization_dict[var_name] = harmonized_label

    harmonized_dict = {}
    change_log = {}

    for var_name, group in df.groupby("Variable Name"):
        labels = group["SAS Label"].unique().tolist()

        if var_name in harmonization_dict:
            harmonized_label = harmonization_dict[var_name]
            harmonized_dict[var_name] = harmonized_label

            changed = [
                (label, harmonized_label)
                for label in labels
                if label != harmonized_label
            ]
            if changed:
                change_log[var_name] = changed
        else:
            # No conflict, keep original (assumes one label)
            harmonized_dict[var_name] = labels[0] if labels else ""

    # Save both as CSV in same folder
    base_dir = os.path.dirname(csv_path)

    pd.DataFrame(
        list(harmonized_dict.items()), columns=["Variable Name", "Harmonized SAS Label"]
    ).to_csv(os.path.join(base_dir, "harmonized_sas_labels.csv"), index=False)

    change_records = []
    for var, changes in change_log.items():
        for original, new in changes:
            change_records.append(
                {
                    "Variable Name": var,
                    "Original SAS Label": original,
                    "Harmonized SAS Label": new,
                }
            )

    pd.DataFrame(change_records).to_csv(
        os.path.join(base_dir, "sas_label_change_log.csv"), index=False
    )

    return harmonized_dict, change_log


def final_codebook(datafolder):
    metadatapath = f"{datafolder}/metadata"
    # Paths
    original_codebook_path = f"{metadatapath}/ALL_combined_variable_codebook_all.csv"
    harmonized_labels_path = f"{metadatapath}/harmonized_sas_labels.csv"
    output_path = f"{metadatapath}/ALL_combined_variable_codebook_all_harmonized.csv"

    # Load original codebook
    codebook_df = pd.read_csv(original_codebook_path)

    # Normalize Variable Name for matching
    codebook_df["Variable Name"] = codebook_df["Variable Name"].str.upper()

    # Load harmonized SAS Labels
    harmonized_df = pd.read_csv(harmonized_labels_path)
    harmonized_df["Variable Name"] = harmonized_df["Variable Name"].str.upper()
    harmonized_df["Harmonized SAS Label"] = (
        harmonized_df["Harmonized SAS Label"].str.lower().str.strip()
    )

    # Merge to get harmonized labels
    codebook_df = codebook_df.merge(harmonized_df, on="Variable Name", how="left")

    # Replace SAS Label with harmonized one if available
    codebook_df["SAS Label"] = codebook_df["Harmonized SAS Label"].combine_first(
        codebook_df["SAS Label"].fillna("").str.strip().str.lower()
    )

    # Drop temporary column
    codebook_df.drop(columns=["Harmonized SAS Label"], inplace=True)

    # Save the updated codebook
    codebook_df.to_csv(output_path, index=False)

    print("Updated codebook with harmonized SAS Labels saved to:", output_path)


def double_check_variable_names(datafolder):
    metadatapath = f"{datafolder}/metadata"

    # Load the NHANES metadata
    df = pd.read_csv(
        f"{metadatapath}/ALL_combined_variable_codebook_all_harmonized.csv"
    )

    # Normalize case for consistency
    df["Variable Name"] = df["Variable Name"].str.upper()
    df["SAS Label"] = df["SAS Label"].fillna("").str.strip().str.lower()

    # Find variable names with >1 unique SAS Label
    label_variants = (
        df.groupby("Variable Name")["SAS Label"]
        .nunique()
        .reset_index()
        .rename(columns={"SAS Label": "Unique SAS Label Count"})
    )

    # Keep only those with multiple label versions
    variant_vars = label_variants[label_variants["Unique SAS Label Count"] > 1]

    # Get full metadata rows for those variable names
    variant_details = df[df["Variable Name"].isin(variant_vars["Variable Name"])]

    # Sort by Variable Name, then Begin Year
    variant_details_sorted = variant_details.sort_values(
        ["Variable Name", "Begin Year"]
    )
    print(
        "Number of unique Variable Names with multiple SAS Labels:",
        variant_details_sorted["Variable Name"].nunique(),
    )


def metadata_process(datafolder):
    """
    Main function to process NHANES metadata.
    It creates subfolders, downloads metadata, codebooks, merges them,
    cleans variable names, and processes SAS labels.
    """
    create_project_subfolders(datafolder)
    download_metatdata(datafolder)
    download_codebooks(datafolder)
    merge_metadata(datafolder)
    variable_name_clean(datafolder)
    process_sas_labels(datafolder)
    final_codebook(datafolder)
    double_check_variable_names(datafolder)


def count_xpt_files(url):
    """Counts the number of .XPT files on an NHANES data page."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        soup = BeautifulSoup(response.content, "html.parser")

        # Find all anchor tags (links) on the page.
        links = soup.find_all("a")

        xpt_count = 0
        for link in links:
            href = link.get("href")
            if href and href.lower().endswith(".xpt"):
                xpt_count += 1

        return xpt_count

    except requests.exceptions.RequestException as e:
        print("")
        # print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print("")
        # print(f"An unexpected error occurred: {e}")
        return None


def download_xpt_files(url, datapath, keyword):
    """Downloads all .XPT files from a given NHANES data page."""
    output_dir = f"{datapath}/{keyword}"

    with open("./nhanes_file_list.json") as f:
        files_by_category = json.load(f)

    try:
        os.makedirs(output_dir, exist_ok=True)

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")

        xpt_links = [
            link.get("href")
            for link in links
            if link.get("href") and link.get("href").lower().endswith(".xpt")
        ]

        xpt_links = [
            href
            for href in xpt_links
            if os.path.basename(href).upper() in files_by_category[keyword]
        ]

        if not xpt_links:
            print("No .XPT files found.")
            return

        print(f"Found {len(xpt_links)} .XPT files. Starting download...")

        for href in xpt_links:
            full_url = urljoin(url, href)
            file_name = os.path.basename(href)

            try:
                file_path = os.path.join(output_dir, file_name)
                with requests.get(full_url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                print(f"Downloaded: {file_name}")
            except Exception as e:
                print("")
                # print(f"Failed to download {file_name}: {e}")

    except requests.exceptions.RequestException as e:
        print("")
        # print(f"Error fetching URL: {e}")
    except Exception as e:
        print("")
        # print(f"An unexpected error occurred: {e}")


def download_nhanes_data(datapath):
    nhansedatapath = f"{datapath}/tables"
    for keyword in [
        "Demographics",
        "Dietary",
        "Examination",
        "Laboratory",
        "Questionnaire",
    ]:
        url = (
            f"https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component={keyword}"
        )
        download_xpt_files(url, nhansedatapath, keyword)


def compare_folders(folder1, folder2):
    files1 = set(os.listdir(folder1))
    files2 = set(os.listdir(folder2))

    common_files = files1 & files2
    only_in_folder1 = files1 - files2
    only_in_folder2 = files2 - files1

    return {
        "common": list(common_files),
        "only_in_folder1": list(only_in_folder1),
        "only_in_folder2": list(only_in_folder2),
    }


def are_csvs_equal(file1, file2):
    """
    Compares two CSV files to check if they are exactly the same
    in content, including headers and row order.

    Parameters:
        file1 (str): Path to the first CSV file.
        file2 (str): Path to the second CSV file.

    Returns:
        bool: True if files are equal, False otherwise.
    """
    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except Exception as e:
        print("")
        # print(f"Error reading files: {e}")
        return False

    return df1.equals(df2)


def convert_xpt_to_csv(datafolder):
    # Process first 4 categories
    keywords = ["Demographics", "Dietary", "Questionnaire", "Laboratory"]

    # Path to dictionary
    dictionary_path = (
        f"{datafolder}/metadata/ALL_combined_variable_codebook_all_harmonized.csv"
    )

    # Track failures
    failed_files = []

    for keyword in keywords:
        print(f"\nProcessing category: {keyword}")

        # Define paths
        folder_path = f"{datafolder}/tables/{keyword}"
        output_folder = f"{datafolder}/converted_tables/{keyword}"
        log_folder = f"{datafolder}/conversion_log/{keyword}"

        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(log_folder, exist_ok=True)

        # List files
        input_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        # Convert each file
        for file_path in tqdm(input_files, desc=f"Converting files in {keyword}"):
            try:
                convert_utils.convert(
                    file_path, output_folder, log_folder, dictionary_path
                )
            except Exception as e:
                print("")
                # print(f"Failed: {os.path.basename(file_path)} — {str(e)}")
                failed_files.append(os.path.basename(file_path))

    for keyword in ["Examination"]:
        print(f"\nProcessing category: {keyword}")

        # Define paths
        folder_path = f"{datafolder}/tables/{keyword}"
        output_folder = f"{datafolder}/converted_tables/{keyword}"
        log_folder = f"{datafolder}/conversion_log/{keyword}"

        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(log_folder, exist_ok=True)

    input_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Skip files at indices 55 and 96
    excluded_filenames = {"PAXMIN_H.xpt", "PAXMIN_G.xpt"}

    # Create a new list excluding the specified indices
    processed_input_files = [
        f for f in input_files if os.path.basename(f) not in excluded_filenames
    ]

    # Now you can use processed_input_files instead of input_files
    print(f"Total files after exclusion: {len(processed_input_files)}")

    for file_path in tqdm(processed_input_files, desc=f"Converting files in {keyword}"):
        try:
            convert_utils.convert(file_path, output_folder, log_folder, dictionary_path)
        except Exception as e:
            print("")
            # print(f"Failed: {os.path.basename(file_path)} — {str(e)}")
            failed_files.append(os.path.basename(file_path))


import os


def rename_mortality_file(base_name):
    mapping = {
        "1999": "mortality_data",
        "2001": "mortality_data_b",
        "2003": "mortality_data_c",
        "2005": "mortality_data_d",
        "2007": "mortality_data_e",
        "2009": "mortality_data_f",
        "2011": "mortality_data_g",
        "2013": "mortality_data_h",
        "2015": "mortality_data_i",
        "2017": "mortality_data_j",
    }

    for years, new_name in mapping.items():
        if years in base_name:
            new_filename = f"{new_name}.csv"
            print(f"Renamed '{base_name}' to '{new_filename}'")
            return new_filename  # just the new base name

    print("No matching year range found.")
    return None


import os
import pandas as pd


def add_mortality_data(mortalityfolder, datafolder):
    # Define the directory containing the .dat files
    mortality_dir = mortalityfolder

    # Define fixed-width column specs and column names
    colspecs = [
        (0, 6),  # SEQN (1-6)
        (14, 15),  # eligstat (15)
        (15, 16),  # mortstat (16)
        (16, 19),  # ucod_leading (17-19)
        (19, 20),  # diabetes (20)
        (20, 21),  # hyperten (21)
        (42, 45),  # permth_int (43-45)
        (45, 48),  # permth_exm (46-48)
    ]

    column_names = [
        "SEQN",
        "eligstat",
        "mortstat",
        "ucod_leading",
        "diabetes",
        "hyperten",
        "permth_int",
        "permth_exm",
    ]

    # Define rename map to make column names more intuitive
    column_rename_map = {
        "SEQN": "respondent_sequence_number",
        "eligstat": "eligibility_status",
        "mortstat": "mortality_status",
        "ucod_leading": "cause_of_death_code",
        "diabetes": "diabetes_related_death",
        "hyperten": "hypertension_related_death",
        "permth_int": "months_followup_interview",
        "permth_exm": "months_followup_examination",
    }

    # List all .dat files in the directory
    dat_files = [f for f in os.listdir(mortality_dir) if f.endswith(".dat")]

    # Read and merge all .dat files
    df_list = []
    for file in dat_files:
        path = os.path.join(mortality_dir, file)
        df = pd.read_fwf(
            path, colspecs=colspecs, names=column_names, na_values=["", "."]
        )
        df = df.rename(columns=column_rename_map)
        df["source_file"] = file  # Optional: track the origin file

        eligstat_map = {1: "Eligible", 2: "Under age 18, not public", 3: "Ineligible"}

        ucod_leading_map = {
            1: "Heart disease",
            2: "Cancer",
            3: "Respiratory diseases",
            4: "Accidents",
            5: "Cerebrovascular diseases",
            6: "Alzheimers disease",
            7: "Diabetes mellitus",
            8: "Influenza and pneumonia",
            9: "Kidney diseases",
            10: "All other causes",
        }

        # Apply the mappings to your DataFrame
        df["eligibility_status"] = df["eligibility_status"].map(eligstat_map)
        df["cause_of_death_code"] = df["cause_of_death_code"].map(ucod_leading_map)

        dir_path = f"{datafolder}/converted_tables/Mortality"

        filename = rename_mortality_file(file)

        file_path = os.path.join(dir_path, filename)

        # Create the directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)

        # Save the DataFrame
        df.to_csv(file_path, index=False)

        print(f"File saved to: {file_path}")


BASE_URL = (
    "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/"
)

mortality_files = [
    "NHANES_1999_2000_MORT_2019_PUBLIC.dat",
    "NHANES_2001_2002_MORT_2019_PUBLIC.dat",
    "NHANES_2003_2004_MORT_2019_PUBLIC.dat",
    "NHANES_2005_2006_MORT_2019_PUBLIC.dat",
    "NHANES_2007_2008_MORT_2019_PUBLIC.dat",
    "NHANES_2009_2010_MORT_2019_PUBLIC.dat",
    "NHANES_2011_2012_MORT_2019_PUBLIC.dat",
    "NHANES_2013_2014_MORT_2019_PUBLIC.dat",
    "NHANES_2015_2016_MORT_2019_PUBLIC.dat",
    "NHANES_2017_2018_MORT_2019_PUBLIC.dat",
]


def download(url: str, dest: Path):
    if dest.exists() and dest.stat().st_size > 0:
        print(f"Skipping (already exists): {dest.name}")
        return

    print(f"Downloading {dest.name}...")
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1024 * 1024)  # 1 MB
            if not chunk:
                break
            f.write(chunk)

    print(f"Done: {dest.name} ({dest.stat().st_size:,} bytes)")


def mortality_data_process(datafolder):
    # Create Mortality subfolder
    mortality_dir = Path(datafolder) / "tables" / "Mortality"
    mortality_dir.mkdir(parents=True, exist_ok=True)

    # Download all files
    for fname in mortality_files:
        download(BASE_URL + fname, mortality_dir / fname)

    print("\nAll mortality files saved to:")
    print(mortality_dir)

    # add mortality data to converted tables
    mortality_dir = f"{datafolder}/tables/Mortality"
    add_mortality_data(mortality_dir, datafolder)


column_rename_map = {
    "SEQN": "respondent_sequence_number",
    "eligstat": "eligibility_status",
    "mortstat": "mortality_status",
    "ucod_leading": "cause_of_death_code",
    "diabetes": "diabetes_related_death",
    "hyperten": "hypertension_related_death",
    "permth_int": "months_followup_interview",
    "permth_exm": "months_followup_examination",
}
mapping = {
    "1999-2000": "mortality_data",
    "2001-2002": "mortality_data_b",
    "2003-2004": "mortality_data_c",
    "2005-2006": "mortality_data_d",
    "2007-2008": "mortality_data_e",
    "2009-2010": "mortality_data_f",
    "2011-2012": "mortality_data_g",
    "2013-2014": "mortality_data_h",
    "2015-2016": "mortality_data_i",
    "2017-2018": "mortality_data_j",
}


reverse_map = {v: k for k, v in column_rename_map.items()}
reverse_map_years = {v: k for k, v in mapping.items()}


def generate_metadata(table_name, column_names, df, reverse_map, reverse_map_years):
    metadata_list = []

    # Get file name part after the dot
    data_file_name = table_name.split(".")[-1]

    # Get year range and split it
    year_range = reverse_map_years.get(data_file_name, "")
    start_year, end_year = (
        map(int, year_range.split("-")) if year_range else (None, None)
    )

    for col_name in column_names:
        # Get matching values for the column
        matching_row = df[df["column"] == col_name]
        if matching_row.empty:
            continue
        matching_values = matching_row["values"].iloc[0]

        # Get abbreviation
        var_abbr = reverse_map.get(col_name, "")

        # Construct metadata dictionary
        metadata = {
            "Variable Name": var_abbr,
            "Variable Description": col_name,
            "Data File Name": data_file_name,
            "Data File Description": "mortality data",
            "Begin Year": start_year,
            "EndYear": end_year,
            "Component": "Mortality",
            "Use Constraints": "No",
            "Variable": col_name,
            "SAS Label": col_name,
            "English Text": col_name,
            "Target": None,
            "Values": matching_values,
        }

        metadata_list.append(metadata)

    return metadata_list


def update_schema_mortality(datafolder):
    # File list
    mortality_schema_files = [
        f"{datafolder}/schema/mortality_data.json",
        f"{datafolder}/schema/mortality_data_b.json",
        f"{datafolder}/schema/mortality_data_c.json",
        f"{datafolder}/schema/mortality_data_d.json",
        f"{datafolder}/schema/mortality_data_e.json",
        f"{datafolder}/schema/mortality_data_f.json",
        f"{datafolder}/schema/mortality_data_g.json",
        f"{datafolder}/schema/mortality_data_h.json",
        f"{datafolder}/schema/mortality_data_i.json",
        f"{datafolder}/schema/mortality_data_j.json",
    ]
    all_metadata = []

    for file_path in mortality_schema_files:
        with open(file_path, "r") as f:
            json_data = json.load(f)

        parsed_rows = []
        for table_entry in json_data:
            table_name = table_entry["table"]  # save the table name for metadata
            for column_name, column_info in table_entry["columns"].items():
                sample_values = column_info.get("sample_values", [])
                parsed_rows.append(
                    {
                        "table": table_name,
                        "column": column_name,
                        "values": sample_values,
                    }
                )

        df = pd.DataFrame(parsed_rows)
        filtered_df = df[df["column"] != "source_file"]
        column_names = filtered_df["column"].tolist()

        metadata_output = generate_metadata(
            table_name, column_names, df, reverse_map, reverse_map_years
        )
        metadata_df = pd.DataFrame(metadata_output)
        metadata_df.loc[
            metadata_df["Variable Description"] == "eligibility_status",
            "Variable Description",
        ] = "tracking mortality eligibility status"

        all_metadata.extend(metadata_df.to_dict(orient="records"))

    # Final merge
    metadata_dff = pd.DataFrame(all_metadata)

    codebook_df = pd.read_csv(
        f"{datafolder}/metadata/ALL_combined_variable_codebook_all_harmonized.csv"
    )

    # Concatenate the existing metadata_dff with the new data
    combined_df = pd.concat([metadata_dff, codebook_df], ignore_index=True)

    # View or save
    # combined_df
    combined_df.to_csv(
        f"{datafolder}/metadata/ALL_combined_variable_codebook_all_harmonized_mortality_added.csv",
        index=False,
    )


def final_schema(datafolder):
    # Get list of base file names (without .json) in lower case
    folder = f"{datafolder}/schema"
    base_names = [
        os.path.splitext(f)[0].lower()
        for f in os.listdir(folder)
        if f.endswith(".json")
    ]

    # Read CSV and lower case "Data File Name"
    csv_path = f"{datafolder}/metadata/ALL_combined_variable_codebook_all_harmonized_mortality_added.csv"
    df = pd.read_csv(csv_path)
    df["Data File Name"] = df["Data File Name"].str.lower()

    print(len(df))
    # Keep only rows where the data file name is in base_names
    filtered_df = df[df["Data File Name"].isin(base_names)]

    print(filtered_df)
    print(len(filtered_df))
    # [52152 rows x 13 columns]
    # 52152

    df = filtered_df

    folder = f"{datafolder}/schema"
    base_names = [
        os.path.splitext(f)[0].lower()
        for f in os.listdir(folder)
        if f.endswith(".json")
    ]

    def clean_var_name(name: str) -> str:
        """Clean variable or table name to be safe and lowercase."""
        if not isinstance(name, str):
            return ""
        name = re.sub(r"[ ,()\-\/%]", "_", name.strip().lower())
        name = re.sub(r"[^\w]", "_", name)
        return re.sub(r"_+", "_", name).strip("_")

    # --- 2. PERFORMANCE OPTIMIZATION: PRE-CLEAN COLUMNS ---
    print("Pre-cleaning columns for efficient matching...")
    df["cleaned_sas_label"] = df["SAS Label"].apply(clean_var_name)
    df["cleaned_data_file"] = df["Data File Name"].apply(clean_var_name)

    # --- 3. PRE-CREATE NEW COLUMNS ---
    df["Data Type"] = pd.NA
    df["Table Name"] = pd.NA
    df["Column Name"] = pd.NA
    df["Examples"] = None

    # --- 4. LOOP THROUGH FILES AND UPDATE DATAFRAME ---
    for base_name in tqdm(base_names, desc="Processing Schema Files"):
        file_path = os.path.join(folder, f"{base_name}.json")

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            if isinstance(data, list) and data:
                table_info = data[0]
            else:
                table_info = data

            full_table_name = table_info.get("table", "Not Found")
            if full_table_name and "." in full_table_name:
                table_name = full_table_name.split(".")[1]
            else:
                table_name = full_table_name or "Not Found"

            columns_data = table_info.get("columns", {})

            for column_name, column_details in columns_data.items():
                data_type = column_details.get("data_type", "N/A")
                sample_values = column_details.get("sample_values", [])

                if data_type in ["double precision", "bigint", "integer", "numeric"]:
                    sample_preview = sample_values[:5]
                elif data_type == "text":
                    non_empty_samples = [
                        v for v in sample_values if v and str(v).strip()
                    ]
                    empty_samples = [
                        v for v in sample_values if not v or not str(v).strip()
                    ]
                    sample_preview = non_empty_samples
                else:
                    # Make this message more informative
                    non_empty_samples = [
                        v for v in sample_values if v and str(v).strip()
                    ]
                    sample_preview = non_empty_samples

                # Use the pre-cleaned columns for a fast, vectorized match
                mask = (df["cleaned_sas_label"] == column_name) & (
                    df["cleaned_data_file"] == table_name
                )

                if mask.any():
                    df.loc[mask, "Data Type"] = data_type
                    df.loc[mask, "Table Name"] = table_name
                    df.loc[mask, "Column Name"] = column_name
                    df.loc[mask, "Examples"] = pd.Series(
                        [sample_preview] * mask.sum(), index=df[mask].index
                    )

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print("")
            # print(f"  -> Error processing file {file_path}: {e}")

    # --- 5. CLEANUP AND VERIFY ---
    # Drop the temporary cleaned columns
    df.drop(columns=["cleaned_sas_label", "cleaned_data_file"], inplace=True)

    print("\n--- Update Complete ---")
    # print("Displaying a sample of updated rows:")
    # print(df[df["Data Type"].notna()].head().to_string())

    # Drop specified columns if they exist
    columns_to_drop = ["Data Type", "Table Name", "Column Name"]
    df_cleaned = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    output_path = f"{datafolder}/metadata/schema_summary.csv"
    df_cleaned.to_csv(output_path, index=False)


import os
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
import logging
import sys
from pathlib import Path

import sys
from pathlib import Path

sys.path.append(str(Path.cwd().parents[0]))
from config import other_config, data_config, config

db_config = {
    "database": config.DB_NAME,
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "port": config.DB_PORT,
}


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


from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def execute_sql(sql: str):
    engine = create_db_engine(db_config)
    try:
        with engine.begin() as connection:
            connection.execute(text(sql))
    except SQLAlchemyError as e:
        raise RuntimeError(f"Database error: {e}") from e


def csv_to_psql(datafolder, schema_name):
    """
    Loads all CSV files from a folder into a PostgreSQL schema.
    """
    log_file = f"{datafolder}/csv_upload_log.txt"
    logging.basicConfig(
        filename=log_file,
        filemode="w",  # Overwrite on each run
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    csv_folder = f"{datafolder}/converted_tables"
    csv_files = []
    for root, dirs, files in os.walk(csv_folder):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    try:
        engine = create_db_engine(db_config)
        logging.info(f"Connected to: {engine.url}")

        with engine.begin() as connection:
            connection.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"))
            connection.execute(text(f"CREATE SCHEMA {schema_name};"))
            logging.info(f"Schema '{schema_name}' created.")

            for csv_filepath in tqdm(csv_files, desc="Uploading CSVs to DB"):
                table_name = os.path.splitext(os.path.basename(csv_filepath))[0]
                try:
                    df = pd.read_csv(csv_filepath, low_memory=False)
                    df.to_sql(
                        table_name,
                        connection,
                        schema=schema_name,
                        if_exists="replace",
                        index=False,
                    )
                    logging.info(
                        f"CSV data from '{csv_filepath}' loaded into '{schema_name}.{table_name}' successfully."
                    )
                except Exception as e:
                    logging.error(
                        f"Failed to load '{csv_filepath}' into '{schema_name}.{table_name}': {e}"
                    )

            logging.info("All CSV files loaded successfully.")

    except Exception as e:
        logging.error(f"An error occurred during DB operation: {e}")


def create_schema(datapath, schema):
    folder_path = f"{datapath}/converted_tables"

    os.makedirs(f"{datapath}/schema", exist_ok=True)

    table_names = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            table_name, ext = os.path.splitext(file)
            table_names.append(table_name)

    for table in tqdm(table_names, desc="Processing tables", total=len(table_names)):
        engine = n.create_db_engine(db_config)
        schema_data = n.extract_schema_and_samples(engine, table, schema)

        output_file_path = os.path.abspath(f"{datapath}/schema/{table}.json")
        with open(output_file_path, "w") as f:
            json.dump(schema_data, f, indent=4)
