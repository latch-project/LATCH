import copy
import evaluate
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import utils
import sys
from pathlib import Path
import copy
from typing import Dict, List, Tuple, Any

sys.path.append(str(Path.cwd().parents[0]))
from config import other_config, data_config, config


def calculate_text_deviation(golden_text: str, variant_text: str) -> float:
    """
    Calculates the semantic deviation score between two text strings.

    A score of 0 means the texts are identical in meaning, while a score
    closer to 1 means they are very different.

    Args:
        golden_text: The original, ideal text string.
        variant_text: The perturbed or modified text string for comparison.
        model: The loaded SentenceTransformer model.

    Returns:
        A float representing the semantic deviation score.
    """
    if not isinstance(golden_text, str) or not isinstance(variant_text, str):
        raise TypeError("Both golden_text and variant_text must be strings.")

    model = SentenceTransformer("all-mpnet-base-v2")

    golden_embedding = model.encode(golden_text)
    variant_embedding = model.encode(variant_text)

    similarity_score = util.cos_sim(golden_embedding, variant_embedding)[0, 0].item()

    deviation_score = 1 - similarity_score

    return deviation_score


def _extract_phrases_and_default(variants: List[Any]) -> Tuple[List[str], str]:
    """
    Supports two shapes:
      1) List of lists: [ [phrase, "default"|score,...], [phrase, score,...], ... ]
      2) Flat list of strings: [ phrase0, phrase1, ... ]
    Returns (all_phrases, default_phrase)
    """
    if not variants:
        return [], ""

    if all(isinstance(v, list) for v in variants):
        phrases = [v[0] for v in variants if isinstance(v, list) and v]
        if len(variants[0]) > 1 and variants[0][1] == "default":
            default_phrase = variants[0][0]
        else:
            default_phrase = phrases[0] if phrases else ""
        return phrases, default_phrase

    phrases = [str(v) for v in variants]
    default_phrase = phrases[0] if phrases else ""
    return phrases, default_phrase


def generate_test_cases1(
    template_string: str, synonyms_dict: Dict[str, List[Any]]
) -> Dict[str, str]:
    """
    Generate test cases by substituting exactly ONE variation at a time.
    Uses the first/default phrase per key as the baseline for all other keys.

    Returns a dict mapping "key::phrase" -> rendered text (to avoid key collisions).
    """

    defaults: Dict[str, str] = {}
    phrase_lists: Dict[str, List[str]] = {}

    for key, variants in synonyms_dict.items():
        phrases, default_phrase = _extract_phrases_and_default(variants)
        if not phrases or not default_phrase:
            continue
        phrase_lists[key] = phrases
        defaults[key] = default_phrase

    out: Dict[str, str] = {}
    for key, phrases in phrase_lists.items():
        for phrase in phrases:
            if phrase == defaults[key]:
                continue
            params = copy.deepcopy(defaults)
            params[key] = phrase
            try:
                rendered = template_string.format(**params)
            except KeyError:
                continue
            out[f"{key}::{phrase}"] = rendered

    return out


def first_elements_only(synonyms_dict: Dict[str, List[Any]]) -> Dict[str, List[str]]:
    """
    For each key, return ONLY the first element of each sublist (or the strings themselves for flat lists).
    """
    result = {}
    for key, variants in synonyms_dict.items():
        if all(isinstance(v, list) for v in variants):
            result[key] = [v[0] for v in variants if isinstance(v, list) and v]
        else:
            result[key] = [str(v) for v in variants]
    return result


def defaults_only(synonyms_dict: Dict[str, List[Any]]) -> Dict[str, str]:
    """Return just the default phrase per key."""
    d = {}
    for key, variants in synonyms_dict.items():
        _, default_phrase = _extract_phrases_and_default(variants)
        if default_phrase:
            d[key] = default_phrase
    return d


def get_default(tempt, synonyms):
    default_values = {key: values[0] for key, values in synonyms.items()}
    default_text = tempt.format(**default_values)
    return default_text


import random


def generate_six_digit_number():
    """
    Generates a random 6-digit integer.

    A 6-digit number is any integer between 100,000 and 999,999, inclusive.
    This function uses random.randint() to select a number from that range.

    Returns:
        int: A random integer between 100,000 and 999,999.
    """
    return random.randint(100000, 999999)


schema_config = data_config.schema_configs


