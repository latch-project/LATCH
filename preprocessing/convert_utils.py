import pandas as pd
import os
import ast
import re
import numpy as np
import ast
import convert_dictionary
import warnings

warnings.filterwarnings("ignore")


def get_all_file_names(folder_path):
    file_names = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_names.append(os.path.join(root, file))
    return file_names


def is_age_threshold(val_desc):
    return (
        re.search(
            r"\b\d+\s*(or more|years\s+of\s+age\s+and\s+over|years\s+or)",
            val_desc,
            re.IGNORECASE,
        )
        or re.search(r"greater\s+than\s+or\s+equal\s+to", val_desc, re.IGNORECASE)
        or re.search(r"than\s+\d+\s+year", val_desc, re.IGNORECASE)
    )


def troubleshoot_column(filepath, column, metadatapath):
    filename = os.path.splitext(os.path.basename(filepath))
    file_base = filename[0]

    metadata_df = pd.read_csv(metadatapath)
    meta_subset = metadata_df[metadata_df["Data File Name"] == file_base]

    varname_to_label = {
        varname.lower(): label.lower()
        for varname, label in meta_subset[["Variable Name", "SAS Label"]]
        .dropna(subset=["SAS Label"])
        .set_index("Variable Name")["SAS Label"]
        .to_dict()
        .items()
    }

    df = pd.read_sas(filepath, format="xport")
    df.replace(5.397605346934028e-79, 0, inplace=True)
    df.columns = [col.lower() for col in df.columns]

    def word_in_dict_keys(word, dictionary):
        return word.strip().lower() in (key.lower() for key in dictionary.keys())

    for colname in df.columns:
        if colname == column:
            sas_label = varname_to_label.get(colname.lower(), "[No SAS Label found]")

            values_str_series = meta_subset[
                meta_subset["Variable Name"].str.lower() == colname
            ]["Values"]

            if values_str_series.isnull().any():
                print("")

            try:
                values_str = values_str_series.values[0]
                values_list = ast.literal_eval(values_str)
            except Exception as e:
                print("")

                if values_str_series.empty:
                    print("")
                else:
                    print("")

            def map_value_description(val_desc):
                val_desc = val_desc.strip().lower()
                if "range of values" in val_desc:
                    return "numerical"

                elif word_in_dict_keys(val_desc, convert_dictionary.numeric_ver1):
                    return "special"
                else:
                    return "categorical"

            code_map = {}
            for item in values_list:
                code = str(item["Code or Value"]).strip()
                print(f"Code: {code}")
                desc = str(item["Value Description"]).strip()
                print(f"Description: {desc}")
                mapped_type = map_value_description(desc)
                print(f"Mapped type: {mapped_type}")
                try:
                    code_key = int(code) if code != "." else "."

                except:
                    code_key = code

                if mapped_type == "numerical":
                    mapped_value = "numerical"  # skip
                elif mapped_type == "special":
                    mapped_value = convert_dictionary.numeric_ver1.get(
                        desc.strip().lower()
                    )
                elif mapped_type is None:
                    mapped_value = None

                elif mapped_type == "categorical":
                    mapped_value = desc

                else:
                    mapped_value = None

                # Only map categorical or None
                if mapped_type == "categorical":
                    code_map[code_key] = mapped_value
                    print("categorical")
                    print(f"Mapped value: {mapped_value}")
                    print(f"Code key: {code_key}")
                elif mapped_type == "special":
                    code_map[code_key] = mapped_value
                    print("special")
                    print(f"Mapped value: {mapped_value}")
                    print(f"Code key: {code_key}")
                elif mapped_type is None:
                    code_map[code_key] = None

            df[colname] = df[colname].replace(code_map)

    df = df.rename(columns=varname_to_label)
    return df


