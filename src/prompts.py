import json
import examples
import utils


def pick_most_suitable_candidates():
    return f"""
Your goal is to pick one candidate that best describes the keyword in a given list

Response to user: Output the final keyword (string) wrapped in triple single quotes ('''   ''') with no extra commentary.
"""


def pre_review_step1_parse_request_free_text():
    return f"""
Your goal is to evaluate whether analysis request makes sense and has all the information needed. If not, we will be requesting more information from the user.

Analysis scope:
We support these: logistic regression, linear regression, cox regression, group comparison, prevalence, and mediation analysis. There are weighted versions for each (e.g., weighted logistic regression and logistic regression)
Typically we need these components for analysis: analysis type, period of interest, inclusion criteria, exclusion criteria, covariates (if applicable), predictor (if applicable), and outcome.

Outcomes should be in different forms based on the statistical analysis:
- Logistic regressions require binary outcome, 
- Linear regressions require numerical outcome, 
- Cox regression requires two outcome metrics: time to event, and binary outcome so list two outcomes for this analysis, 
- Group comparison wlil be the variable that divides the group,
- Prevalence will be the variable we are measuring the prevalence of.
- Only regresssion models will have predictors. For prevalence and group comparison analysis, variables of interest will be treated as like covariates in regressions for categorization purposes.

Dataset and Period scope:
We support either NHANES (1999-2023) or AIREADI data (2023-2025)

Other rules:
If the request is ambiguous or needs more details, please ask the user for more information.
If there are any contradictory information within the user input, ask for clarification.
Ask for more detail if thess are missing: analysis type, period of interest, inclusion criteria, exclusion criteria, outcome, or any other necessary metrics for a specified statistics analyses, to make sure that we have all the study details. 
If analysis type is missing, you can recommend one as well based on given information.

If this analysis plan is reasonable and not missing critical informtaion, say "Pass".
If it is missing critical information say "Review Required" and explain why it is not reasonable and ask questions for the user for clarification.
"""


def step1_parse_request_free_text():
    return f"""
Your goal is to convert the user's free-text request into a structured study design specification.

General rules:
- Organize the content into these components: analysis type, dataset, period of interest, inclusion criteria, exclusion criteria, variables (note: variable requirements depend on the analysis type).
- If any component is missing, set its value to None.
- Provide complete derivation, categorization, data processing, and calculation details; do not omit steps.
- If a unit appears with a variable name, preserve it exactly as written.
- Preserve all keyword and variable names exactly as provided (including spelling, casing, punctuation, and spacing). Do not normalize, reinterpret, or replace with synonyms; keep them as-is whenever possible.
- Pay close attention to logical operators (AND, OR, IF); they control the analysis logic and outcomes.

Datasets:
- Allowed datasets: NHANES, AIREADI.

Inclusion/Exclusion rules:
- Include or exclude participants only according to the user's requested conditions.
- If criteria is redundant (both inclusion exclusion) just include it in either.
- Do not include/exclude based on missing values unless the user explicitly requests this for specific variables.
- For conditions that could be framed as either inclusion or exclusion, follow the user's framing.
- If the user wants to include all participants, set inclusion to None.

Analysis type:
- Choose one of: logistic regression, linear regression, cox regression, mediation analysis, group comparison, prevalence, stratified logistic regression, weighted logistic regression, weighted linear regression, weighted cox regression, weighted group comparison, weighted prevalence, weighted stratified logistic regression.
- If a weight type is specified, denote it in parentheses, e.g., "weighted logistic regression (exam)" or "weighted logistic regression (questionnaire)". If no weight is specified, do not use a weighted analysis; the model will automatically select the most restrictive compatible weights based on the variables used.
- If the analysis type is not specified, choose the most suitable one
- Variable requirements by analysis (list items in this exact order):
  - Logistic regression: covariates (if provided); predictor; outcome (binary mapped to 1 and 0).
  - Cox regression: covariates (if provided); predictor; outcome consisting of (1) time-to-event and (2) event indicator (binary, in this order).
  - Linear regression: covariates (if provided); predictor; outcome.
  - Prevalence: grouping variables (if comparing groups); outcome (binary mapped to 1 and 0).
  - Mediation analysis: covariates (if provided), predictor; mediator; outcome.
  - Group comparison: variables being compared; outcome (the variable used to define groups).

Period of interest:
- Use the format YYYY-YYYY, e.g., 2014-2015.

This is an example of the input and expected output:

input will be:
{examples.question_free_text}

Output should be text with the following structure:
{examples.question}

Response to user: Output the final result wrapped in triple single quotes ('''   ''') with no extra commentary.
"""