def get_result(question, years, schema, keyword):
    not_found_keywords = [keyword]
    year_list = years
    a, b, c = utils.make_multiple_dictionaries_grouped(
        schema,
        not_found_keywords,
        year_list,
        question,
        schema_config[schema]["dictionary"],
        schema_config[schema]["schema_folder"],
        "google_gemini-2.5-flash",
    )
    return a, b, c


import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def sigmoid(x, k, x0):
    return 1 / (1 + np.exp(-k * (x - x0)))


def parse_pairs(pairs):
    # If it's already a numpy array, validate shape
    if isinstance(pairs, np.ndarray):
        if pairs.ndim != 2 or pairs.shape[1] != 2:
            raise ValueError("NumPy input must have shape (n, 2).")
        x_arr = pairs[:, 0].astype(float)
        y_arr = pairs[:, 1].astype(float)
    else:
        try:
            xs, ys = [], []
            for item in pairs:
                if not (isinstance(item, (list, tuple)) and len(item) == 2):
                    raise ValueError("Each pair must be a [x, y] list/tuple.")
                x, y = float(item[0]), float(item[1])
                xs.append(x)
                ys.append(y)
            x_arr = np.asarray(xs, dtype=float)
            y_arr = np.asarray(ys, dtype=float)
        except TypeError as e:
            raise ValueError("pairs must be an iterable of [x, y].") from e

    if not np.isin(y_arr, [0, 1]).all():
        raise ValueError("All y values should be 0 or 1 for a probability fit.")
    return x_arr, y_arr


def fit_sigmoid_from_pairs(pairs):
    x_data, y_data = parse_pairs(pairs)
    order = np.argsort(x_data)
    x_data, y_data = x_data[order], y_data[order]
    corr = np.corrcoef(x_data, y_data)[0, 1] if len(np.unique(x_data)) > 1 else 0.0
    k0 = 10.0 if corr >= 0 else -10.0
    x0_0 = np.median(x_data)
    params, _ = curve_fit(
        sigmoid,
        x_data,
        y_data,
        p0=[k0, x0_0],
        bounds=([-1e3, x_data.min() - 1e3], [1e3, x_data.max() + 1e3]),
        maxfev=10000,
    )
    k_fit, x0_fit = params
    x_grid = np.linspace(x_data.min(), x_data.max(), 300)
    y_fit = sigmoid(x_grid, k_fit, x0_fit)

    print(f"Steepness (k): {k_fit:.4f}")
    print(f"Midpoint (x0): {x0_fit:.4f}")

    # Plot (single plot, default colors)
    plt.figure(figsize=(8, 5))
    plt.plot(x_data, y_data, "o", label="Data")
    plt.plot(x_grid, y_fit, linewidth=2.0, label="Fitted sigmoid")
    plt.axvline(x=x0_fit, linestyle="--", label=f"x0 = {x0_fit:.4f}")
    plt.title("Sigmoid Fit")
    plt.xlabel("Deviation Score")
    plt.ylabel("P(Outcome=1)")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.ylim(-0.1, 1.1)
    plt.legend()
    plt.show()

    return k_fit, x0_fit


def get_score(dictionary, key):
    try:
        synonym_list = dictionary[key]
    except (NameError, AttributeError, KeyError):
        print(
            "Note: Could not import 'q.synonyms1'. Using placeholder data for demonstration."
        )
        synonym_list = dictionary[key]
    default = synonym_list[0][0]
    results_data = []
    for item_list in synonym_list[1:]:
        value = item_list[0]
        try:
            score = evaluate.calculate_text_deviation(value, default)
        except (NameError, AttributeError):
            print("score problem")
            score = abs(len(value) - len(default)) / 100.0
        results_data.append({"Phrase": value, "Score": score})

    results_sorted = sorted(results_data, key=lambda x: x["Score"])
    output_string = f'"{key}": [\n'
    output_string += f'    ["{default}", "default"],\n'
    for item in results_sorted:
        phrase = item["Phrase"]
        score = item["Score"]
        output_string += f'    ["{phrase}", {score:.6f}],\n'

    output_string = output_string.rstrip(",\n") + "\n]"
    return output_string


from collections import Counter
import pprint


