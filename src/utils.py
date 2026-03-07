import json
from openai import OpenAI
import re
import os
import csv
from io import StringIO
from tabulate import tabulate
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import prompts as p
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate
import random
import numpy as np
import ast
from typing import Dict, List, Any
import random
from collections import Counter
import anthropic
from google import genai
from google.genai import types
import survey_weights as s
import traceback
from datetime import datetime
import sys
from collections import defaultdict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy.engine import Engine
from pathlib import Path
import ast
import pandas as pd
import re
import pandas as pd
import json
from datetime import datetime
import json
import ast
from tabulate import tabulate
import csv
import os
from datetime import datetime

sys.path.append(str(Path.cwd().parents[0]))
from config import other_config, data_config, config

PRICING = {
    "google_gemini-2.5-flash": {
        "input_price_per_million": 0.30,
        "output_price_per_million": 2.50,
    },
    "google_gemini-2.0-flash-001": {
        "input_price_per_million": 0.1,
        "output_price_per_million": 0.4,
    },
    "openai_gpt-4.1-2025-04-14": {
        "input_price_per_million": 2,
        "output_price_per_million": 8,
    },
    "openai_gpt-5.1-2025-11-13": {
        "input_price_per_million": 1.25,
        "output_price_per_million": 10,
    },
    "anthropic_claude-sonnet-4-5-20250929": {
        "input_price_per_million": 3,
        "output_price_per_million": 15,
    },
    "anthropic_claude-3-7-sonnet-20250219": {
        "input_price_per_million": 3,
        "output_price_per_million": 15,
    },
}


def calculate_cost(model, usage_info):
    if model == "google_gemini-2.5-flash":
        return calculate_gemini_cost(model, usage_info)
    elif model == "google_gemini-2.0-flash-001":
        return calculate_gemini_cost(model, usage_info)
    elif model == "openai_gpt-4.1-2025-04-14":
        return calculate_openai_cost(model, usage_info)
    elif model == "openai_gpt-5.1-2025-11-13":
        return calculate_openai_cost(model, usage_info)
    elif model == "anthropic_claude-3-7-sonnet-20250219":
        return calculate_anthropic_cost(model, usage_info)
    elif model == "anthropic_claude-sonnet-4-5-20250929":
        return calculate_anthropic_cost(model, usage_info)


