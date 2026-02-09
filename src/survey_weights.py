interview_weight_column_map = {
    "1999-2000": ["demo", "full_sample_4_year_interview_weight", 4.0],
    "2001-2002": ["demo_b", "full_sample_4_year_interview_weight", 4.0],
    "2003-2004": ["demo_c", "full_sample_2_year_interview_weight", 2.0],
    "2005-2006": ["demo_d", "full_sample_2_year_interview_weight", 2.0],
    "2007-2008": ["demo_e", "full_sample_2_year_interview_weight", 2.0],
    "2009-2010": ["demo_f", "full_sample_2_year_interview_weight", 2.0],
    "2011-2012": ["demo_g", "full_sample_2_year_interview_weight", 2.0],
    "2013-2014": ["demo_h", "full_sample_2_year_interview_weight", 2.0],
    "2015-2016": ["demo_i", "full_sample_2_year_interview_weight", 2.0],
    "2017-2018": ["demo_j", "full_sample_2_year_interview_weight", 2.0],
    "2017-2020": ["p_demo", "full_sample_interview_weight", 3.2],
    "2021-2023": ["demo_l", "full_sample_2_year_interview_weight", 2.0],
}
exam_weight_column_map = {
    "1999-2000": ["demo", "full_sample_4_year_mec_exam_weight", 4.0],
    "2001-2002": ["demo_b", "full_sample_4_year_mec_exam_weight", 4.0],
    "2003-2004": ["demo_c", "full_sample_2_year_mec_exam_weight", 2.0],
    "2005-2006": ["demo_d", "full_sample_2_year_mec_exam_weight", 2.0],
    "2007-2008": ["demo_e", "full_sample_2_year_mec_exam_weight", 2.0],
    "2009-2010": ["demo_f", "full_sample_2_year_mec_exam_weight", 2.0],
    "2011-2012": ["demo_g", "full_sample_2_year_mec_exam_weight", 2.0],
    "2013-2014": ["demo_h", "full_sample_2_year_mec_exam_weight", 2.0],
    "2015-2016": ["demo_i", "full_sample_2_year_mec_exam_weight", 2.0],
    "2017-2018": ["demo_j", "full_sample_2_year_mec_exam_weight", 2.0],
    "2017-2020": ["p_demo", "full_sample_mec_exam_weight", 3.2],
    "2021-2023": ["demo_l", "full_sample_2_year_mec_exam_weight", 2.0],
}

psu_column_map = {
    "1999-2000": ["demo", "masked_variance_pseudo_psu"],
    "2001-2002": ["demo_b", "masked_variance_pseudo_psu"],
    "2003-2004": ["demo_c", "masked_variance_pseudo_psu"],
    "2005-2006": ["demo_d", "masked_variance_pseudo_psu"],
    "2007-2008": ["demo_e", "masked_variance_pseudo_psu"],
    "2009-2010": ["demo_f", "masked_variance_pseudo_psu"],
    "2011-2012": ["demo_g", "masked_variance_pseudo_psu"],
    "2013-2014": ["demo_h", "masked_variance_pseudo_psu"],
    "2015-2016": ["demo_i", "masked_variance_pseudo_psu"],
    "2017-2018": ["demo_j", "masked_variance_pseudo_psu"],
    "2017-2020": ["p_demo", "masked_variance_pseudo_psu"],
    "2021-2023": ["demo_l", "masked_variance_pseudo_psu"],
}

stratum_column_map = {
    "1999-2000": ["demo", "masked_variance_pseudo_stratum"],
    "2001-2002": ["demo_b", "masked_variance_pseudo_stratum"],
    "2003-2004": ["demo_c", "masked_variance_pseudo_stratum"],
    "2005-2006": ["demo_d", "masked_variance_pseudo_stratum"],
    "2007-2008": ["demo_e", "masked_variance_pseudo_stratum"],
    "2009-2010": ["demo_f", "masked_variance_pseudo_stratum"],
    "2011-2012": ["demo_g", "masked_variance_pseudo_stratum"],
    "2013-2014": ["demo_h", "masked_variance_pseudo_stratum"],
    "2015-2016": ["demo_i", "masked_variance_pseudo_stratum"],
    "2017-2018": ["demo_j", "masked_variance_pseudo_stratum"],
    "2017-2020": ["p_demo", "masked_variance_pseudo_stratum"],
    "2021-2023": ["demo_l", "masked_variance_pseudo_stratum"],
}