def get_both_results(dictionary):
    v1_all = []
    v2_all = []

    for entries in dictionary.values():
        valid = [e for e in entries if isinstance(e[1], (float, int))]
        v1_all.extend([[e[1], e[2]] for e in valid])
        v2_all.extend([[e[1], 0 if e[2] == 1 and e[3] == 1 else e[2]] for e in valid])

    summary_total = {
        "v1_total": len(v1_all),
        "v1_ones": sum(f == 1 for _, f in v1_all),
        "v1_zeros": sum(f == 0 for _, f in v1_all),
        "v2_total": len(v2_all),
        "v2_ones": sum(f == 1 for _, f in v2_all),
        "v2_zeros": sum(f == 0 for _, f in v2_all),
    }

    import pprint

    pp = pprint.PrettyPrinter(indent=2)
    print("\n📊 Summary totals:")
    pp.pprint(summary_total)
    return v1_all, v2_all


def get_results(dictionary):
    results = {}

    for key, rows in dictionary.items():
        filtered = [
            [row[1], row[2]] for row in rows if isinstance(row, list) and len(row) > 2
        ]
        results[key] = filtered

    return results


def build_text(base_text, rules=None):
    """
    Replace placeholders in base_text with updated inclusion, exclusion, and covariate text.

    Args:
        base_text (str): Template text with {inclusion}, {exclusion}, {covariate} placeholders.
        rules (list[str], optional): List of rules in the format 'type: "text"'
                                     where type is one of ['inclusion', 'exclusion', 'covariate'].

    Returns:
        str: Final formatted text.
    """
    texts = {
        "inclusion": "",
        "exclusion": "",
        "covariates": "",
        "predictor": "",
        "outcome": "",
    }

    if rules:
        for rule in rules:
            if ":" in rule:
                key, value = rule.split(":", 1)
                key = key.strip().lower()
                value = value.strip().strip('"')
                if key in texts:
                    texts[key] = " " + value

    final_text = base_text
    for placeholder, content in texts.items():
        final_text = final_text.replace("{" + placeholder + "}", content)

    return final_text


import ast
import ast
import json
import pandas as pd


def read_variables(text: str) -> pd.DataFrame:
    """
    Parse a schema-like text blob and return a tidy DataFrame of (keyword, column)
    collected from each item's data_sources and recursively from nested depends_on.

    Notes:
      - Tries JSON first, falls back to ast.literal_eval for Python-literal dict strings.
      - Skips top-level metadata keys in EXCLUDE_KEYS.
      - Inherits parent keyword for depends_on entries that omit 'keyword'.
      - Protects against cyclic depends_on graphs.
    """
    # Parse input robustly
    try:
        schema = json.loads(text)
    except Exception:
        schema = ast.literal_eval(text)

    if not isinstance(schema, dict):
        raise TypeError("Top-level schema must be a dict-like object.")

    EXCLUDE_KEYS = {"analysis_type", "period_of_interest"}
    result: dict[str, set[str]] = {}
    visited: set[int] = set()

    def collect(keyword: str, entry) -> None:
        if not isinstance(entry, dict):
            return

        # Prevent infinite recursion if depends_on introduces cycles
        obj_id = id(entry)
        if obj_id in visited:
            return
        visited.add(obj_id)

        # Collect columns from data_sources
        for ds in entry.get("data_sources") or []:
            if isinstance(ds, dict):
                col = ds.get("column")
                if col:
                    result.setdefault(keyword, set()).add(col)

        # Recurse into depends_on
        for dep in entry.get("depends_on") or []:
            if isinstance(dep, dict):
                dep_kw = dep.get(
                    "keyword", keyword
                )  # inherit parent keyword if missing
                collect(dep_kw, dep)

    # Walk all top-level list sections (except excluded metadata keys)
    for section, items in schema.items():
        if section in EXCLUDE_KEYS:
            continue
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            keyword = item.get("keyword")
            if not keyword:
                continue
            collect(keyword, item)

    # Build tidy DataFrame
    df_cols = pd.DataFrame(
        [(kw, col) for kw, cols in result.items() for col in cols],
        columns=["keyword", "column"],
    ).drop_duplicates()

    # Stable sort for readability
    if not df_cols.empty:
        df_cols = df_cols.sort_values(["keyword", "column"], ignore_index=True)

    return df_cols


import re