def step1_parse_request():
    return f"""
Your goal is to create an organized dictionary for a study design based on the structured study design specification.

Rules for parsing input:
- Include full derivation details (e.g., categorization, binning, formula, IF/ELSE) without omitting any steps.
- For each derived variable, trace dependencies recursively until you reach the most basic variables, and list only these fundamental variables as keywords.
- Include units in the keyword if present.
- For phrases that has conditions like missing value or more/less than certain value, organize the logic separately in keyword and condition so that correct keyword can be later looked up.
- For analysis type, use the exact wording from thse input and don't omit anything.
- Make all keyword lowercase and no special symbols for consistency.
- For mapping derivations, list only the mapped labels, not the source-target pairs. Source values will be inferred later from examples. 
- For mapping derivations, if any of the mapped labels is specified as reference keep the word "reference" in the final name for clarity.
- For categorical and binary variables in covariates, name them explicitly as group names in strings.

This is an example of the input and expected output:

input will be:
{examples.question}

Output should be a JSON object with the following structure:
{examples.parsed_question}

Response to user: Output the final result wrapped in triple single quotes ('''   ''') with no extra commentary.
"""


def step2_get_relevant_tables(schema):
    if "nhanes" in schema:
        example = examples.nhanes_table_example

    elif "aireadi" in schema:
        example = examples.aireadi_table_example

    return f"""
  Your goal is to select the most relevant candidate from the provided candidates that best aligns with the given keyword from the question.
  - If any candidate matches the keyword exactly from the user question, it is the correct candidate so select it.
  - If not, follow the instruction below to make a correct choice:
  - If more information like table name is available, use that to get more context and help you pick the most accurate candidate. For example, age related information should be in demographic or patient related table, and serum levels should be in the lab or measurement table.
  - Make sure to be precise about any medical condition names. For example, pre disease X,  disease X, risk of disease X are different conditions pick the correct one.
  - If there are multiple same name candidates, pick the most relevant one to the user's question based on the description.
  - If a keyword is related to a missing value or a comparison (e.g., less than or more than some value), pick the variable that is related to the keyword. We can check for missing values or perform comparisons on that variable later. For example, for "Missing or Unknown vitamin C" or "vitamin C level more than 10%", "vitamin C" is the correct choice.
  - Pick the one that most accurately describes what the original question is looking for.
  
  {example}
  
  Use only the provided options and do not introduce new ones.

  Response to user: The full formatted final output dictionary wrapped in triple single quotes (''' ... ''') without any explanation or commentary.
    """


def step2_3_evaluate_picked_candidate_pickone1():
    return f"""
Your goal is to evaluate whether the keyword is specific enough to be narrowed down to one options. 
If keyword was found in multiple tables and was not specified which one, pick one that is most suitable for the user question and explain the reason. But if it was specified, output will be "Yes"

Your output should be a single-line decision like: "Yes" or "No not specified, I would pick Variable XX from Table YY because ...".

Response to user: The  final output must in a list format wrapped in triple single quotes (''' ... ''') without any explanation or commentary
    """


def step2_3_evaluate_picked_candidate_pickone2():
    example_format = examples.nhanes_table_example
    return f"""
Your goal is pick one candidate that is most suitable for the user question based on the provided comment.

Your output should be a single-line decision like: {example_format}

Response to user: The  final output must in a list format wrapped in triple single quotes (''' ... ''') without any explanation or commentary
    """


def step2_3_evaluate_picked_candidate_pickone3():
    return f"""
Your goal is to rank the given column names from different cycles in the order that is most suitable based on the original question.

Your output should be a single-line decision like column names in a list in the order of your recommendation: "["var1", "var2, "var3"....]".

Response to user: The  final output must in a list format wrapped in triple single quotes (''' ... ''') without any explanation or commentary
    """


def step2_3_evaluate_picked_candidate_pickone4():
    return f"""
Your goal is evaluate the picked column and its relevant information to see if this can give information about the keyword to answer a question.
You are part of the electronig health record analysis pipeline but it is possible that we get keywords from the user input that is irrelevant and we don't have the varialbes to answer all questions.
The given column we picked is what we picked among the schema we have but might not be useful so evaluate it. If the keyword seems irrelevant from the column name,  categorize it as no.

If yes, say "Yes", if not, say "No because ....."

Response to user: The  final output must in a list format wrapped in triple single quotes (''' ... ''') without any explanation or commentary
    """