def assign_verdicts(input_data, non_full_sample_df, exam_lab_tables):
    """
    Assigns verdicts ('exam', 'questionnaire', or weight group name) for each keyword
    based on associated table names and weight group mappings.

    Args:
        input_data (dict): keyword -> list of table names
        non_full_sample_df (pd.DataFrame): must contain 'Table Names' and 'Weight Group'
        exam_lab_tables (Iterable): list or set of known 'exam' or 'lab' table names

    Returns:
        tuple:
            - dict: keyword -> verdict
            - dict: table_name (short) -> weight group
    """
    # Build mapping from table name → weight group
    table_to_group = {}
    for _, row in non_full_sample_df.iterrows():
        for table in row["Table Names"]:
            short_table = table.lower().strip().split(".")[-1]
            table_to_group[short_table] = row["Weight Group"]

    # Normalize exam/lab tables to short format
    exam_lab_tables = set(t.lower().strip().split(".")[-1] for t in exam_lab_tables)

    # Determine verdicts
    verdicts = {}

    for keyword, tables in input_data.items():
        short_tables = [t.lower().strip().split(".")[-1] for t in tables]
        table_groups = {
            table_to_group.get(t) for t in short_tables if t in table_to_group
        }
        table_groups = {g for g in table_groups if g is not None}

        if len(table_groups) == 1:
            verdicts[keyword] = list(table_groups)[0]
            # print(verdicts[keyword])
        else:
            all_in_exam = all(t in exam_lab_tables for t in short_tables)
            verdicts[keyword] = "exam" if all_in_exam else "questionnaire"
            # print(verdicts[keyword])

    return verdicts, table_to_group


from collections import defaultdict


def get_weights_for_verdict(
    verdict,
    years,
    interview_weight_column_map,
    exam_weight_column_map,
    input_data,
    table_to_group,
    final_weights_df,
    verdicts,
):
    results = []

    # Step 1: Turn year ranges into lookup keys like "2011-2012"
    year_labels = [f"{start}-{end}" for start, end in years]

    if verdict == "questionnaire":
        if len(year_labels) == 1 and year_labels[0] in ("1999-2000", "2001-2002"):

            if year_labels == "1999-2000":
                results.append(("demo", "full_sample_2_year_interview_weight", 4.0))

            elif year_labels == "2001-2002":
                results.append(("demo_b", "full_sample_2_year_interview_weight", 4.0))

        else:
            for y in year_labels:
                if y in interview_weight_column_map:
                    table, weight_col, coeff = interview_weight_column_map[y]
                    results.append((table, weight_col, coeff))
    elif verdict == "exam":
        if len(year_labels) == 1 and year_labels[0] in ("1999-2000", "2001-2002"):

            if year_labels == "1999-2000":
                results.append(("demo", "full_sample_2_year_mec_exam_weight", 4.0))

            elif year_labels == "2001-2002":
                results.append(("demo_b", "full_sample_2_year_mec_exam_weight", 4.0))

        else:
            for y in year_labels:
                if y in exam_weight_column_map:
                    table, weight_col, coeff = exam_weight_column_map[y]
                    results.append((table, weight_col, coeff))
    else:
        # For other groups like audiometry, voc, etc.
        # Step 1: Find all relevant short table names from input_data
        relevant_tables = []
        for keyword, tables in input_data.items():
            if verdicts.get(keyword) == verdict:
                relevant_tables.extend(
                    [t.lower().strip().split(".")[-1] for t in tables]
                )

        relevant_groups = set()
        for t in relevant_tables:
            g = table_to_group.get(t)
            if g:
                relevant_groups.add(g)

        # Step 2: From final_weights_df, find rows matching those groups
        for _, row in final_weights_df.iterrows():
            if row["Weight Group"] in relevant_groups:
                for table in row["Table Names"]:
                    short_table = table.lower().strip().split(".")[-1]
                    if short_table in relevant_tables:
                        results.append(
                            (table, row["Weight Column Name"], row["Years Covered"])
                        )

    return results