def read_one_var(input_file):
    df = pd.read_csv(input_file)

    selected_columns = [
        "Title",
        "Question",
        "Structured Question",
        "Years",
        "Cohort",
        "Schema Incorportation",
        "SQL",
        "Variables",
        "Statistics",
    ]
    titles = df["Title"].dropna().unique()

    # titles = sorted(titles)
    print("-------------")
    print(f"Found {len(titles)} unique titles:\n")
    print("-------------")
    for t in titles:
        print(t)

        filtered_df = df[selected_columns]
        filtered_df1 = filtered_df[filtered_df["Title"] == t]

        for idx, row in filtered_df1.iterrows():
            vars_data = str(row["Question"])
            print(vars_data)

            vars_data = str(row["Structured Question"])
            print(vars_data)

            vars_data = str(row["Cohort"])
            print(vars_data)

            vars_data = str(row["Schema Incorportation"])
            vars_data = evaluate.read_variables(vars_data)
            print(vars_data.to_string())

            # vars_data = (str(row["SQL"]))
            # print(vars_data)

            # Variables
            print("1) VARIABLES")
            vars_data = ast.literal_eval(str(row["Variables"]))
            vars_df = pd.DataFrame(vars_data)
            print(vars_df.to_string(index=False))

            # Statistics
            print("2) STATISTICS")
            s = str(row["Statistics"])
            s = re.sub(r"\bnan\b", "None", s, flags=re.IGNORECASE)
            stats_data = ast.literal_eval(s)
            stats_df = pd.DataFrame(stats_data)
            # filtered_df = stats_df[stats_df["term"].str.contains("q2", case=False, na=False)]
            print(stats_df.to_string(index=False))


def read_one_var_sql(input_file):
    df = pd.read_csv(input_file)

    selected_columns = [
        "Title",
        "Question",
        "Structured Question",
        "Years",
        "Cohort",
        "Schema Incorportation",
        "SQL",
        "Variables",
        "Statistics",
    ]
    titles = df["Title"].dropna().unique()

    titles = sorted(titles)
    print("-------------")
    print(f"Found {len(titles)} unique titles:\n")
    print("-------------")
    for t in titles:
        print(t)

        filtered_df = df[selected_columns]
        filtered_df1 = filtered_df[filtered_df["Title"] == t]

        for idx, row in filtered_df1.iterrows():
            vars_data = str(row["SQL"])
            print(vars_data)


import pandas as pd
import ast
import re


def read_repetition(input_file, expected_title_count=3):
    print("\n" + "#" * 100)
    print("Processing file:", input_file)
    print("#" * 100)

    df = pd.read_csv(input_file)

    selected_columns = [
        "Title",
        "Question",
        "Structured Question",
        "Cohort",
        "Variables",
        "SQL",
        "Statistics",
    ]

    # Check missing columns
    missing_cols = [c for c in selected_columns if c not in df.columns]
    if missing_cols:
        print("ERROR: Missing columns:", missing_cols)
        return

    df = df[selected_columns]

    # Get unique titles
    titles = df["Title"].dropna().unique()

    print("Found titles:", titles)
    print("Total unique titles:", len(titles))

    # Check expected title count
    if len(titles) != expected_title_count:
        print(f"WARNING: Expected {expected_title_count} titles, found {len(titles)}")

    # Process each title
    for t in titles:
        filtered_df = df[df["Title"] == t]

        for idx, row in filtered_df.iterrows():
            print("=" * 80)
            print(f"ROW {idx} | Title = {t}")
            print("=" * 80)

            # # Question text
            # print(str(row["Question"]))
            # print(str(row["Structured Question"]))

            # -----------------
            # VARIABLES
            # -----------------
            print("\n1) VARIABLES")

            try:
                vars_data = ast.literal_eval(str(row["Variables"]))
                vars_df = pd.DataFrame(vars_data)
                print(vars_df.to_string(index=False))
            except Exception as e:
                print("Failed to parse Variables:", e)
                print(row["Variables"])

            # -----------------
            # STATISTICS
            # -----------------
            print("\n2) STATISTICS")

            try:
                s = str(row["Statistics"])
                s = re.sub(r"\bnan\b", "None", s, flags=re.IGNORECASE)

                stats_data = ast.literal_eval(s)
                stats_df = pd.DataFrame(stats_data)
                print(stats_df.to_string(index=False))
            except Exception as e:
                print("Failed to parse Statistics:", e)
                print(row["Statistics"])

            print("\n")

            print("cohort")
            vars_data = str(row["Cohort"])
            print(vars_data)