def calculate_anthropic_cost(model_name: str, usage_info: object) -> dict:
    """Calculates the cost of an Anthropic API call from usage data."""
    if model_name not in PRICING:
        return {"error": f"Pricing for model '{model_name}' not found."}

    pricing = PRICING[model_name]
    input_tokens = usage_info.input_tokens
    output_tokens = usage_info.output_tokens

    input_cost = (input_tokens / 1_000_000) * pricing["input_price_per_million"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_price_per_million"]
    total_cost = input_cost + output_cost

    return {
        "model_name": model_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost": total_cost,
        "formatted_total_cost": f"${total_cost:,.6f}",
    }


def calculate_openai_cost(model_name: str, usage_info) -> dict:
    """Calculates the cost of an OpenAI Responses API call."""

    if model_name not in PRICING:
        return {"error": f"Pricing for model '{model_name}' not found."}

    pricing = PRICING[model_name]

    # Responses API fields
    input_tokens = usage_info.input_tokens
    output_tokens = usage_info.output_tokens

    input_cost = (input_tokens / 1_000_000) * pricing["input_price_per_million"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_price_per_million"]

    total_cost = input_cost + output_cost

    return {
        "model_name": model_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost": total_cost,
        "formatted_total_cost": f"${total_cost:,.6f}",
    }


def calculate_gemini_cost(model_name: str, usage_metadata: object) -> dict:
    """
    Calculates the cost of a Gemini API call using the response's usage_metadata.

    Args:
        model_name (str): The specific Gemini model used.
        usage_metadata (object): The usage_metadata object from the API response,
                                 containing prompt_token_count and candidates_token_count.

    Returns:
        dict: A dictionary containing input, output, and total costs.
    """
    if model_name not in PRICING:
        return {"error": f"Pricing for model '{model_name}' not found."}
    pricing_info = PRICING[model_name]
    input_tokens = usage_metadata.prompt_token_count
    output_tokens = usage_metadata.candidates_token_count
    input_cost = (input_tokens / 1_000_000) * pricing_info["input_price_per_million"]
    output_cost = (output_tokens / 1_000_000) * pricing_info["output_price_per_million"]
    total_cost = input_cost + output_cost

    return {
        "model_name": model_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost": total_cost,
        "formatted_total_cost": f"${total_cost:,.6f}",
    }


db_config = {
    "database": config.DB_NAME,
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "port": config.DB_PORT,
}


def get_weights(
    dictionary, years, schema, analysis, patientid="respondent_sequence_number"
):
    with open(f"{data_config.root}/nhanes/weights/exam_tables.json", "r") as f:
        exam_lab_tables = set(json.load(f))
    df = pd.read_csv(f"{data_config.root}/nhanes/weights/subset_weights.csv")
    df["Table Names"] = df["Table Names"].apply(ast.literal_eval)
    non_full_sample_df = df
    verdicts, table_to_group = s.assign_verdicts(
        dictionary, non_full_sample_df, exam_lab_tables
    )
    unique_verdicts = sorted(set(verdicts.values()))
    if "exam" in analysis:
        unique_verdicts.append("exam")
    verdict_to_weights = {}

    for keyword in unique_verdicts:
        weights = s.get_weights_for_verdict(
            verdict=keyword,
            years=years,
            interview_weight_column_map=s.interview_weight_column_map,
            exam_weight_column_map=s.exam_weight_column_map,
            input_data=dictionary,
            table_to_group=table_to_group,
            final_weights_df=non_full_sample_df,
            verdicts=verdicts,
        )
        verdict_to_weights[keyword] = weights  # Store in dictionary

    sql = s.get_restriction_summary_table_sql(verdict_to_weights, schema=schema)
    df = execute_query(sql)
    most_restrictive_verdict = df.sort_values(
        "pct_overlap_with_all", ascending=False
    ).iloc[0]["verdict"]
    if "exam" in analysis:
        most_restrictive_verdict = "exam"
        verdict = most_restrictive_verdict
        weights = verdict_to_weights[f"{most_restrictive_verdict}"]

    elif "questionnaire" in analysis:
        most_restrictive_verdict = "questionnaire"
        verdict = most_restrictive_verdict
        weights = verdict_to_weights[f"{most_restrictive_verdict}"]
    else:
        verdict = most_restrictive_verdict
        weights = verdict_to_weights[f"{most_restrictive_verdict}"]

    def suffix_key(table: str) -> str:
        t = table.lower()
        if t.startswith("p_"):
            return "p"
        m = re.search(r"_([a-z])$", t)
        return m.group(1) if m else ""

    unique_weights_by_year = {}
    for table, weight_col, coeff in weights:
        key = suffix_key(table)
        if key not in unique_weights_by_year:
            unique_weights_by_year[key] = (table, weight_col, coeff)
    unique_weights_by_year
    weights = list(unique_weights_by_year.values())
    if len(weights) != len(years):
        print("**Weight and year lists have different lengths")
    weights_sql = s.generate_adjusted_weight_sql(weights, schema)
    psu_stratum_sql_code = s.generate_temp_psu_stratum_sql(
        years, s.psu_column_map, s.stratum_column_map, schema
    )
    sql_final = s.merge_weight_and_design_tables(weights_sql, psu_stratum_sql_code)

    return sql_final, verdict


def post_hoc_cohort(sql, cohort_track):
    cohort_info = execute_query(sql + "\n" + cohort_track)
    if isinstance(cohort_info, pd.DataFrame):
        print("Input is a DataFrame. Converting to string...")
        cohort = cohort_info.to_string()
    else:
        print("Input is not a DataFrame. Saving directly...")
        cohort = cohort_info
    return cohort


def sql_refine(sql, master_sql, variable_dic, years, schema, analysis):
    if "weighted" in analysis.lower():
        weight, full_sql_script = process_weighted_sql(
            sql, master_sql, variable_dic, years, schema, analysis
        )
        cohort_track = weighted_generate_exclusion_report_sql(full_sql_script)
    else:
        full_sql_script = master_sql + "\n" + sql
        weight = None
        cohort_track = generate_exclusion_report_sql_with_comments(sql)
    return weight, full_sql_script, cohort_track


def process_weighted_sql(sql, master_sql, variable_dic, years, schema, analysis):
    variables = list(execute_query(sql).columns)
    weighted_final_sql = generate_sql_merge_with_weights(variables)
    tables_by_keyword = {
        keyword: [entry["table"] for entry in entries]
        for keyword, entries in variable_dic.items()
    }
    weight_sql, weightname = get_weights(tables_by_keyword, years, schema, analysis)

    full_sql_script = (
        weight_sql
        + "\n\n"
        + master_sql
        + "\n\n"
        + delete_sql
        + "\n\n"
        + sql
        + "\n\n"
        + weighted_final_sql
    )
    return weightname, full_sql_script


delete_sql = """
-- Clean up final_master_table
DELETE FROM final_master_table
WHERE respondent_sequence_number NOT IN (
    SELECT respondent_sequence_number FROM weight_design
);
"""


def generate_sql_merge_with_weights(final_vars):

    if "respondent_sequence_number" not in final_vars:
        raise ValueError(
            '"respondent_sequence_number" must be included in the final_vars list.'
        )

    def quote(col):
        return f'"{col}"'

    final_cols_sql = ",\n    ".join(
        [
            f"ft.{quote(col)}"
            for col in final_vars
            if col != "respondent_sequence_number"
        ]
    )
    weight_cols = [
        f'wd.{quote("respondent_sequence_number")}',
        f'wd.{quote("masked_variance_pseudo_psu")}',
        f'wd.{quote("masked_variance_pseudo_stratum")}',
        f'wd.{quote("survey_weight")}',
    ]
    in_analysis_col = f'CASE WHEN ft.{quote("respondent_sequence_number")} IS NOT NULL THEN 1 ELSE 0 END AS "in_analysis"'
    all_cols_sql = ",\n    ".join(weight_cols + [in_analysis_col, final_cols_sql])
    sql = f"""-- STEP: Create merged final table with design variables + in_analysis flag
DROP TABLE IF EXISTS temp_final_with_weights;

CREATE TEMP TABLE temp_final_with_weights AS
SELECT 
    {all_cols_sql}
FROM weight_design wd
LEFT JOIN temp_final_table ft
  ON wd.{quote("respondent_sequence_number")} = ft.{quote("respondent_sequence_number")};
  
-- Preview the result
SELECT * FROM temp_final_with_weights;
"""
    return sql


def merge_sql_scripts(sql1: str, sql2: str, sql3: str) -> str:
    def clean_sql(sql: str) -> str:
        lines = sql.strip().splitlines()
        return "\n".join(
            line
            for line in lines
            if "SELECT * FROM temp_final_table" not in line
            and "-- ========== STEP 6: View Output ==========" not in line
        )

    merged_sql = "\n\n".join(
        [
            "-- === Cohort generation (LLM) ===",
            clean_sql(sql1),
            "-- === Weight integration (rule-based) ===",
            clean_sql(sql2),
            clean_sql(sql3),
        ]
    )
    return merged_sql


def random_id():
    return random.randint(10000, 99999)


def find_keyword_by_id(study_id, data):
    try:
        study_id = int(study_id)
    except ValueError:
        return "Invalid ID format"

    def search(d, parent_key=""):
        if isinstance(d, dict):
            for k, v in d.items():
                result = search(v, k)
                if result:
                    return f"{parent_key} > {result}" if parent_key else result
        elif isinstance(d, list):
            if study_id in d:
                return parent_key
        elif d == study_id:
            return parent_key
        return None

    return search(data) or "ID not found"


def add_to_lookup_table(lookup_dict, lookup_table):
    """
    Appends a structured keyword lookup dictionary to a flat CSV file.

    Args:
        lookup_dict (dict): Format {keyword: [{cycle, table, column, example values}, ...]}
        lookup_table (str): Path to the CSV file to append to.
    """
    csv_path = lookup_table
    file_exists = os.path.exists(csv_path)
    rows_added = []

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists or os.path.getsize(csv_path) == 0:
            writer.writerow(["keyword", "cycle", "table", "column", "example_values"])

        for keyword, records in lookup_dict.items():
            for entry in records:
                row = [
                    keyword,
                    entry.get("cycle", ""),
                    entry.get("table", ""),
                    entry.get("column", ""),
                    str(entry.get("example_values", [])),
                ]
                writer.writerow(row)
                rows_added.append(row)
    print("Rows added to lookup table:")
    for row in rows_added:
        print(row)

    return len(rows_added)


def extract_lookup_table(json_data):
    """
    Extracts a flattened lookup table from a structured question JSON.

    Args:
        json_data (dict): The JSON object containing analysis info.

    Returns:
        pd.DataFrame: A DataFrame with columns: keyword, cycle, table, column, example_values.
    """
    records = []

    for section in ["inclusion", "exclusion", "covariates"]:
        for item in json_data.get(section, []):
            keyword = item.get("keyword")
            for source in item.get("data_sources", []):
                records.append(
                    {
                        "keyword": keyword,
                        "cycle": source.get("cycle"),
                        "table": source.get("table"),
                        "column": source.get("column"),
                        "example_values": source.get("example values"),
                    }
                )

    label = json_data.get("label", {})
    keyword = label.get("keyword")
    for source in label.get("data_sources", []):
        records.append(
            {
                "keyword": keyword,
                "cycle": source.get("cycle"),
                "table": source.get("table"),
                "column": source.get("column"),
                "example_values": source.get("example values"),
            }
        )

    return pd.DataFrame(records)


def summarize_data_sources(data):
    """
    Summarizes the tables and columns used for each keyword in the provided data structure.

    This function recursively finds data sources, handling nested dependencies for derived keywords.

    Args:
        data (dict): The input JSON data as a Python dictionary.

    Returns:
        dict: A dictionary where each key is a keyword and the value is another
              dictionary containing the sets of tables and columns used.
    """
    summary = {}

    def get_sources(item):
        sources = {"tables": set(), "columns": set()}

        if "data_sources" in item:
            for source in item["data_sources"]:
                if "table" in source:
                    sources["tables"].add(source["table"])
                if "column" in source:
                    sources["columns"].add(source["column"])
        if "depends_on" in item:
            for dep_item in item["depends_on"]:
                dep_sources = get_sources(dep_item)
                sources["tables"].update(dep_sources["tables"])
                sources["columns"].update(dep_sources["columns"])

        return sources

    sections_to_process = ["exclusion", "predictor", "covariates", "label"]
    for section in sections_to_process:
        if section in data:
            for item in data[section]:
                keyword = item["keyword"]
                if keyword not in summary:
                    summary[keyword] = {"tables": set(), "columns": set()}

                keyword_sources = get_sources(item)
                summary[keyword]["tables"].update(keyword_sources["tables"])
                summary[keyword]["columns"].update(keyword_sources["columns"])

    return summary


def print_summary(summary):
    """
    Prints the summary in a readable format.
    """
    for keyword, sources in summary.items():
        print(f"Keyword: {keyword}")
        tables = ", ".join(sorted(list(sources["tables"])))
        columns = ", ".join(sorted(list(sources["columns"])))
        print(f"  Tables: {tables}")
        print(f"  Columns: {columns}")
        print("-" * 40)


def summarize_data_source_pairs(data):
    """
    Summarizes the (table, column) pairs used for each keyword.

    This function recursively finds data sources and preserves the table-column
    linkage, handling nested dependencies for derived keywords.

    Args:
        data (dict): The input JSON data as a Python dictionary.

    Returns:
        dict: A dictionary where each key is a keyword and the value is a
              set of (table, column) tuples.
    """
    summary = {}

    def get_source_pairs(item):
        pairs = set()
        if "data_sources" in item:
            for source in item["data_sources"]:
                if "table" in source and "column" in source:
                    pairs.add((source["cycle"], source["table"], source["column"]))
        if "depends_on" in item:
            for dep_item in item["depends_on"]:
                pairs.update(get_source_pairs(dep_item))

        return pairs

    sections_to_process = ["exclusion", "predictor", "covariates", "label"]

    for section in sections_to_process:
        if section in data:
            for item in data[section]:
                keyword = item["keyword"]
                if keyword not in summary:
                    summary[keyword] = set()

                keyword_pairs = get_source_pairs(item)
                summary[keyword].update(keyword_pairs)

    return summary


def print_pairs_summary(summary):
    """
    Prints the summary of (table, column) pairs in a readable format.
    """
    for keyword, pairs in summary.items():
        print(f"Keyword: {keyword}")
        if not pairs:
            print("  No table-column pairs found.")
        else:
            sorted_pairs = sorted(list(pairs))
            for cycle, table, column in sorted_pairs:
                print(f"  - Cycle : {cycle}, Table: {table}, Column: {column}")
        print("-" * 60)


def get_table(csv_path, title):
    df = pd.read_csv(csv_path)
    df["Title"] = df["Title"].astype(str)
    matched = df[df["Title"] == str(title)]

    if matched.empty:
        print(f" No entry found for title: {title}")
        return
    question_str = matched["Question"].iloc[0]
    dataframe_str = matched["Dataframeshape"].iloc[0]
    stats_str = matched["Statistics"].iloc[0]
    sql = matched["SQL"].iloc[0]
    variable = matched["Variables"].iloc[0]
    variable_list = ast.literal_eval(variable)
    variable_df = pd.DataFrame(variable_list)
    missing = matched["Missing Value"].iloc[0]
    missing_list = ast.literal_eval(missing)
    missing_df = pd.DataFrame(missing_list)

    return sql


def _normalize_string(s):
    """Converts string to lowercase and removes all non-alphanumeric characters."""
    if not isinstance(s, str):
        return ""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _normalize_string(s):
    """Converts string to lowercase and removes all non-alphanumeric characters."""
    if not isinstance(s, str):
        return ""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def build_keyword_lookup(csv_path, keywords, year_ranges, lookup_enabled=True):
    """
    Looks up keywords and year ranges in a CSV, using exact string match.
    """
    keywords_to_exclude = {"all individuals", "None", "none"}
    keywords = [kw for kw in keywords if kw not in keywords_to_exclude]

    if not lookup_enabled:
        not_found_keywords = [
            [keyword, year_range] for keyword in keywords for year_range in year_ranges
        ]
        print("Lookup disabled. Returning all keywords as not found.")
        return {}, not_found_keywords

    columns = ["keyword", "cycle", "table", "column", "example_values"]
    try:
        df = pd.read_csv(csv_path, header=None, names=columns)
    except FileNotFoundError:
        print(f"Error: Lookup file not found at {csv_path}")
        not_found_keywords = [
            [keyword, year_range] for keyword in keywords for year_range in year_ranges
        ]
        return {}, not_found_keywords

    df["keyword"] = df["keyword"].astype(str)
    df["cycle"] = df["cycle"].astype(str)
    cycle_years = df["cycle"].str.extract(r"(?P<start>\d{4})[-–](?P<end>\d{4})")
    df["cycle_start"] = pd.to_numeric(cycle_years["start"], errors="coerce")
    df["cycle_end"] = pd.to_numeric(cycle_years["end"], errors="coerce")
    df = df.dropna(subset=["cycle_start", "cycle_end"])
    df = df.astype({"cycle_start": int, "cycle_end": int})
    df_keyword_filtered = df[df["keyword"].isin(keywords)]

    def cycle_exactly_matches_range(cycle_start, cycle_end):
        return any(
            cycle_start == yr_start and cycle_end == yr_end
            for yr_start, yr_end in year_ranges
        )

    df_filtered = df_keyword_filtered[
        df_keyword_filtered.apply(
            lambda row: cycle_exactly_matches_range(
                row["cycle_start"], row["cycle_end"]
            ),
            axis=1,
        )
    ].copy()

    result = {}
    not_found_keywords = []

    if not df_filtered.empty:
        result = {
            keyword: group[["cycle", "table", "column", "example_values"]].to_dict(
                orient="records"
            )
            for keyword, group in df_filtered.groupby("keyword")
        }

    found_pairs = set()
    if not df_filtered.empty:
        for _, row in df_filtered.iterrows():
            keyword = row["keyword"]
            for yr_start, yr_end in year_ranges:
                if row["cycle_start"] == yr_start and row["cycle_end"] == yr_end:
                    found_pairs.add((keyword, (yr_start, yr_end)))

    for keyword in keywords:
        for yr_range in year_ranges:
            if (keyword, tuple(yr_range)) not in found_pairs:
                not_found_keywords.append([keyword, yr_range])

    print("Not found keyword-year combinations:")
    print(not_found_keywords)

    return result, not_found_keywords


def safe_json_load(data):
    """
    Safely load JSON from a string or return it directly if already a dict.
    Handles trailing commas, incorrect boolean casing, and single quotes.
    """
    if isinstance(data, dict):
        return data

    if not isinstance(data, str):
        raise ValueError("Input must be a dictionary or JSON-formatted string.")
    cleaned = data.strip()
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
    cleaned = cleaned.replace("False", "false").replace(
        "True", "true".replace("99999", "Infinity")
    )
    cleaned = re.sub(r"'", r'"', cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            cleaned = data.strip()
            cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
            cleaned = (
                cleaned.replace("false", "False")
                .replace("true", "True")
                .replace("null", "None")
                .replace("Infinity", "99999")
            )
            return ast.literal_eval(cleaned)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON or Python dict: {e}")


def enrich_keywords_with_data_sources(
    analysis: Dict[str, Any], lookup: List[Dict[str, Any]]
) -> Dict[str, Any]:
    keyword_map = {}
    for entry in lookup:
        for kw in entry["keywords"]:
            keyword_map[kw] = {
                "table": entry["table"],
                "column": entry["column"],
                "examples": entry["pooled_example"],
            }

    def enrich_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
        enriched = dict(entry)
        kw = entry["keyword"]
        if kw in keyword_map:
            enriched.update(keyword_map[kw])
        return enriched

    for section in [
        k
        for k in analysis.keys()
        if k not in {"analysis_type", "dataset", "period_of_interest"}
    ]:
        if section in analysis:
            enriched_list = []
            for item in analysis[section]:
                enriched = enrich_entry(item)
                if "depends_on" in item:
                    enriched["depends_on"] = [
                        enrich_entry(dep) for dep in item["depends_on"]
                    ]
                if "derivation" in item:
                    enriched["derivation"] = item["derivation"]
                enriched_list.append(enriched)
            analysis[section] = enriched_list

    return analysis


def master_table_and_schema_creation(parsed_question, matching_schema_info, patient_id):

    question_dic = safe_json_load(parsed_question)
    data, bottom_level_keywords = get_bottom_level_variables_check(matching_schema_info)

    sources = extract_keywords_and_data_sources(data)
    a = merge_by_common_columns(sources)
    b = extract_table_column_pairs_with_examples(a)
    c = add_majority_column_field(b)
    c1 = simplify_to_final_master_table_structure(c)
    master_schema = enrich_keywords_with_data_sources(question_dic, c1)
    master_sql = generate_temp_table_sql(c, patient_id)
    del master_schema["analysis_type"]
    del master_schema["period_of_interest"]
    return master_sql, master_schema


def simplify_to_final_master_table_structure(
    data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    simplified = []
    for entry in data:
        simplified.append(
            {
                "keywords": entry["keywords"],
                "table": "final_master_table",
                "column": entry["majority_column"].lower(),
                "pooled_example": entry["pooled_example"],
            }
        )
    return simplified


import json
from typing import List, Dict, Any


def merge_by_common_columns(
    keywords: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Groups keywords if they share the exact same set of column names in their
    data sources. When merged, the data_sources from the first keyword encountered
    is used for the entire group.

    Args:
        keywords: A list where each item is a dictionary containing a 'keyword'
                  and its 'data_sources'.

    Returns:
        A list of dictionaries, where keywords with common columns are merged.
    """

    def normalize_source(source: Dict[str, Any]) -> Dict[str, Any]:
        """Corrects known typos in a source dictionary."""
        normalized = source.copy()
        if "example values" in normalized:
            normalized["example_values"] = normalized.pop("example values")
        return normalized

    def create_column_fingerprint(sources: List[Dict[str, Any]]) -> str:
        """
        Creates a unique fingerprint based on the sorted list of unique column
        names from a list of data sources.
        """
        normalized_sources = [normalize_source(s) for s in sources]
        column_names = {s["column"] for s in normalized_sources}
        sorted_columns = sorted(list(column_names))
        return json.dumps(sorted_columns)

    merged_dict = {}

    for entry in keywords:
        key = create_column_fingerprint(entry["data_sources"])

        if key in merged_dict:

            existing_keywords = merged_dict[key]["keywords"]
            new_keyword = entry["keyword"]
            shared_columns = json.loads(
                key
            )  # Unpack the columns from the key for the message

            merged_dict[key]["keywords"].append(new_keyword)
        else:

            merged_dict[key] = {
                "keywords": [entry["keyword"]],
                "data_sources": [normalize_source(s) for s in entry["data_sources"]],
            }

    return [
        {"keywords": sorted(item["keywords"]), "data_sources": item["data_sources"]}
        for item in merged_dict.values()
    ]


def generate_temp_table_sql(data, patientid="respondent_sequence_number"):
    sql_blocks = []
    temp_table_names = []

    for entry in data:
        keywords = entry["keywords"]
        majority_column = entry["majority_column"]
        pairs = entry["table_column_pairs"]

        comment = "-- TEMP TABLE FOR " + ", ".join([f'"{k}"' for k in keywords])
        temp_table_name = f"temp_master_{majority_column.lower()}"
        temp_table_names.append((temp_table_name, majority_column))

        drop_statement = f"DROP TABLE IF EXISTS {temp_table_name};"
        create_statement = f"CREATE TEMP TABLE {temp_table_name} AS"

        union_queries = [
            f'SELECT {patientid}, "{column}" AS "{majority_column}"\nFROM {table}'
            for table, column in pairs
        ]
        full_union = "\nUNION ALL\n".join(union_queries)

        index_statement = f"""
-- Add index for faster joins
CREATE INDEX idx_{temp_table_name} ON {temp_table_name} ({patientid});"""

        sql_block = f"{comment}\n{drop_statement}\n{create_statement}\n{full_union};{index_statement}"
        sql_blocks.append(sql_block)

    all_ids_union = "\nUNION\n".join(
        [f"SELECT {patientid} FROM {name}" for name, _ in temp_table_names]
    )

    temp_all_ids_sql = f"""
-- ALL UNIQUE PATIENT IDs
DROP TABLE IF EXISTS temp_all_ids;
CREATE TEMP TABLE temp_all_ids AS
{all_ids_union};

-- Add index to the main ID table for the final join
CREATE INDEX idx_temp_all_ids_{patientid} ON temp_all_ids ({patientid});
""".strip()

    join_clauses = []
    select_columns = [f"    a.{patientid}"]
    for idx, (table_name, col) in enumerate(temp_table_names):
        alias = f"t{idx}"
        join_clauses.append(
            f"LEFT JOIN {table_name} {alias} ON a.{patientid} = {alias}.{patientid}"
        )
        select_columns.append(f'    {alias}."{col}"')

    final_sql = f"""
-- FINAL MASTER TABLE
DROP TABLE IF EXISTS final_master_table;
CREATE TABLE final_master_table AS
SELECT
{',\n'.join(select_columns)}
FROM temp_all_ids a
{' \n'.join(join_clauses)};

CREATE INDEX idx_final_master_{patientid}    
    ON final_master_table ({patientid});

""".strip()
    sql_blocks.append(temp_all_ids_sql)
    sql_blocks.append(final_sql)

    return "\n\n".join(sql_blocks)


def generate_temp_table_sql_old(data, patientid="respondent_sequence_number"):
    sql_blocks = []
    temp_table_names = []

    for entry in data:
        keywords = entry["keywords"]
        majority_column = entry["majority_column"]
        pairs = entry["table_column_pairs"]

        comment = "-- TEMP TABLE FOR " + ", ".join([f'"{k}"' for k in keywords])
        temp_table_name = f"temp_master_{majority_column.lower()}"
        temp_table_names.append((temp_table_name, majority_column))

        drop_statement = f"DROP TABLE IF EXISTS {temp_table_name};"
        create_statement = f"CREATE TEMP TABLE {temp_table_name} AS"

        union_queries = [
            f'SELECT {patientid}, "{column}" AS "{majority_column}"\nFROM {table}'
            for table, column in pairs
        ]
        full_union = "\nUNION ALL\n".join(union_queries)
        sql_block = f"{comment}\n{drop_statement}\n{create_statement}\n{full_union};"
        sql_blocks.append(sql_block)

    all_ids_union = "\nUNION\n".join(
        [f"SELECT {patientid} FROM {name}" for name, _ in temp_table_names]
    )
    temp_all_ids_sql = f"""
-- ALL UNIQUE PATIENT IDs
DROP TABLE IF EXISTS temp_all_ids;
CREATE TEMP TABLE temp_all_ids AS
{all_ids_union};
""".strip()

    join_clauses = []
    select_columns = [f"    a.{patientid}"]
    for idx, (table_name, col) in enumerate(temp_table_names):
        alias = f"t{idx}"
        join_clauses.append(
            f"LEFT JOIN {table_name} {alias} ON a.{patientid} = {alias}.{patientid}"
        )
        select_columns.append(f'    {alias}."{col}"')

    final_sql = f"""
-- FINAL MASTER TABLE
DROP TABLE IF EXISTS final_master_table;
CREATE TABLE final_master_table AS
SELECT
{',\n'.join(select_columns)}
FROM temp_all_ids a
{' \n'.join(join_clauses)};
""".strip()

    sql_blocks.append(temp_all_ids_sql)
    sql_blocks.append(final_sql)

    return "\n\n".join(sql_blocks)


def add_majority_column_field(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for entry in data:
        columns = [col for _, col in entry["table_column_pairs"]]
        column_counts = Counter(columns)
        max_count = max(column_counts.values())
        top_columns = [
            col for col, count in column_counts.items() if count == max_count
        ]
        majority_column = random.choice(top_columns)

        result.append(
            {
                "keywords": entry["keywords"],
                "table_column_pairs": entry["table_column_pairs"],
                "pooled_example": entry["pooled_example"],
                "majority_column": majority_column,
            }
        )
    return result


def merge_keywords_by_data_sources(
    keywords: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    def normalize_source(source: Dict[str, Any]) -> Dict[str, Any]:
        normalized = source.copy()
        if "example values" in normalized:
            normalized["example_values"] = normalized.pop("example values")
        return normalized

    def serialize_sources(sources: List[Dict[str, Any]]) -> str:
        simplified_sources = [
            {"cycle": s["cycle"], "table": s["table"], "column": s["column"]}
            for s in (normalize_source(src) for src in sources)
        ]

        unique_source_strings = {
            json.dumps(s, sort_keys=True) for s in simplified_sources
        }
        deduplicated_sources = [json.loads(s) for s in unique_source_strings]
        return json.dumps(
            sorted(
                deduplicated_sources,
                key=lambda x: (x["cycle"], x["table"], x["column"]),
            ),
            sort_keys=True,
        )

    merged_dict = {}
    for entry in keywords:
        key = serialize_sources(entry["data_sources"])
        if key in merged_dict:
            merged_dict[key]["keywords"].append(entry["keyword"])
        else:
            normalized_sources = [normalize_source(s) for s in entry["data_sources"]]
            merged_dict[key] = {
                "keywords": [entry["keyword"]],
                "data_sources": normalized_sources,
            }
    return [
        {"keywords": item["keywords"], "data_sources": item["data_sources"]}
        for item in merged_dict.values()
    ]


def extract_table_column_pairs_with_examples(
    data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    result = []
    for entry in data:
        pairs = []
        seen = set()
        example_set = set()

        for source in entry["data_sources"]:
            pair = (source["table"], source["column"])
            if pair not in seen:
                seen.add(pair)
                pairs.append([source["table"], source["column"]])
            example_set.update(
                val for val in source.get("example_values", []) if val != ""
            )

        is_all_numeric = all(_is_number(val) for val in example_set)
        if is_all_numeric:
            pooled_example = sorted(example_set, key=_as_number)[:5]
        else:
            pooled_example = sorted(example_set)

        result.append(
            {
                "keywords": entry["keywords"],
                "table_column_pairs": pairs,
                "pooled_example": pooled_example,
            }
        )
    return result


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _as_number(s: str) -> float:
    try:
        return float(s)
    except ValueError:
        return float("inf")


def merge_dicts(d1, d2):
    merged = dict(d1)
    for key, value in d2.items():
        if key in merged:
            if isinstance(merged[key], list) and isinstance(value, list):
                merged[key].extend(value)
            else:
                merged[key] = value
        else:
            merged[key] = value
    return merged


def get_bottom_level_variables(input_json_str):
    if isinstance(input_json_str, str):
        input_json_str = input_json_str.strip()
        if input_json_str.lower().startswith("json"):
            first_brace = input_json_str.find("{")
            if first_brace != -1:
                input_json_str = input_json_str[first_brace:]
            else:
                raise ValueError("No JSON object found in input string.")
        if not input_json_str:
            raise ValueError(
                "Empty or invalid JSON string passed to get_bottom_level_variables"
            )
        try:
            data = json.loads(input_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e.msg}") from e
    elif isinstance(input_json_str, dict):
        data = input_json_str
    else:
        raise TypeError("Input must be a JSON string or dictionary")
    bottom_vars = set()

    def collect_variables(block):
        if not block.get("depends_on"):
            bottom_vars.add(block["keyword"])
        else:
            for dep in block.get("depends_on", []):
                collect_variables(dep)

    for section in [
        k
        for k in data.keys()
        if k not in {"analysis_type", "dataset", "period_of_interest", "outcome"}
    ]:
        for item in data.get(section, []):
            collect_variables(item)

    label_section = data.get("outcome")
    if isinstance(label_section, dict):
        for value in label_section.values():
            collect_variables(value)
    elif isinstance(label_section, list):
        for item in label_section:
            collect_variables(item)

    return {"bottom_level_variables": sorted(bottom_vars)}


def get_first_code_block(response):
    match = re.search(r"'''(.*?)'''", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    raise ValueError("No code block found in the response.")


def get_json_block(response: str) -> str:
    """
    Extracts a JSON string from a larger text block, trying various patterns.

    Args:
        response: The string response, potentially containing a JSON code block.

    Returns:
        A string containing valid JSON.

    Raises:
        ValueError: If no valid JSON block can be found or parsed.
    """
    response.replace("True", "true").replace("False", "false")
    match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
    if match:
        potential_json = match.group(1).strip()
        potential_json = potential_json.replace("True", "true").replace(
            "False", "false"
        )
        try:
            json.loads(potential_json)
            return potential_json
        except json.JSONDecodeError:
            pass

    match = re.search(r"[`']{3}\s*(\{.*?\})\s*[`']{3}", response, re.DOTALL)
    if match:
        potential_json = match.group(1).strip()
        potential_json = potential_json.replace("True", "true").replace(
            "False", "false"
        )
        try:
            json.loads(potential_json)
            return potential_json
        except json.JSONDecodeError:
            pass

    try:
        start_index = response.find("{")
        end_index = response.rfind("}") + 1
        if start_index != -1 and end_index != 0:
            potential_json = response[start_index:end_index]
            potential_json = potential_json.replace("True", "true").replace(
                "False", "false"
            )
            json.loads(potential_json)
            return potential_json
    except json.JSONDecodeError:
        pass

    raise ValueError("Could not find or parse a valid JSON block in the response.")


openai_api_key = config.OPENAI_API_KEY
ANTHROPIC_API_KEY = config.ANTHROPIC_API_KEY
GOOGLE_API_KEY = config.GOOGLE_API_KEY

import time


def generate_ai_response(system_content, user_content, provider):
    """
    Fetches a completion from a specified LLM provider using a config dictionary.

    Args:
    system_content (str): The system message or instruction for the model.
    user_content (str): The user's prompt or message.
    config (dict): A dictionary containing 'provider', 'model', 'api_key' (optional),
    'max_tokens', and 'temperature'.

    Returns:
    str: The content of the generated message.
    """

    user_content = user_content

    try:
        if "openai" in provider:

            openai_config = {
                "provider": "openai",
                "model": provider.split("_")[1],
                "temperature": 0,
                "max_tokens": 50000,
                "api_key": openai_api_key,
            }

            model = openai_config.get("model")
            provider = openai_config.get("provider", "").lower()
            max_tokens = openai_config.get("max_tokens", 50000)
            temperature = openai_config.get("temperature", 0)
            api_key = openai_config.get("api_key")
            client = OpenAI(api_key=openai_api_key)

            if "gpt-5" in model:
                resp = client.responses.create(
                    model=model,
                    instructions=system_content,
                    input=user_content,
                    max_output_tokens=max_tokens,
                    reasoning={"effort": "medium"},
                )
                text = resp.output_text
                usage = resp.usage
                return text, usage

            else:
                resp = client.responses.create(
                    model=model,
                    instructions=system_content,
                    input=user_content,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
                text = resp.output_text
                usage = resp.usage
                return text, usage

        elif "anthropic" in provider:

            anthropic_config = {
                "provider": "anthropic",
                "model": provider.split("_")[1],
                "temperature": 0,
                "max_tokens": 4096,  # 50000, #4096,
                "api_key": ANTHROPIC_API_KEY,
            }
            provider = anthropic_config.get("provider", "").lower()
            max_tokens = anthropic_config.get("max_tokens", 50000)
            temperature = anthropic_config.get("temperature", 0)
            api_key = anthropic_config.get("api_key")
            model = anthropic_config.get("model")

            anthropic_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                raise ValueError(
                    "Anthropic API key not in config and ANTHROPIC_API_KEY env var not set."
                )
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            response = client.messages.create(
                model=model,
                system=system_content,
                messages=[{"role": "user", "content": user_content}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            usage = response.usage

            return response.content[0].text, usage

        elif "google" in provider:

            google_config = {
                "provider": "google",
                "model": provider.split("_")[1],
                "temperature": 0,
                "max_tokens": 50000,
                "api_key": GOOGLE_API_KEY,
            }

            provider = google_config.get("provider", "").lower()
            max_tokens = google_config.get("max_tokens", 50000)
            temperature = google_config.get("temperature", 0)
            api_key = google_config.get("api_key")
            model = google_config.get("model")
            google_api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                raise ValueError(
                    "Google API key not in config and GOOGLE_API_KEY env var not set."
                )

            last_err = None
            for attempt in range(1, 4):  # try 3 times
                try:
                    client = genai.Client(api_key=google_api_key)
                    response = client.models.generate_content(
                        model=model,
                        config=types.GenerateContentConfig(
                            system_instruction=system_content,
                            max_output_tokens=max_tokens,
                            temperature=temperature,
                        ),
                        contents=user_content,
                    )
                    usage = response.usage_metadata
                    return response.text, usage
                except Exception as e:
                    last_err = e
                    print(f"[google] attempt {attempt} failed: {e!r}")
                    if attempt == 3:
                        raise
                    time.sleep(1.0)

            raise last_err

        else:
            raise ValueError(
                "Unsupported provider. Choose from 'openai', 'anthropic', or 'google'."
            )
    except Exception as e:
        return f"An error occurred with provider {provider}: {e}"


def extract_final_variables(input_json_str):
    data = json.loads(input_json_str)

    covariates = []
    for cov in data.get("covariates", []):
        covariates.append(cov["keyword"])
    label = data.get("label", {}).get("keyword", None)

    return {"covariates": covariates, "label": label}


def get_only_derived_blocks(data):
    data = json.loads(data)
    derived_blocks = []

    for section in ["inclusion", "exclusion", "covariates", "predictor", "label"]:
        if section == "label":
            block = data.get("label")
            if block and block.get("derived", False):
                derived_blocks.append(block)
        else:
            for block in data.get(section, []):
                if block.get("derived", False):
                    derived_blocks.append(block)

    return derived_blocks


def get_analysis_type(data):
    if isinstance(data, str):
        data = data.strip()
        if data.lower().startswith("json"):
            first_brace = data.find("{")
            if first_brace != -1:
                data = data[first_brace:]
        data = json.loads(data)
    return data.get("analysis_type", None)


def get_schema(data):
    if isinstance(data, str):
        data = data.strip()
        if data.lower().startswith("json"):
            first_brace = data.find("{")
            if first_brace != -1:
                data = data[first_brace:]
        data = json.loads(data)
    return data.get("dataset", None)


def get_period_of_interest(data):
    if isinstance(data, str):
        data = data.strip()
        if data.lower().startswith("json"):
            first_brace = data.find("{")
            if first_brace != -1:
                data = data[first_brace:]
        data = json.loads(data)
    return data.get("period_of_interest", None)


def match_periods(input_periods):
    """
    Accepts:
      - a string like '1999-2002, 2011-2014'
      - OR a list/tuple like ['1999-2002', '2011-2014']
    Returns:
      - list of [start, end] windows that are fully contained in the input ranges,
        de-duplicated and sorted ascending; or None if nothing matches.
    """
    available_periods1 = [
        [2021, 2023],
        [2011, 2012],
        [2013, 2014],
        [2015, 2016],
        [2017, 2018],
        [2009, 2010],
        [2007, 2008],
        [2005, 2006],
        [2003, 2004],
        [2001, 2002],
        [1999, 2000],
        [2023, 2025],
    ]

    available_periods2 = [
        [2021, 2023],
        [2011, 2012],
        [2013, 2014],
        [2015, 2016],
        [2017, 2020],  # merged
        [2009, 2010],
        [2007, 2008],
        [2005, 2006],
        [2003, 2004],
        [2001, 2002],
        [1999, 2000],
        [2023, 2025],
    ]

    if not input_periods:
        return None
    if isinstance(input_periods, str):
        pieces = [p.strip() for p in input_periods.split(",") if p.strip()]
    elif isinstance(input_periods, (list, tuple)):
        pieces = []
        for item in input_periods:
            if isinstance(item, str) and item.strip():
                pieces.extend([p.strip() for p in item.split(",") if p.strip()])
    else:
        return None

    def match_one_range(rng_str):
        if "-" not in rng_str:
            return []
        try:
            start_input, end_input = map(int, rng_str.split("-"))
            start_input, end_input = min(start_input, end_input), max(
                start_input, end_input
            )
        except ValueError:
            return []

        if any(y in range(start_input, end_input + 1) for y in (2019, 2020)):
            available_periods = available_periods2
        else:
            available_periods = available_periods1

        return [
            [start, end]
            for start, end in available_periods
            if start_input <= start and end <= end_input
        ]

    matched = []
    for p in pieces:
        matched.extend(match_one_range(p))

    if not matched:
        return None

    # De-duplicate and sort by (start, end)
    dedup = sorted({(s, e) for s, e in matched})
    return [[s, e] for s, e in dedup]


def clean_var_name(name: str) -> str:
    """Clean variable or table name to be safe and lowercase."""
    if not isinstance(name, str):
        return ""
    name = re.sub(r"[ ,()\-\/%]", "_", name.strip().lower())
    name = re.sub(r"[^\w]", "_", name)
    return re.sub(r"_+", "_", name).strip("_")


def extract_sample_values(schema_str, variable_name):
    """Extract example sample values from schema."""
    pattern = rf"{re.escape(variable_name)}:.*?\(e\.g\., (.*?)\)"
    match = re.search(pattern, schema_str)
    return match.group(1).strip() if match else None


def filter_by_year(df, start_year, end_year):
    """Filter DataFrame rows matching a specific begin and end year."""
    return df[(df["Begin Year"] == start_year) & (df["EndYear"] == end_year)].copy()


def ensure_llm_log(title, file_path):
    """Creates an empty CSV log file with headers if it doesn't exist."""
    if not os.path.isfile(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Title" "Step",
                    "System Message",
                    "User Message",
                    "AI Response",
                ],
            )
            writer.writeheader()


def llm_log_to_csv(title, file_path, tag, system_msg, user_msg, ai_response):
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Title",
                "Step",
                "System Message",
                "User Message",
                "AI Response",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "Title": title,
                "Step": tag,
                "System Message": system_msg,
                "User Message": user_msg,
                "AI Response": ai_response,
            }
        )


def display_parsed_result(key, raw_input, max_values=3, multiline=False):
    """
    Parse and display a result row from a string or list input.

    Args:
        key (str): The original keyword.
        raw_input (str | list): A list or stringified list with 3 elements:
                                [column_name, table_name, example_values_str].
        max_values (int): Max number of example values to show.
        multiline (bool): Whether to show each value on a new line.
    """

    if isinstance(raw_input, list):
        parsed = raw_input if len(raw_input) == 3 else None
    elif isinstance(raw_input, str):
        try:
            cleaned = raw_input.strip().strip("'''").strip('"').strip()
            parsed = ast.literal_eval(cleaned)
            if not (isinstance(parsed, list) and len(parsed) == 3):
                parsed = None
        except Exception:
            parsed = None
    else:
        parsed = None

    if not parsed:
        print(
            f"[Error] Failed to process keyword '{key}': Expected a list of exactly 3 items."
        )
        return

    column_name = parsed[0]
    table_name = parsed[1]
    example_raw = parsed[2]

    if isinstance(example_raw, str):
        try:
            examples = ast.literal_eval(example_raw)
            if not isinstance(examples, list):
                examples = [example_raw]
        except Exception:
            examples = [example_raw]
    elif isinstance(example_raw, list):
        examples = example_raw
    else:
        examples = [str(example_raw)]

    examples = [e for e in examples if str(e).strip()]
    examples = examples[:max_values]
    example_text = "\n".join(examples) if multiline else ", ".join(examples)
    headers = ["Key", "Column Name", "Table Name", "Example Values"]
    row = [[key, column_name, table_name, example_text]]
    print(tabulate(row, headers=headers, tablefmt="grid"))


import json
import ast
from collections import defaultdict


def extract_keywords_and_data_sources(configs):
    result = []

    def collect_items(section):
        for item in section:
            keyword = item.get("keyword")
            if "data_sources" in item:
                result.append(
                    {"keyword": keyword, "data_sources": item["data_sources"]}
                )
            if item.get("derived") and "depends_on" in item:
                collect_items(item["depends_on"])

    for key in [
        k
        for k in configs.keys()
        if k not in {"analysis_type", "dataset", "period_of_interest"}
    ]:
        section = configs.get(key, [])
        collect_items(section)

    return result


def get_bottom_level_variables_check(input_json_str):
    if isinstance(input_json_str, str):
        input_json_str = input_json_str.strip()
        if input_json_str.lower().startswith("json"):
            first_brace = input_json_str.find("{")
            if first_brace != -1:
                input_json_str = input_json_str[first_brace:]
            else:
                raise ValueError("No JSON object found in input string.")

        if not input_json_str:
            raise ValueError(
                "Empty or invalid JSON string passed to get_bottom_level_variables"
            )

        try:
            data = json.loads(input_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e.msg}") from e
    elif isinstance(input_json_str, dict):
        data = input_json_str
    else:
        raise TypeError("Input must be a JSON string or dictionary")

    bottom_vars = set()

    def collect_variables(block):
        if not block.get("derived", False):
            bottom_vars.add(block["keyword"])
        else:
            for dep in block.get("depends_on", []):
                collect_variables(dep)

    for section in [
        k
        for k in data.keys()
        if k not in {"analysis_type", "dataset", "period_of_interest"}
    ]:
        for item in data.get(section, []):
            collect_variables(item)

    return data, sorted(bottom_vars)


def check_column_consistency(input_json_str):
    data, bottom_level_keywords = get_bottom_level_variables_check(input_json_str)

    keyword_columns = defaultdict(set)
    keyword_types = defaultdict(set)
    keyword_cycles = defaultdict(set)
    keyword_tables = defaultdict(set)
    keyword_column_table_pairs = defaultdict(set)

    def process_data_sources(keyword, sources):
        for ds in sources:
            col = ds.get("column")
            tbl = ds.get("table")
            cycle = ds.get("cycle")

            if col:
                keyword_columns[keyword].add(col)
            if tbl:
                keyword_tables[keyword].add(tbl)
            if cycle:
                keyword_cycles[keyword].add(cycle)
            if col and tbl:
                keyword_column_table_pairs[keyword].add((col, tbl))

            examples_raw = ds.get("example_values") or ds.get("example values")
            if not examples_raw:
                continue

            try:
                examples = (
                    ast.literal_eval(examples_raw)
                    if isinstance(examples_raw, str)
                    else examples_raw
                )
            except Exception:
                examples = []

            for val in examples:
                if val == "":
                    continue
                try:
                    val_type = (
                        type(ast.literal_eval(val))
                        if isinstance(val, str)
                        else type(val)
                    )
                except Exception:
                    val_type = str
                keyword_types[keyword].add(val_type)

    def collect_keyword_data(keyword, item):
        if item.get("keyword") == keyword and not item.get("derived", False):
            process_data_sources(keyword, item.get("data_sources", []))
        for dep in item.get("depends_on", []):
            collect_keyword_data(keyword, dep)

    for section in ["inclusion", "exclusion", "covariates", "predictor", "label"]:
        for item in data.get(section, []):
            for kw in bottom_level_keywords:
                collect_keyword_data(kw, item)

    # ---------- checks & warnings ---------------------------------------
    warnings = []
    all_checks_passed = True

    # 1. Column-name consistency
    inconsistent_columns = {k: v for k, v in keyword_columns.items() if len(v) > 1}
    if inconsistent_columns:
        warnings.append("⚠️ Column Name Inconsistencies Found Across Cycles:")
        for kw in sorted(inconsistent_columns):
            pair_strings = [
                f"{col} ({tbl})" for col, tbl in sorted(keyword_column_table_pairs[kw])
            ]
            warnings.append(f"  🔸 {kw}: " + ", ".join(pair_strings))
        all_checks_passed = False

    # 2. Example-type consistency
    inconsistent_types = {k: v for k, v in keyword_types.items() if len(v) > 1}
    if inconsistent_types:
        warnings.append("\n⚠️ Inconsistent Example-Value Types Found:")
        for kw in sorted(inconsistent_types):
            type_names = [t.__name__ for t in keyword_types[kw]]
            warnings.append(
                f"  🔸 {kw}: types={type_names} | cycles={sorted(keyword_cycles[kw])}"
            )
        all_checks_passed = False

    # 3. Cycle-count consistency
    cycle_counts = {k: len(v) for k, v in keyword_cycles.items()}
    unique_counts = set(cycle_counts.values())
    if len(unique_counts) > 1:
        warnings.append("\n⚠️ Uneven Number of Cycles Detected Across Keywords:")
        for kw in sorted(cycle_counts):
            warnings.append(
                f"  🔸 {kw}: {cycle_counts[kw]} cycles | tables={sorted(keyword_tables[kw])}"
            )
        all_checks_passed = False
    if warnings:
        print("\n".join(warnings))
    else:
        print("No warnings – everything looks consistent.")
    return all_checks_passed, warnings


def get_first_code_block(response):
    match = re.search(r"'''(?:R\s*)?(.*?)'''", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```(?:R\s*)?(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"'''(.*?)'''", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response.strip()


def clean_var_name(name: str) -> str:
    """Clean variable or table name to be safe and lowercase."""
    if not isinstance(name, str):
        return ""
    name = re.sub(r"[ ,()\-\/%]", "_", name.strip().lower())
    name = re.sub(r"[^\w]", "_", name)
    return re.sub(r"_+", "_", name).strip("_")


def get_variable_row(schema, df, table_name, variable_name):
    """
    Returns the row from df where 'Data File Name' matches table_name
    and clear_var_name applied to 'SAS Label' matches variable_name.
    """
    if "nhanes" in schema:
        df = df.copy()
        df["clean_label"] = df["SAS Label"].apply(clean_var_name)
        match = df[
            (df["Data File Name"] == table_name) & (df["clean_label"] == variable_name)
        ]
        if len(match) > 1:
            print(
                f"ALERT: Found {len(match)} matching rows for variable '{variable_name}' in table '{table_name}'"
            )
        if match.empty:
            print("No match found.")
            return None
        examples_str = match["Examples"].iloc[0]
        try:
            examples_list = ast.literal_eval(examples_str)
            return examples_list
        except Exception:
            print("Could not parse 'Examples' as list. Returning raw string.")
            return examples_str

    elif "aireadi" in schema:
        match = df[
            (df["table_name"].str.split(".").str[-1] == table_name)
            & (df["column_name"] == variable_name)
        ]
        if len(match) > 1:
            print(
                f"ALERT: Found {len(match)} matching rows for variable '{variable_name}' in table '{table_name}'"
            )
        if match.empty:
            print("No match found.")
            return None

        examples_str = match["values"].iloc[0]
        try:
            examples_list = ast.literal_eval(examples_str)
            return examples_list
        except Exception:
            print("Could not parse 'Examples' as list. Returning raw string.")
            return examples_str


def display_variable_metadata_with_year_and_key(schema, year, key, raw_input, examples):
    config_variabile = data_config.config_map[schema]
    cleaned = get_first_code_block(str(raw_input).strip())
    parsed = None
    try:
        parsed_dict = ast.literal_eval(cleaned)
        required_keys = config_variabile["display_input_column"]
        if all(k in parsed_dict for k in required_keys):
            parsed = [parsed_dict[k] for k in required_keys]
    except Exception:
        pass

    if not parsed:
        print(
            f"[Error] Failed to parse input for key '{key}': expected a dictionary with specific keys."
        )
        print(raw_input)
        return

    headers = config_variabile["display_output_column"]
    row = [str(year), key] + parsed + [examples]

    if schema == "aireadi":
        # print("for aireadi only 2023-2024 available")
        row[0] = "[2023, 2025]"
        if headers[-1] == "values":
            print(tabulate([row[:-1]], headers=headers[:-1], tablefmt="grid"))
        else:
            print(tabulate([row], headers=headers, tablefmt="grid"))
    else:
        selected_indices = [0, 1, 2, 4, 3, 8]
        print(
            tabulate(
                [[row[i] for i in selected_indices]],
                headers=[headers[i] for i in selected_indices],
                tablefmt="grid",
            )
        )


def make_multiple_dictionaries_grouped(
    title,
    schema,
    not_found_keywords,
    years_list,
    question,
    dictionary_path,
    schema_path,
    llm_provider,
    llm_log=None,
    safeguard=True,
):
    config_variabile = data_config.config_map[schema]
    result = {}
    model = SentenceTransformer("all-MiniLM-L6-v2")

    usage_logs = []
    alert_messages = []

    for i, keyword in enumerate(not_found_keywords, start=1):
        print(f"{i}th out of {len(not_found_keywords)}: {keyword}")
        result[keyword] = []

        for years in years_list:
            max_attempts = 2
            for attempt in range(max_attempts):
                try:
                    start_year, end_year = map(int, years)
                    df = pd.read_csv(dictionary_path)

                    if "nhanes" in schema:
                        df = filter_by_year(df, start_year, end_year)

                    if df.empty or config_variabile["keyword_column"] not in df.columns:
                        continue

                    keyword_search = (
                        df[config_variabile["keyword_column"]].fillna("").tolist()
                    )

                    embeddings = model.encode(keyword_search)
                    index = faiss.IndexFlatL2(embeddings.shape[1])
                    index.add(embeddings)

                    query_vec = model.encode([keyword])
                    k = min(40, len(df))
                    distances, indices = index.search(query_vec, k)

                    candidates = df.iloc[indices[0]].copy()

                    candidates["Similarity Score"] = 1 - (distances[0] / 2)
                    columns_to_keep = config_variabile["columns_to_keep"]
                    candidates = candidates[columns_to_keep]

                    # Filter terms (e.g., arsenic, pesticides) that may trigger commercial LLM safety filters
                    # and cause the model to refuse or block responses during automated queries.

                    words_to_drop = ["arsenic", "pesticides", "insecticides"]
                    pattern = "|".join(words_to_drop)
                    rows_with_forbidden_words = (
                        candidates.select_dtypes(include="object")
                        .apply(lambda col: col.str.contains(pattern, case=False, na=False))
                        .any(axis=1)
                    )
                    candidates = candidates[~rows_with_forbidden_words]

                    # print(candidates.to_string())
                    candidates = candidates.to_dict(orient="records")

                    user_message = f"Keyword:{keyword}, Candidates:{candidates}"
                    system_message = p.step2_get_relevant_tables(schema)
                    response, usage = generate_ai_response(
                        system_message, user_message, llm_provider
                    )
                    cost_details = calculate_cost(llm_provider, usage)
                    usage_logs.append(cost_details)

                    if llm_log:
                        llm_log_to_csv(
                            title,
                            llm_log,
                            "Step 2: Get Relevant Schema",
                            system_message,
                            user_message,
                            response,
                        )

                    try:
                        assert response is not None, "response is None"
                        code_block = get_first_code_block(
                            response.replace("json", "").replace("python", "")
                        )
                        assert code_block is not None, "code_block is None"
                        code_block = re.sub(
                            r"(:\s*)null(?=\s*[,}])", r'\1"null value"', code_block
                        )
                        clean_response = ast.literal_eval(code_block)

                    except Exception as e:
                        print("Failed during processing:")
                        print("response =", repr(response))
                        print(
                            "code_block =",
                            (
                                repr(code_block)
                                if "code_block" in locals()
                                else "<not created>"
                            ),
                        )
                        print("🔍 Error:", e)

                    if "nhanes" in schema:
                        count = 0
                        matching_files = []
                        matched_keyword = clean_response["SAS Label"]
                        for item in candidates:
                            if matched_keyword == item["SAS Label"]:
                                count += 1
                                matching_files.append(item["Data File Description"])

                        if count > 1 and safeguard:
                            filtered_candidates = [
                                item
                                for item in candidates
                                if item["SAS Label"] == matched_keyword
                            ]

                            eval_user = (
                                f"Keyword: {keyword}, Candidates: {filtered_candidates}"
                            )
                            eval_system = p.step2_3_evaluate_picked_candidate_pickone1()
                            evaluation, usage = generate_ai_response(
                                eval_system, eval_user, llm_provider
                            )
                            if llm_log:
                                llm_log_to_csv(
                                    title,
                                    llm_log,
                                    "Step 2.1.1: Same Variable from Multiple Tables",
                                    eval_system,
                                    eval_user,
                                    evaluation,
                                )

                            if get_first_code_block(evaluation) != "Yes":

                                eval_user = f"Based on the comment {evaluation}, pick the right candidate among Candidates: {filtered_candidates}"
                                eval_system = (
                                    p.step2_3_evaluate_picked_candidate_pickone2()
                                )
                                evaluation, usage = generate_ai_response(
                                    eval_system, eval_user, llm_provider
                                )
                                cost_details = calculate_cost(llm_provider, usage)
                                usage_logs.append(cost_details)

                                if llm_log:
                                    llm_log_to_csv(
                                        title,
                                        llm_log,
                                        "Step 2.1.2: Same Variable from Multiple Tables",
                                        eval_system,
                                        eval_user,
                                        evaluation,
                                    )

                            match = re.search(r"{.*}", evaluation, re.DOTALL)
                            if match:
                                dict_string = match.group(0)

                                try:
                                    clean_response = ast.literal_eval(dict_string)

                                except (ValueError, SyntaxError) as e:
                                    print(f"Error converting string to dictionary: {e}")
                            else:
                                print("No dictionary found in the string.")

                    table_name = clean_var_name(
                        clean_response.get(config_variabile["table_name_column"])
                    )

                    var_name = clean_var_name(
                        clean_response.get(config_variabile["variable_name_column"])
                    )

                    if not var_name:
                        raise ValueError(
                            f"LLM response for keyword '{keyword}' did not contain a variable name. "
                            f"Response received: {clean_response}"
                        )

                    if table_name.startswith(f"{schema}_"):
                        table_name = table_name[len(schema) + 1 :]

                    total_dic = pd.read_csv(dictionary_path)

                    values = get_variable_row(
                        schema, total_dic, table_name, var_name
                    )  # ,clean_var_name)
                    examples = ", ".join(str(x) for x in values)

                    cost_details = calculate_cost(llm_provider, usage)
                    usage_logs.append(cost_details)

                    if "aireadi" in schema:
                        # print("aireadi detected")
                        cycle = "2023-2025"
                    else:
                        cycle = f"{years[0]}-{years[1]}"

                    result[keyword].append(
                        {
                            "cycle": cycle,
                            "table": f"{schema}.{table_name}",
                            "column": var_name,
                            "example_values": values,
                        }
                    )
                    display_variable_metadata_with_year_and_key(
                        schema, years, keyword, clean_response, examples
                    )
                    break

                except Exception as e:
                    alert_message = None
                    print(
                        f"[Error] Failed to process keyword '{keyword}' for years {years}: {e}"
                    )
                    print("[📍 Full traceback:]")
                    traceback.print_exc()
                    alert_messages.append(alert_message)
                    continue
            else:

                print(
                    f"Failed to process keyword '{keyword}' for years {years} after {max_attempts} attempts."
                )
                print("[Full traceback for final failure:]")
                traceback.print_exc()
                alert_message = f"Failed to process keyword '{keyword}' for years {years} after {max_attempts} attempts."
                alert_messages.append(alert_message)
                continue

        if len(years_list) > 1 and safeguard:

            column_names = set([item["column"] for item in result[keyword]])

            if len(column_names) > 1:

                eval_user = f"For keyword {keyword}, columns are {column_names}, for a question {question}"
                eval_system = p.step2_3_evaluate_picked_candidate_pickone3()
                evaluation, usage = generate_ai_response(
                    eval_system, eval_user, llm_provider
                )

                cost_details = calculate_cost(llm_provider, usage)
                usage_logs.append(cost_details)

                if llm_log:
                    llm_log_to_csv(
                        title,
                        llm_log,
                        "Step 2.2: Multiple variables selected across cycles",
                        eval_system,
                        eval_user,
                        evaluation,
                    )

                options = ast.literal_eval(get_first_code_block(evaluation))
                multi_cycle_error1 = f"Multiple variables candidates detected for '{keyword}' across cycles: {options}"
                print(multi_cycle_error1)
                alert_messages.append(multi_cycle_error1)

                candidate_availability = {}
                found_candidate = None

                multi_cycle_error2 = (
                    "\nSearching for a candidate available in all cycles..."
                )
                print(multi_cycle_error2)
                alert_messages.append(multi_cycle_error2)

                all_found_candidates = []

                for i in options:
                    found_in_years = []

                    data_file_name = "N/A"
                    data_file_desc = "N/A"

                    for years in years_list:
                        start_year, end_year = map(int, years)
                        df = pd.read_csv(dictionary_path)
                        if "nhanes" in schema:
                            df = filter_by_year(df, start_year, end_year)

                        matching_row = df[df["SAS Label"].apply(clean_var_name) == i]

                        if not matching_row.empty:
                            found_in_years.append(years)
                            if data_file_name == "N/A":
                                data_file_name = matching_row.iloc[0]["Data File Name"]
                                data_file_desc = matching_row.iloc[0][
                                    "Data File Description"
                                ]

                    candidate_availability[i] = found_in_years

                    if len(found_in_years) == len(years_list):

                        all_found_candidates.append(i)

                    else:
                        all_cycles_set = set(map(tuple, years_list))
                        available_cycles_set = set(map(tuple, found_in_years))
                        missing_cycles = list(all_cycles_set - available_cycles_set)
                        multi_cycle_error6 = f"  - Skipping candidate '{i}' (From: '{data_file_desc}' - {data_file_name}). Missing from cycles: {missing_cycles}"
                        print(multi_cycle_error6)
                        alert_messages.append(multi_cycle_error6)

                if len(all_found_candidates) > 1:

                    eval_user = f"For keyword {keyword}, the candidates are {all_found_candidates}"
                    eval_system = p.pick_most_suitable_candidates()
                    evaluation, usage = generate_ai_response(
                        eval_system, eval_user, llm_provider
                    )

                    found_candidate = get_first_code_block(evaluation)
                    print("picked_candidate")
                    print(found_candidate)

                    cost_details = calculate_cost(llm_provider, usage)
                    usage_logs.append(cost_details)

                    if llm_log:
                        llm_log_to_csv(
                            title,
                            llm_log,
                            "Step safe guard: Evaluate the meaning of the chosen candidate and keyword among all available yearse",
                            eval_system,
                            eval_user,
                            evaluation,
                        )

                elif len(all_found_candidates) == 1:
                    found_candidate = all_found_candidates[0]

                else:
                    found_candidate = None

                multi_cycle_error3 = f"Found a candidate that is available from all cycles: '{found_candidate}'"
                multi_cycle_error4 = f"   (From: '{data_file_desc}' - {data_file_name})"
                multi_cycle_error5 = f"   If you prefer to use other candidates, consider adjusting your time period and replace {keyword} with other candidate\n"

                alert_messages.append(multi_cycle_error3)
                alert_messages.append(multi_cycle_error4)
                alert_messages.append(multi_cycle_error5)

                if found_candidate:
                    multi_cycle_error7 = f"   Rebuilding results for '{keyword}' using '{found_candidate}'."
                    print(multi_cycle_error7)
                    alert_messages.append(multi_cycle_error7)

                    result[keyword] = []
                    for years in years_list:
                        start_year, end_year = map(int, years)
                        df = pd.read_csv(dictionary_path)
                        if "nhanes" in schema:
                            df = filter_by_year(df, start_year, end_year)
                        matching_row = df[
                            df["SAS Label"].apply(clean_var_name) == found_candidate
                        ].iloc[0]
                        table_name = clean_var_name(
                            matching_row[config_variabile["table_name_column"]]
                        )
                        var_name = clean_var_name(
                            matching_row[config_variabile["variable_name_column"]]
                        )
                        cycle = f"{years[0]}-{years[1]}"

                        values = get_variable_row(
                            schema, total_dic, table_name, var_name
                        )
                        result[keyword].append(
                            {
                                "cycle": cycle,
                                "table": f"{schema}.{table_name}",
                                "column": var_name,
                                "example_values": values,
                            }
                        )
                else:
                    multi_cycle_error8 = f"\n No single candidate from {options} was available for all periods. So we will used a mix of these, please review them to make sure this is okay"
                    print(multi_cycle_error8)
                    alert_messages.append(multi_cycle_error8)
        eval_user = f"For keyword {keyword}, columns we picked are {result[keyword]}"
        eval_system = p.step2_3_evaluate_picked_candidate_pickone4()
        evaluation, usage = generate_ai_response(eval_system, eval_user, llm_provider)

        cost_details = calculate_cost(llm_provider, usage)
        usage_logs.append(cost_details)

        if llm_log:
            llm_log_to_csv(
                title,
                llm_log,
                "Step 2.3: Evaluate the meaning of the chosen candidate and keyword",
                eval_system,
                eval_user,
                evaluation,
            )

        if "yes" not in get_first_code_block(evaluation).lower():
            multi_cycle_error8 = f"The selected candidate variable may not be the suitable keyword {get_first_code_block(evaluation)}"
            print(multi_cycle_error8)
            alert_messages.append(multi_cycle_error8)

    return result, usage_logs, alert_messages


def format_schema_results(input_dict):
    formatted_result = {}

    for key, value in input_dict.items():
        column = value["column_name"]
        table = value["table_name"]

        raw_examples = value.get("example_values", "")
        example_values = [v.strip() for v in raw_examples.split(",") if v.strip()]

        formatted_result[key] = [
            {
                "cycle": "2023-2025",
                "table": f"aireadi.{table}",
                "column": column,
                "example values": example_values,
            }
        ]

    return formatted_result


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


engine = create_db_engine(db_config)
with engine.connect() as conn:
    print(conn.execute(text("SELECT 1")).fetchone())


def execute_query(sql_query):
    """Executes SQL query in the database."""
    engine = create_db_engine(db_config)
    try:
        with engine.connect() as connection:
            df = pd.read_sql(text(sql_query), connection)
            return df
    except SQLAlchemyError as e:
        return f"SQL Execution Error: {str(e)}"


def execute_sql_script(sql_script):
    engine = create_db_engine(db_config)
    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(sql_script))
        return True, "SQL script executed successfully."
    except Exception as e:
        return False, f"SQL Execution Error: {str(e)}"


def get_last_query():
    sql = "SELECT * FROM final_table;"
    df = execute_query(sql)
    return df


def split_error_and_sql(input_str):
    """
    Splits a combined error + SQL string into two parts:
    - error (everything before '[SQL:')
    - sql (everything starting from after '[SQL:')

    Returns:
        error_message (str)
        sql_query (str)
    """
    sql_marker = "[SQL:"
    split_index = input_str.find(sql_marker)

    if split_index == -1:
        raise ValueError("The string does not contain the '[SQL:' marker.")

    error_message = input_str[:split_index].strip()

    sql_query = input_str[split_index + len(sql_marker) :].strip().rstrip("]")

    return error_message, sql_query


def fix_sql_errors(
    title, schema_info, error_sql, question, llm_provider, usage_logs, llm_log=None
):
    """Attempts to fix SQL errors iteratively using schema information and logs each step."""

    max_attempts = 3
    total_attempts = 0
    safeguard_logs = []

    while total_attempts < max_attempts:

        error, sql = split_error_and_sql(error_sql)
        print("----------")
        print(f"error:{error}")

        total_attempts += 1
        print("----------")
        print(f"⚡ Attempt {total_attempts}")

        system_message = p.step3_2_debug_sql()

        user_message = f"Error: {error_sql}### Schema Information: {schema_info} ##### Original Question: {question}"

        advice, usage = generate_ai_response(system_message, user_message, llm_provider)
        cost_details = calculate_cost(llm_provider, usage)
        usage_logs.append(cost_details)
        safeguard_logs.append(advice)

        if llm_log:
            llm_log_to_csv(
                title,
                llm_log,
                "Step 3-2: Debug Plan",
                system_message,
                user_message,
                advice,
            )

        print("----------------Fix Plan Response:")
        print(advice)

        system_message = p.step3_3_debug_execute()
        user_message = f"Using this Advice: {advice}. Based on this advice I provided, fix the error  {error}, in the SQL code: {sql}. After fixing the given SQL code,  give me the correct SQL. I will also give you schema information so you can use this for troubleshooting:{schema_info} and the original question {question} "
        fix_sql, usage = generate_ai_response(
            system_message, user_message, llm_provider
        )
        cost_details = calculate_cost(llm_provider, usage)
        usage_logs.append(cost_details)
        safeguard_logs.append(fix_sql)

        final_sql = extract_sql_code(fix_sql)
        print("----------------Fixed SQL Response:")
        print(final_sql)

        if llm_log:
            llm_log_to_csv(
                title,
                llm_log,
                "Step 3-3: Debug Execute",
                system_message,
                user_message,
                final_sql,
            )

        print(f"Executing Attempt {total_attempts}...")

        last_df_attempt = execute_query(final_sql)

        if isinstance(last_df_attempt, pd.DataFrame):
            print("Success: Query returned a DataFrame.")
            break
        elif isinstance(last_df_attempt, str):
            print("SQL Error Message received.")
            error_sql = last_df_attempt
        else:
            print(f"Unexpected result type: {type(last_df_attempt)}")
            error = f"Unexpected return type: {type(last_df_attempt)}"

    return final_sql, last_df_attempt, total_attempts, safeguard_logs


def remove_final_output(sql: str) -> str:
    """
    Removes the final output query from the given SQL string.
    Specifically removes lines like:
    -- Final output
    SELECT * FROM final_table;

    Args:
        sql (str): The full SQL string.

    Returns:
        str: Cleaned SQL without the final output.
    """
    pattern = r"--\s*Final output\s*\n\s*SELECT\s+\*\s+FROM\s+final_table\s*;"

    cleaned_sql = re.sub(pattern, "", sql, flags=re.IGNORECASE)

    return cleaned_sql.strip()


import json


def get_completion_from_messages(messages, model, temperature, max_tokens):
    """Fetches AI-generated response from OpenAI."""
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response["choices"][0]["message"]["content"]


def extract_sql_code(text):
    """
    Extracts SQL code from markdown-style or plain strings prefixed with 'sql'.

    Supports:
    - ```sql ... ```
    - '''sql ... '''
    - Plain strings starting with 'sql\n'
    """

    pattern = r"(?:```|''')\s*sql\s*(.*?)(?:```|''')|(?:```|''')\s*(.*?)(?:```|''')"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        return (match.group(1) or match.group(2)).strip()

    if text.strip().lower().startswith("sql"):
        return "\n".join(text.strip().splitlines()[1:]).strip()

    return "Not found"


def ensure_lookup_table(lookup_table_path):
    """
    Checks if a CSV lookup table exists. If not, creates an empty CSV.

    Parameters:
        lookup_table_path (str): Path to the lookup table CSV file.
    """
    os.makedirs(os.path.dirname(lookup_table_path), exist_ok=True)

    if not os.path.exists(lookup_table_path):
        empty_df = pd.DataFrame()
        empty_df.to_csv(lookup_table_path, index=False)


import re


import re
import re


def weighted_generate_exclusion_report_sql(sql_script: str) -> str:
    """
    Parses an NHANES SQL script to automatically generate a report on
    included/excluded rows at each logical step.

    This version ensures that 'temp_all_ids' and 'weight_design' are always
    the first two steps in the report, while all other key tables are
    detected and sorted dynamically after them.
    """
    report_steps = []

    if re.search(
        r"CREATE(?:\s+TEMP)?\s+TABLE\s+temp_all_ids", sql_script, re.IGNORECASE
    ):
        report_steps.append(
            {
                "table": "temp_all_ids",
                "label": "Total unique participants pooled from all sources",
            }
        )
    if re.search(
        r"CREATE(?:\s+TEMP)?\s+TABLE\s+weight_design", sql_script, re.IGNORECASE
    ):
        report_steps.append(
            {
                "table": "weight_design",
                "label": "Participants with a valid survey weight (after initial filtering)",
            }
        )
    dynamic_pattern = re.compile(
        r"""
        (?:--\s*(?P<comment>.*?))?    
        \s*
        CREATE(?:\s+TEMP)?\s+TABLE\s+
        (?P<table>                  
            temp_inclusion(?:_[a-zA-Z0-9_]+)?|
            temp_exclusion(?:_[a-zA-Z0-9_]+)?|
            temp_cohort|
            temp_final_table
        )                             
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    dynamic_steps = []
    for match in dynamic_pattern.finditer(sql_script):
        comment = match.group("comment")
        table_name = match.group("table")

        if not comment:
            comment = table_name.replace("_", " ").replace("temp ", "").capitalize()

        dynamic_steps.append(
            {"table": table_name, "label": comment.strip(), "position": match.start()}
        )

    dynamic_steps.sort(key=lambda x: x["position"])
    report_steps.extend(dynamic_steps)
    if not report_steps:
        return "-- No key tables for reporting were found in the script."

    with_clauses = []
    for i, step in enumerate(report_steps):
        step_label = f"{step['label']}".replace("'", "''")
        table = step["table"]
        with_clauses.append(
            f"SELECT {i} AS step_num, '{step_label}' AS step, COUNT(*) AS count FROM {table}"
        )

    with_sql = (
        "WITH counts AS (\n    " + "\n    UNION ALL\n    ".join(with_clauses) + "\n)"
    )

    final_sql = f"""
{with_sql},
differences AS (
    SELECT
        step_num,
        step,
        count,
        LAG(count) OVER (ORDER BY step_num) AS previous_count,
        LAG(count) OVER (ORDER BY step_num) - count AS excluded_at_step
    FROM counts
)
SELECT
    step_num,
    step,
    count AS remaining_after_step,
    excluded_at_step
FROM differences
ORDER BY step_num;
""".strip()

    return final_sql


def generate_exclusion_report_sql_with_comments(sql_script: str) -> str:
    """
    Parses a SQL script with comments to generate a report on excluded rows.

    This version includes a fix to handle single quotes within comments,
    preventing SQL injection or syntax errors.
    """

    pattern = re.compile(
        r"(?:--\s*(?P<comment>.*?))?\s*CREATE TEMP TABLE (?P<table>temp_[a-zA-Z0-9_]+)",
        re.IGNORECASE,
    )

    matches = list(pattern.finditer(sql_script))

    steps = []
    for i, match in enumerate(matches):
        table = match.group("table")
        comment = match.group("comment") or f"Step {i}"

        step_label = f"{comment.strip().replace("'", "''")}"

        steps.append((i, step_label, table))

    with_clauses = [
        f"SELECT {i} AS step_num, '{step_label}' AS step, COUNT(*) AS count FROM {table}"
        for i, step_label, table in steps
    ]

    if not with_clauses:
        return "-- No temp tables found to report on."

    with_sql = (
        "WITH counts AS (\n    " + "\n    UNION ALL\n    ".join(with_clauses) + "\n)"
    )

    final_sql = f"""
{with_sql},
differences AS (
    SELECT
        step_num,
        step,
        count,
        LAG(count) OVER (ORDER BY step_num) AS previous_count,
        LAG(count) OVER (ORDER BY step_num) - count AS excluded_at_step
    FROM counts
)
SELECT
    step_num,
    step,
    count AS remaining_after_step,
    excluded_at_step
FROM differences
ORDER BY step_num;
""".strip()

    return final_sql


def extract_top_keywords(data):
    excluded_keys = {"dataset", "inclusion", "exclusion"}
    desired_keys = [key for key in data.keys() if key not in excluded_keys]
    result = []

    for section in desired_keys:
        entries = data.get(section, [])
        if isinstance(entries, dict):
            entries = list(entries.values())
        for item in entries:
            if isinstance(item, dict) and "keyword" in item:
                cleaned = clean_var_name(item["keyword"])
                result.append(cleaned)

    return result


import time
import traceback


def process_sql(
    title, master_sql, dictionary, patient_id, question, llm_provider, llm_log=None
):
    usage_logs = []
    error = False
    success, message = execute_sql_script(master_sql)
    print("master table formed")
    system_prompt = p.step3_text_to_sql(dictionary, patient_id)
    print("dictionary")
    print(dictionary)
    ai_response, usage = generate_ai_response(system_prompt, question, llm_provider)
    cost_details = calculate_cost(llm_provider, usage)
    usage_logs.append(cost_details)
    sql_query = extract_sql_code(ai_response)
    if llm_log:
        llm_log_to_csv(
            title,
            llm_log,
            "Step 3-1: Initial SQL",
            system_prompt,
            question,
            ai_response,
        )
    combined_sql = master_sql + "\n" + sql_query
    if "Error" in sql_query:
        return "sql generation failed"

    result_df_or_error = execute_query(sql_query)

    if isinstance(result_df_or_error, str) and "Error" in result_df_or_error:
        error = True
        sql_query, fixed_result, total_attempts, safeguard_log = fix_sql_errors(
            title,
            dictionary,
            result_df_or_error,
            question,
            llm_provider,
            usage_logs,
            llm_log,
        )
        return fixed_result, sql_query, error, total_attempts, usage_logs, safeguard_log

    return result_df_or_error, sql_query, error, 0, usage_logs, None


def log_row_to_csv(log_path, headers, values):
    """
    Ensures the CSV log file exists with headers, then appends a row based on values dict.

    Parameters:
        log_path (str): Full path to the log CSV file.
        headers (list): List of column headers.
        values (dict): Dictionary where keys match headers and values are logged.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    if not os.path.exists(log_path):
        with open(log_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    row = [values.get(header, "") for header in headers]

    with open(log_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def merge_question_with_metadata(question_parse, data_dict):
    def update_metadata(item):
        keyword = item.get("keyword")
        if keyword in data_dict:
            item["data_sources"] = data_dict[keyword]
        for dep in item.get("depends_on", []):
            update_metadata(dep)

    for section in [
        k
        for k in question_parse.keys()
        if k not in {"analysis_type", "dataset", "period_of_interest", "outcome"}
    ]:
        for item in question_parse.get(section, []):
            update_metadata(item)

    label_section = question_parse.get("outcome")
    if isinstance(label_section, dict):
        for _, item in label_section.items():
            update_metadata(item)
    elif isinstance(label_section, list):
        for item in label_section:
            update_metadata(item)

    return question_parse


def extract_sql_code(text):
    """
    Extracts SQL code from a given text using a two-step process.

    1. First, it searches for a block explicitly tagged with ```sql or '''sql.
    2. If no tagged block is found, it falls back to finding the first generic
       code block fenced with ``` or '''.

    Args:
        text (str): The input text containing SQL code.

    Returns:
        str: Extracted SQL code or "Not found" if no SQL code is detected.
    """

    specific_pattern = r"(?:```sql|'''sql)\s*\n(.*?)(?:```|''')"
    match = re.search(specific_pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    generic_pattern = r"(?:```|''')\s*\n(.*?)(?:```|''')"
    match = re.search(generic_pattern, text, re.DOTALL)

    return match.group(1).strip() if match else "Not found"


def extract_keywords_and_years(not_found_list):
    keywords = set()
    year_ranges = set()

    for item in not_found_list:
        keyword, year_range = item
        keywords.add(keyword)
        year_ranges.add(tuple(year_range))

    return list(keywords), [list(yr) for yr in year_ranges]


def clean_example_values(example_values_str):
    try:
        values = ast.literal_eval(example_values_str)
        if all(isinstance(v, str) for v in values):
            if all(v.replace(".", "", 1).isdigit() for v in values if v.strip()):
                return [v for v in values]
            else:
                return sorted(set(v.strip() for v in values if v.strip()))
        return values
    except Exception as e:
        print(f"Failed to parse: {example_values_str} {e}")
        return example_values_str


def process_data_structure(data):
    def process_node(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "example_values" and isinstance(value, str):
                    node[key] = clean_example_values(value)
                else:
                    process_node(value)
        elif isinstance(node, list):
            for item in node:
                process_node(item)

    data_copy = data.copy()
    process_node(data_copy)
    return data_copy


def clean_empty_fields(obj):
    if isinstance(obj, dict):
        keys_to_remove = []
        for key, value in obj.items():
            obj[key] = clean_empty_fields(value)
            if key == "depends_on" and value == []:
                keys_to_remove.append(key)
            elif key == "formula" and value is None:
                keys_to_remove.append(key)
            elif key == "processing" and (
                value is None or value.get("method") == "none"
            ):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del obj[key]

    elif isinstance(obj, list):
        return [clean_empty_fields(item) for item in obj]

    return obj


def read_json(filepath):
    """Read a JSON file and return its contents as a Python dict."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


import csv
from datetime import datetime
from pathlib import Path


def log_manager_state_to_csv_1(
    csv_path: str,
    manager,
    parsed_query_info,
    timea,
    llm,
):
    csv_path = Path(csv_path)
    file_exists = csv_path.exists()

    fieldnames = [
        "Title",
        "Question",
        "Structured Question",
        "Parsed Question",
        "Safeguard1",
        "Cost",
        "Time",
        "LLM",
    ]

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "Title": manager.title,
                "Question": parsed_query_info.question,
                "Structured Question": repr(parsed_query_info.question_structured),
                "Parsed Question": repr(parsed_query_info.question_parse),
                "Safeguard1": parsed_query_info.safeguard1,
                "Cost": parsed_query_info.cost,
                "Time": timea,
                "LLM": llm,
            }
        )


def log_manager_state_to_csv_2(
    csv_path: str,
    title,
    schema,
    key,
    default_phrase,
    key_individual,
    score,
    result,
    alert_messages,
    usage_logs,
    timea,
):
    csv_path = Path(csv_path)
    file_exists = csv_path.exists()

    fieldnames = [
        "Title",
        "Schema",
        "Group",
        "Original_word",
        "Synonym",
        "Score",
        "Result",
        "Safeguard2",
        "Cost",
        "Time",
    ]

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "Title": title,
                "Schema": schema,
                "Group": key,
                "Original_word": default_phrase,
                "Synonym": key_individual,
                "Score": score,
                "Result": result,
                "Safeguard2": alert_messages,
                "Cost": usage_logs,
                "Time": timea,
            }
        )


def log_manager_state_to_csv_3(
    csv_path: str,
    title,
    schema,
    topic,
    difficulty,
    question,
    question_structured,
    question_parse,
    variables,
    sql,
    safeguard,
    sql_error,
    sql_attempt,
    cost,
    total_time,
    review,
):
    csv_path = Path(csv_path)
    file_exists = csv_path.exists()

    fieldnames = [
        "Title",
        "Schema",
        "Topic",
        "Difficulty Level",
        "Question",
        "Question Structured",
        "Question Parse",
        "Schema Incorportation",
        "SQL",
        "Safeguard3",
        "SQL Error",
        "SQL Attempts",
        "Cost",
        "Time",
        "AI Complementary Review",
    ]

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "Title": title,
                "Schema": schema,
                "Topic": topic,
                "Difficulty Level": difficulty,
                "Question": question,
                "Question Structured": question_structured,
                "Question Parse": question_parse,
                "Schema Incorportation": variables,
                "SQL": sql,
                "Safeguard3": safeguard,
                "SQL Error": sql_error,
                "SQL Attempts": sql_attempt,
                "Cost": cost,
                "Time": total_time,
                "AI Complementary Review": review,
            }
        )