def step3_text_to_sql(schema_summary, patientid):
    example_schema = json.dumps(examples.schema, indent=2)
    ordered_variables = utils.extract_top_keywords(schema_summary)

    return f"""
Your goal is to generate SQL code. 
Follow these steps to answer the researcher's question, which is the user input.
You will generate a SQL query based on the user's question and the provided schema dictionary, which includes database tables, column names, and example values.
Use PostgreSQL syntax.

SQL Writing Guidelines:

- Use "{patientid}" as the unique patient identifier.
- Always double-quote column names (e.g., "have_fever") to prevent errors.
- Use only valid column names from the schema.
- Use temporary tables to build the logic step-by-step.
- Add a clear comment above each temp table to describe its purpose.
- When categories are assigned through exact example matching, utilize allowed example strings explicitly and verify matches using strict string equality.

Step-by-Step SQL Construction:

Step 1: Inclusion
- Create a temp table called temp_inclusion using rows from final_master_table that meet the inclusion criteria.
- If no inclusion criteria are provided, include all patients from final_master_table.
- For each inclusion rule, apply it in sequence using temp tables.

Step 2: Serial Exclusions
- If no exclusion conditions are provided in the user question, skip this step.
- For each exclusion rule, apply it in sequence using temp tables.
- Each exclusion must filter the output of the previous step.
- Do not subtract exclusion tables; instead, build one step upon the next.
- Start from temp_inclusion and apply each exclusion using a direct JOIN to final_master_table plus a WHERE clause.
- Do not automatically exclude records where the values are NULLS or UNKNOWN unless specified by the prompt.  
- By default, if the exclusion criterion for variable ii is "valueX", we exclude only rows with ii = "valueX" and keep nulls. If the prompt explicitly says to exclude missing ii and values "valueX", we exclude both.

Step 3: Final Cohort
- The final temp table in the exclusion sequence becomes temp_cohort.
- This cohort is used for all further computations.

Step 4: Variables
- Process variables in the order it was presented in the schema summary
- For each variable:
  - Join to temp_cohort.
  - Use intermediate temp tables if transformations, binning, calculations or conditional logic is required.
    - If binning (e.g., tertiles or quartiles) or formulas are needed, first create a temp table for raw values, then compute cohort-based cutoffs, then assign group labels in a final predictor table.
    - For example-based categorization: do not use ILIKE/patterns/regex. Enumerate all allowed example strings and match exactly.
    
Step 5: Final Table
- Assemble temp_final_table by joining all temp tables on "{patientid}".
- The final table's variable's column order will be the following: {patientid}, {ordered_variables}

Step 6: Final Output
- End with: SELECT * FROM temp_final_table;

Example Reference

Schema:
{example_schema}

Example SQL:
{examples.sql_example(patientid)}

Your Schema Dictionary:
{schema_summary}

Response to user: Please output the final SQL query wrapped in triple single quotes ('''sql''') with no additional commentary.
"""


def step3_2_debug_sql():
    return f"""

Your goal is to help with SQL debugging. 

Given the SQL query and the reported error from the user, write a short text plan to fix this based schema information.

- Find the table that caused error and review the schema that relates to the error, including the table and column names.
- Check if table names from the relevant part mataches the schema. If not correct it based on the schema information.
- If error is related to not existing column name, check the schema and remove it.
- If error is reltaed to inconsistent column name, check both the table and column name and rename it.
- If error is related to derived variables, pay attention to the relevant variables and their derivation method specified in the schema.
- Write the plan in a clear, step-by-step format.

Response to user: Please output the plan wrapped in triple single quotes ('''  ''') with no additional commentary.
"""


def step3_3_debug_execute():
    return f"""
Your goal is to help with SQL debugging. 

You will be given:
- The full original SQL query that failed
- Advice describing the fix

Your goal is to:
- Return the corrected SQL script, after applying the recommended fix
- Try to retain and output all major steps, like inclusion, exclusion, cohort creation, covariate extraction, and final table assembly.

Response to user: Please output the corrected SQL query below, wrapped in triple single quotes ('''sql ... ''') with no additional commentary.
"""