def generate_non_numeric_check_queries(
    df, schema, patient_col="respondent_sequence_number"
):
    queries = []
    for _, row in df.iterrows():
        weight_col = row["Weight Column Name"]
        tables = row["Table Names"]
        for table in tables:
            query = f"""
-- Check for non-numeric values in {weight_col} from {table}
SELECT {patient_col}, {weight_col}
FROM {schema}.{table}
WHERE {weight_col}::TEXT !~ '^\\d+(\\.\\d+)?$';
"""
            queries.append(query.strip())
    return queries


def generate_column_existence_checks(
    df,
    schema,
    patient_col="respondent_sequence_number",
):
    queries = []

    for _, row in df.iterrows():
        tables = row["Table Names"]
        for table in tables:

            query = f"""
-- Check if column '{patient_col}' exists in {schema}.{table}
SELECT 
    '{table}' AS table_name,
    column_name
FROM information_schema.columns
WHERE table_schema = '{schema}'
  AND table_name = '{table}'
  AND column_name = '{patient_col}';
"""
            queries.append(query.strip())
    return queries


def get_restriction_summary_table_sql(
    verdict_to_weights,
    schema,
    patient_id_col="respondent_sequence_number",
    output_table="restriction_summary",
):
    verdict_ctes = {}
    individual_sets = []

    for verdict, weights in verdict_to_weights.items():
        union_parts = []
        for table, col, coeff in weights:
            union_parts.append(f"""
                SELECT DISTINCT {patient_id_col}
                FROM {schema}.{table}
                WHERE {col} IS NOT NULL
                """)
        union_sql = "\nUNION\n".join(union_parts)
        cte = f"{verdict}_ids AS (\n{union_sql}\n)"
        verdict_ctes[verdict] = cte
        individual_sets.append(verdict)

    # ALL intersection CTE
    all_verdicts = list(verdict_ctes.keys())
    join_clause = f"{all_verdicts[0]}_ids"
    for other in all_verdicts[1:]:
        join_clause = f"({join_clause} INNER JOIN {other}_ids USING ({patient_id_col}))"

    all_cte = f"""
    all_ids AS (
        SELECT DISTINCT {patient_id_col}
        FROM {join_clause}
    )
    """

    verdict_ctes["all"] = all_cte

    # Build final summary query
    summary_queries = []
    for verdict in individual_sets:
        summary_queries.append(f"""
            SELECT
                '{verdict}' AS verdict,
                COUNT(DISTINCT v.{patient_id_col}) AS verdict_count,
                COUNT(DISTINCT a.{patient_id_col}) AS overlap_with_all,
                ROUND(
                    100.0 * COUNT(DISTINCT a.{patient_id_col}) / NULLIF(COUNT(DISTINCT v.{patient_id_col}), 0),
                    1
                ) AS pct_overlap_with_all
            FROM {verdict}_ids v
            LEFT JOIN all_ids a ON v.{patient_id_col} = a.{patient_id_col}
            """)

    summary_union_sql = "\nUNION ALL\n".join(summary_queries)

    final_sql = f"""
    -- Drop existing table
    DROP TABLE IF EXISTS {output_table};

    -- Create summary
    CREATE TABLE {output_table} AS
    WITH
    {',\n'.join(verdict_ctes.values())}
    {summary_union_sql};

    -- Preview
    SELECT * FROM {output_table}
    ORDER BY pct_overlap_with_all DESC;
    """

    return final_sql