def convert_log_as_you_go(filepath, folder, dictionary_path):
    filename = os.path.splitext(os.path.basename(filepath))
    file_base = filename[0]

    log_filepath = f"{folder}/{file_base}.tsv"

    metadata_df = pd.read_csv(dictionary_path)
    meta_subset = metadata_df[
        metadata_df["Data File Name"].str.lower() == file_base.lower()
    ]

    varname_to_label = {
        varname.lower(): label.lower()
        for varname, label in meta_subset[["Variable Name", "SAS Label"]]
        .dropna(subset=["SAS Label"])
        .set_index("Variable Name")["SAS Label"]
        .to_dict()
        .items()
    }

    df = pd.read_sas(filepath, format="xport")
    df.replace(5.397605346934028e-79, 0, inplace=True)
    df.columns = [col.lower() for col in df.columns]

    if log_filepath:
        with open(log_filepath, "w") as f:
            f.write(
                "file\tcolumn\tsas_label\tmappedtype\tcode_original\tcode_key\tdescription\tmapped_value\n"
            )

    def word_in_dict_keys(word, dictionary):
        return word.strip().lower() in (key.lower() for key in dictionary.keys())

    for colname in df.columns[1:]:
        sas_label = varname_to_label.get(colname.lower(), "[No SAS Label found]")

        values_str_series = meta_subset[
            meta_subset["Variable Name"].str.lower() == colname
        ]["Values"]

        if values_str_series.isnull().any():
            print("")
            continue
        try:
            values_str = values_str_series.values[0]
            values_list = ast.literal_eval(values_str)
        except Exception as e:
            if values_str_series.empty:
                print("")
            else:
                print("")
                print(values_str_series)

        def map_value_description(val_desc):
            val_desc = val_desc.strip().lower()
            if "range of values" in val_desc:
                return "numerical"

            elif word_in_dict_keys(val_desc, convert_dictionary.numeric_ver1):
                return "special"
            else:
                return "categorical"

        code_map = {}
        for item in values_list:
            code = str(item["Code or Value"]).strip()
            desc = str(item["Value Description"]).strip()
            mapped_type = map_value_description(desc)
            try:
                code_key = int(code) if code != "." else "."

            except:
                code_key = code

            if mapped_type == "numerical":
                mapped_value = "numerical"
            elif mapped_type == "special":
                mapped_value = convert_dictionary.numeric_ver1.get(desc.strip().lower())
            elif mapped_type is None:
                mapped_value = None

            elif mapped_type == "categorical":
                mapped_value = desc

            else:
                mapped_value = None

            if log_filepath:
                with open(log_filepath, "a") as f:
                    f.write(
                        f"{file_base}\t{colname}\t{sas_label}\t{mapped_type}\t{code}\t{code_key}\t{desc}\t{mapped_value}\n"
                    )

            if mapped_type == "categorical":
                code_map[code_key] = mapped_value
            elif mapped_type == "special":
                code_map[code_key] = mapped_value
            elif mapped_type is None:
                code_map[code_key] = None

        df[colname] = df[colname].replace(code_map).infer_objects(copy=False)

    df = df.rename(columns=varname_to_label)
    return df


def analyze_csv_for_sql(filename, df):
    is_duplicate_col = df.columns.duplicated()

    for i, col in enumerate(df.columns):
        if is_duplicate_col[i]:
            continue

        try:
            col_data = df[col].dropna()

            if col_data.empty:
                continue

            if not isinstance(col_data, pd.Series):
                continue

            unique_vals = col_data.unique()
            sample_types = col_data.apply(type).value_counts()

            if len(sample_types) > 1:
                if not all(t is str for t in sample_types.index):
                    print("")
                    sql_type = "TEXT (fallback due to mixed types)"
                else:
                    max_len = col_data.astype(str).map(len).max()
                    sql_type = f"VARCHAR({max_len})" if pd.notna(max_len) else "TEXT"
            else:
                if pd.api.types.is_numeric_dtype(df[col]):
                    sql_type = (
                        "FLOAT" if pd.api.types.is_float_dtype(df[col]) else "BIGINT"
                    )
                elif pd.api.types.is_bool_dtype(df[col]):
                    sql_type = "BOOLEAN"
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    sql_type = "TIMESTAMP"
                elif pd.api.types.is_string_dtype(df[col]):
                    max_len = col_data.astype(str).map(len).max()
                    sql_type = f"VARCHAR({max_len})" if pd.notna(max_len) else "TEXT"
                else:
                    sql_type = "TEXT (fallback due to unknown type)"

        except Exception as e:
            print("")
            # print(f"\nError processing column '{col}' in file '{filename}': {e}")


import pandas as pd


def convert_columns_to_numeric(df, columns_to_convert):
    """
    Convert only the specified columns to numeric if they exist in the DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame to modify.
    - columns_to_convert (list): Column names to attempt conversion on.

    Returns:
    - pd.DataFrame: Modified DataFrame with numeric conversions applied.
    """
    for col in columns_to_convert:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            continue
    return df


def convert(filepath, conversionpath, logpath, dictionary_path):
    filename_with_extension = os.path.basename(filepath)
    filename = os.path.splitext(filename_with_extension)[0]

    try:
        df = convert_log_as_you_go(filepath, logpath, dictionary_path)

        df.columns = (
            df.columns.str.strip()  # Remove leading/trailing whitespace
            .str.lower()  # Optional: make lowercase
            .str.replace(r"[ ,()\-\/%]", "_", regex=True)
            .infer_objects(copy=False)  # Replace common special chars with _
            .str.replace(r"[^\w]", "_", regex=True)
            .infer_objects(copy=False)  # Replace any remaining non-word chars with _
            .str.replace(r"_+", "_", regex=True)  # Collapse multiple underscores
            .str.strip("_")
            .infer_objects(copy=False)  # Remove leading/trailing underscores
        )

        df = convert_columns_to_numeric(df, convert_dictionary.columns)
        analyze_csv_for_sql(filename, df)

        df.to_csv(
            f"{conversionpath}/{filename.lower()}.csv",
            index=False,
        )

    except Exception as e:
        print("")
        # print(f"Error processing {filepath}: {e}")