def generate_adjusted_weight_sql(
    weight_entries, schema, temp_table_prefix="temp_master"
):
    """
    Generate SQL for a temp table combining cycle-adjusted survey weights.

    Parameters:
        verdict (str): e.g. "fasting"
        weight_entries (list): List of (table, weight_column, coefficient)
        schema (str): Database schema name
        temp_table_prefix (str): Prefix for the temp table name

    Returns:
        str: SQL string
    """
    total_coeff = sum(coeff for _, _, coeff in weight_entries)
    temp_table_name = f"{temp_table_prefix}_weight"

    union_queries = []
    for table, col, coeff in weight_entries:
        sql = f"""
SELECT respondent_sequence_number, 
       ({col} * {coeff} / {total_coeff}) AS survey_weight
FROM {schema}.{table}
WHERE {col} IS NOT NULL"""
        union_queries.append(sql.strip())

    union_all_sql = "\nUNION ALL\n".join(union_queries)

    full_sql = f"""
-- TEMP TABLE FOR weight
DROP TABLE IF EXISTS {temp_table_name};

CREATE TEMP TABLE {temp_table_name} AS
{union_all_sql};

""".strip()

    return full_sql


def generate_temp_psu_stratum_sql(years, psu_map, stratum_map, schema):
    sql_lines = [
        "-- TEMP TABLE FOR PSU and Stratum",
        "DROP TABLE IF EXISTS temp_psu_stratum;",
        "CREATE TEMP TABLE temp_psu_stratum AS",
    ]

    union_blocks = []
    for start, end in years:
        key = f"{start}-{end}"
        if key not in psu_map or key not in stratum_map:
            raise ValueError(f"Year range {key} not found in provided maps.")

        psu_table, psu_col = psu_map[key]
        stratum_table, stratum_col = stratum_map[key]

        # Sanity check
        if psu_table != stratum_table:
            raise ValueError(
                f"Mismatch in tables for year {key}: {psu_table} vs {stratum_table}"
            )

        full_table = f"{schema}.{psu_table}"
        union_block = f"""SELECT respondent_sequence_number, 
       {psu_col} AS masked_variance_pseudo_psu,
       {stratum_col} AS masked_variance_pseudo_stratum
FROM {full_table}"""
        union_blocks.append(union_block)

    sql_lines.extend(
        "UNION ALL\n" + block if i != 0 else block
        for i, block in enumerate(union_blocks)
    )

    sql_lines[-1] += ";"

    return "\n".join(sql_lines)


def merge_weight_and_design_tables(weight_sql: str, psu_stratum_sql: str) -> str:
    final_sql = []

    # Step 1: Add both source temp table SQLs
    final_sql.append("-- STEP 1: Create temp_master_weight")
    final_sql.append(weight_sql.strip())
    final_sql.append("\n-- STEP 2: Create temp_psu_stratum")
    final_sql.append(psu_stratum_sql.strip())

    # Step 2: Join into final table
    final_sql.append("""
-- STEP 3: Create final weight+design table
DROP TABLE IF EXISTS weight_design;
CREATE TABLE weight_design AS
SELECT 
    s.respondent_sequence_number,
    s.masked_variance_pseudo_psu,
    s.masked_variance_pseudo_stratum,
    w.survey_weight
FROM temp_psu_stratum s
INNER JOIN temp_master_weight w
  ON s.respondent_sequence_number = w.respondent_sequence_number;


""")

    return "\n\n".join(final_sql)


def generate_non_numeric_checks_for_selected_groups(
    df, groups, schema, patient_col="respondent_sequence_number"
):
    inner_queries = []

    # Filter for selected groups
    df_filtered = df[df["Weight Group"].isin(groups)]

    for _, row in df_filtered.iterrows():
        weight_col = row["Weight Column Name"]
        tables = row["Table Names"]
        for table in tables:
            sql = f"""
-- Check for non-numeric values in {weight_col} from {table}
SELECT 
    '{table}' AS source_table,
    '{weight_col}' AS weight_column,
    {weight_col}::TEXT AS weight_value
FROM {schema}.{table}
WHERE {weight_col} IS NOT NULL
  AND {weight_col}::TEXT !~ '^\\d+(\\.\\d+)?$'
"""
            inner_queries.append(sql.strip())

    combined_union = "\nUNION ALL\n".join(inner_queries)

    wrapped_query = f"""
SELECT DISTINCT
    source_table,
    weight_column,
    weight_value
FROM (
{combined_union}
) AS non_numeric_weights;
""".strip()

    return wrapped_query
