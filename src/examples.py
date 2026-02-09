nhanes_table_example = """
For example the output would be a dictioniary with 6 items:
  {
    "SAS Label": "Gender",
    "Data File Description": "Demographic Variables & Sample Weights",
    "Data File Name" "DEMO_D"
    "Variable Name": "RIAGENDR",
    "Component": "Demographics",
    "Variable Description": "Gender of the sample person"
}
"""

aireadi_table_example = """
For example the output would be a dictioniary with 3 items: 
 {
    "column_name": "digitspan",
    "table_name": "aireadi.observation",
    "values": ["0.0", "2.0", "1.0", "", "", "", "", "", "", ""]
}
"""

question_free_text = """
Use NHANES data from 2011-2016. 
Include whose demographic a is equal or more than 20 and who said "Yes" to a questionaire "have you had condition abc".
Exclude who has missing demographic variable a, missing demographic variable b, and participants with physiological state x, and condition x present defined as (blood lab a (g/dL) <= 12.0 AND measurement b (kg) <= 50)
I want to evaluate the effect of vitamin xyz intake on outcome xyz using a logistic regression model. 
Please take into account health score (mg*kg), demographic variable c, and alphabet group xyz when doing this analysis. 
I will give me more instructionis on how to process data:
health score (mg*kg) calculated as (health metric a (mg) * 2) * ((health metric b (kg)/ 3)) then categorized into quartiles (Q1: <25% Q2: ≥25 and <50% Q3: ≥50 and <75% Q4: ≥75%)
alphabet group xyz categorized as binary "group alpha" and "group none alpha",
vitamin xyz intake categorize as 3 groups in tertiles. (T1: <33.3% T2: ≥33.3 and <66.6% T3: ≥66.6%)
outcome xyz defined as binary based on meeting any of the following criteria:
(1) metric xyz < 20 when metric xyz defined for 4 cases: 
If condition xyz = "A" and category xyz = "B", then metric xyz = 100 * serum xyz / 200  
If condition xyz ≠ "A" and category xyz = "B", then metric xyz = 100 * serum xyz / 300  
If condition xyz = "A" and category xyz ≠ "B", then metric xyz = 100 * serum xyz / 400  
If condition xyz ≠ "A" and category xyz ≠ "B", then metric xyz = 100 * serum xyz / 500
or  (2) lab xyz >= 50 - defined as (lab xy * lab z)
"""


question = """
Analysis Type: logistic regression

Dataset: NHANES

Period of Interest: 2011-2016

Inclusion Criteria:
- demographic variable a >= 20 
- have you had condition abc = Yes

Exclusion Criteria:
- missing demographic variable a, 
- missing demographic variable b,
- participants with physiological state x 
- condition x present defined as:
    blood lab a (g/dL) <= 12.0 AND measurement b (kg) <= 50

Covariates:
- health score (mg*kg) calculated as:
  (health metric a (mg) * 2) * (health metric b (kg) / 3)
  categorized into quartiles:
    Q1: <25% Q2: ≥25 and <50% Q3: ≥50 and <75% Q4: ≥75%
- demographic variable c, 
- alphabet group xyz categorized as:
  "group alpha",
  "group non alpha"

Predictor:
- vitamin xyz intake categorize as 3 groups in tertiles:
  T1: <33.3% T2: ≥33.3 and <66.6% T3: ≥66.6%

Outcome:
- outcome xyz  = 1 if (1) or (2) is met; 0 otherwise
  (1) metric xyz < 20 when metric xyz defined for 4 cases: 
  If condition xyz = "A" and category xyz = "B":
    metric xyz = 100 * serum xyz / 200  
  If condition xyz ≠ "A" and category xyz = "B":
    metric xyz = 100 * serum xyz / 300  
  If condition xyz = "A" and category xyz ≠ "B":
    metric xyz = 100 * serum xyz / 400  
  If condition xyz ≠ "A" and category xyz ≠ "B":
    metric xyz = 100 * serum xyz / 500
or
  (2) lab xyz >= 50, defined as:
    lab xyz = lab xy * lab z
"""


parsed_question = """
{
  "analysis_type": "logistic regression",
  "dataset": "NHANES",
  "period_of_interest": "2011-2016",
  "inclusion": [
    {
      "keyword": "demographic variable a",
      "derived": false,
      "condition": ">= 20"
    },
    {
      "keyword": "have you had condition abc",
      "derived": false,
      "condition": "=Yes"
    }
  ],
  "exclusion": [
    {
      "keyword": "demographic variable a",
      "derived": false,
      "condition": "is_na"
    },
    {
      "keyword": "demographic variable b",
      "derived": false,
      "condition": "is_na"
    },
    {
      "keyword": "participants with physiological state x",
      "derived": false
    },
    {
      "keyword": "condition x present",
      "derived": true,
      "depends_on": [
        {
          "keyword": "blood lab a (g/dL)",
          "condition": "<= 12.0",
          "derived": false
        },
        {
          "keyword": "measurement b (kg)",
          "condition": "<= 50.0",
          "derived": false
        }
      ],
      "derivation": [
        {
          "step": 1,
          "derivation_method": {
            "type": "boolean_and",
            "criteria": [
              "blood lab a (g/dL) <= 12.0",
              "measurement b (kg) <= 50"
            ],
          }
        }
      ]
    }
  ],
  
  "covariates": [
    {
      "keyword": "health score (mg*kg)",
      "derived": true,
      "depends_on": [
        {
          "keyword": "health metric a (mg)",
          "derived": false
        },
        {
          "keyword": "health metric b (kg)",
          "derived": false
        }
      ],
      "derivation": [
        {
          "step": 1,
          "derivation_method": {
            "type": "formula",
            "description": "health score (mg*kg) = (health metric a (mg) * 2) * ((health metric b (kg) / 3)",
          }
        },
        {
          "step": 2,
          "derivation_method": {
            "type": "binning",
            "strategy": "quantiles",
            "num_bins": 4,
            "labels": ["Q1: <25%", "Q2: ≥25 and <50%", "Q3: ≥50 and <75%", "Q4: ≥75%"],
          }
        }
      ]
    },
    {
      "keyword": "demographic variable c",
      "derived":  false
    },
    {
      "keyword": "alphabet group xyz",
      "derived": true,
      "depends_on": [
        {
          "keyword": "alphabet group xyz",
          "derived":  false
        }
      ],
      "derivation": [
        {
          "step": 1,
          "derivation_method": {
            "type": "mapping",
            "labels": {
              "group alpha",
              "group non alpha" 
            },
          }
        }
      ]
    }
  ],
  "predictor": [
    {
      "keyword": "vitamin xyz intake",
      "derived": true,
      "depends_on": [
        {
          "keyword": "vitamin xyz intake",
          "derived": false
        }
      ],
      "derivation": [
        {
          "step": 1,
          "derivation_method": {
            "type": "binning",
            "strategy": "tertiles",
            "num_bins": 3,
            "labels": ["T1: <33.3%", "T2: ≥33.3 and <66.6%", "T3: ≥66.6%"],
          }
        }
      ]
    }
  ],
  "outcome": [
    {
      "keyword": "outcome xyz",
      "derived": true,
      "depends_on": [
        {
          "keyword": "serum xyz",
          "derived": false
        },
        {
          "keyword": "condition xyz",
          "derived": false
        },
        {
          "keyword": "category xyz",
          "derived": false
        },
        {
          "keyword": "lab xy",
          "derived": false
        },
        {
          "keyword": "lab z",
          "derived": false
        }
      ],
      "derivation": [
        {
          "step": 1,
          "derivation_method": {
            "type": "formula",
            "description": "metric xyz = 100 * serum xyz / D, where D depends on condition xyz and category xyz",
            "logic": [
              {
                "condition1": "condition xyz = 'A' and category xyz = 'B'",
                "formula1": "100 * serum xyz / 200"
              },
              {
                "condition2": "condition xyz ≠ 'A' and category xyz = 'B'",
                "formula2": "100 * serum xyz / 300"
              },
              {
                "condition3": "condition xyz = 'A' and category xyz ≠ 'B'",
                "formula3": "100 * serum xyz / 400"
              },
              {
                "condition4": "condition xyz ≠ 'A' and category xyz ≠ 'B'",
                "formula4": "100 * serum xyz / 500"
              }
            ],
            "output": "metric xyz"
          }
        },
        {
          "step": 2,
          "derivation_method": {
            "type": "formula",
            "description": "lab xyz = lab xy * lab z",
          }
        },
        {
          "step": 3,
          "derivation_method": {
            "type": "boolean_or",
            "criteria": [
              {
                "condition": "metric xyz < 20"
              },
              {
                "condition": "lab xyz >= 50"
              }
            ],
          },
          {
          "step": 4,
          "derivation_method": {
            "type": "mapping",
            "labels": [
              "1",
              "0"
            ]
          }
        }
      ]
    }
  ]
}
"""
schema = {
    "analysis_type": "logistic_regression",
    "period_of_interest": "2011-2016",
    "dataset": "NHANES",
    "inclusion": [
        {
            "keyword": "demographic variable a",
            "derived": False,
            "condition": ">= 20",
            "table": "final_master_table",
            "column": "demographic_variable_a",
            "examples": ["22", "23", "29", "31", "34"],
        },
        {
            "keyword": "have you had condition abc",
            "derived": False,
            "condition": "=Yes",
            "table": "final_master_table",
            "column": "have_you_had_condition_abc",
            "examples": ["Yes", "No", "Maybe"],
        },
    ],
    "exclusion": [
        {
            "keyword": "demographic variable a",
            "derived": False,
            "condition": "is_na",
            "table": "final_master_table",
            "column": "demographic_variable_a",
            "examples": ["A", "B", "C"],
        },
        {
            "keyword": "demographic variable b",
            "derived": False,
            "condition": "is_na",
            "table": "final_master_table",
            "column": "demographic_variable_b",
            "examples": ["A", "B", "C"],
        },
        {
            "keyword": "participants with physiological state x",
            "derived": False,
            "table": "final_master_table",
            "column": "physiological_state_x",
            "examples": ["No", "Yes"],
        },
        {
            "keyword": "condition x present",
            "derived": True,
            "depends_on": [
                {
                    "keyword": "blood lab a (g/dL)",
                    "derived": False,
                    "condition": "<= 12.0",
                    "table": "final_master_table",
                    "column": "blood_lab_a_g_dl",
                    "examples": ["10.5", "10.8", "10.9", "11.0", "11.2"],
                },
                {
                    "keyword": "measurement b (kg)",
                    "derived": False,
                    "condition": "<= 50.0",
                    "table": "final_master_table",
                    "column": "measurement_b_kg",
                    "examples": ["45.6", "47.5", "48.0", "49.0", "49.5"],
                },
            ],
            "derivation": [
                {
                    "step": 1,
                    "derivation_method": {
                        "type": "boolean_and",
                        "criteria": [
                            "blood lab a (g/dL) <= 12.0",
                            "measurement b (kg) <= 50",
                        ],
                    },
                }
            ],
        },
    ],
    "covariates": [
        {
            "keyword": "health score (mg*kg)",
            "derived": True,
            "depends_on": [
                {
                    "keyword": "health metric a (mg)",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "health_metric_a_mg",
                    "examples": ["22", "23", "29", "31", "34"],
                },
                {
                    "keyword": "health metric b (kg)",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "health_metric_b_kg",
                    "examples": ["22", "23", "29", "31", "34"],
                },
            ],
            "derivation": [
                {
                    "step": 1,
                    "derivation_method": {
                        "type": "formula",
                        "description": "health score (mg*kg) = (health metric a (mg) * 2) * (health metric b (kg) / 3)",
                    },
                },
                {
                    "step": 2,
                    "derivation_method": {
                        "type": "binning",
                        "strategy": "quantiles",
                        "num_bins": 4,
                        "labels": [
                            "Q1: <25%",
                            "Q2: ≥25 and <50%",
                            "Q3: ≥50 and <75%",
                            "Q4: ≥75%",
                        ],
                    },
                },
            ],
        },
        {
            "keyword": "demographic variable c",
            "derived": False,
            "table": "final_master_table",
            "column": "demographic_variable_c",
            "examples": ["22", "23", "29", "31", "34"],
        },
        {
            "keyword": "alphabet group xyz",
            "derived": True,
            "depends_on": [
                {
                    "keyword": "alphabet group xyz",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "alphabet_group_xyz",
                    "examples": [
                        "group alpha",
                        "group beta",
                        "group gamma",
                        "group delta",
                    ],
                }
            ],
            "derivation": [
                {
                    "step": 1,
                    "derivation_method": {
                        "type": "mapping",
                        "labels": ["group alpha", "group non alpha"],
                    },
                }
            ],
        },
    ],
    "predictor": [
        {
            "keyword": "vitamin xyz intake",
            "derived": True,
            "depends_on": [
                {
                    "keyword": "vitamin xyz intake",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "vitamin_xyz",
                    "examples": ["8.2", "9.6", "9.8", "9.9", "10.0"],
                }
            ],
            "derivation": [
                {
                    "step": 1,
                    "derivation_method": {
                        "type": "binning",
                        "strategy": "tertiles",
                        "num_bins": 3,
                        "labels": ["T1: <33.3%", "T2: ≥33.3 and <66.6%", "T3: ≥66.6%"],
                    },
                }
            ],
        }
    ],
    "outcome": [
        {
            "keyword": "outcome xyz",
            "derived": True,
            "depends_on": [
                {
                    "keyword": "serum xyz",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "serum_xyz",
                    "examples": ["82.5", "88.7", "97.6", "99.1", "100.0"],
                },
                {
                    "keyword": "condition xyz",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "condition_xyz",
                    "examples": ["A", "B", "C", "D"],
                },
                {
                    "keyword": "category xyz",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "category_xyz",
                    "examples": ["A", "B", "C", "D"],
                },
                {
                    "keyword": "lab xy",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "lab_xy",
                    "examples": ["10", "11", "12", "13", "14"],
                },
                {
                    "keyword": "lab z",
                    "derived": False,
                    "table": "final_master_table",
                    "column": "lab_z",
                    "examples": ["2", "2.5", "2.6", "2.7", "2.8"],
                },
            ],
            "derivation": [
                {
                    "step": 1,
                    "derivation_method": {
                        "type": "formula",
                        "description": "metric xyz = 100 * serum xyz / D, where D depends on condition xyz and category xyz",
                        "logic": [
                            {
                                "condition1": "condition xyz = 'A' and category xyz = 'B'",
                                "formula1": "100 * serum xyz / 200",
                            },
                            {
                                "condition2": "condition xyz ≠ 'A' and category xyz = 'B'",
                                "formula2": "100 * serum xyz / 300",
                            },
                            {
                                "condition3": "condition xyz = 'A' and category xyz ≠ 'B'",
                                "formula3": "100 * serum xyz / 400",
                            },
                            {
                                "condition4": "condition xyz ≠ 'A' and category xyz ≠ 'B'",
                                "formula4": "100 * serum xyz / 500",
                            },
                        ],
                        "output": "metric xyz",
                    },
                },
                {
                    "step": 2,
                    "derivation_method": {
                        "type": "formula",
                        "description": "lab xyz = lab xy * lab z",
                    },
                },
                {
                    "step": 3,
                    "derivation_method": {
                        "type": "boolean_or",
                        "criteria": [
                            {"condition": "metric xyz < 20"},
                            {"condition": "lab xyz >= 50"},
                        ],
                    },
                },
                {
                    "step": 4,
                    "derivation_method": {"type": "mapping", "labels": ["1", "0"]},
                },
            ],
        }
    ],
}


def sql_example(patientid):
    return f"""
-- ========== STEP 1: Inclusion ==========

-- STEP 1.1: Includes all patients demographic_variable_a 20 or older
CREATE TEMP TABLE temp_inclusion_step1 AS
SELECT "{patientid}"
FROM final_master_table
WHERE "demographic_variable_a" >= 20;

-- STEP 1.2: From the above group, include only those who have had condition abc
CREATE TEMP TABLE temp_inclusion_step2 AS
SELECT i."{patientid}"
FROM temp_inclusion_step1 i
JOIN final_master_table f ON i."{patientid}" = f."{patientid}"
WHERE f."have_you_had_condition_abc" LIKE '%Yes%';

-- ========== STEP 2: Exclusions ==========

-- STEP 2.1: Exclude patients with missing demographic_variable_a
CREATE TEMP TABLE temp_exclusion_step1 AS
SELECT i."{patientid}"
FROM temp_inclusion_step2 i
JOIN final_master_table f ON i."{patientid}" = f."{patientid}"
WHERE f."demographic_variable_a" IS NOT NULL;

-- STEP 2.2: Exclude patients with missing demographic_variable_b
CREATE TEMP TABLE temp_exclusion_step2 AS
SELECT i."{patientid}"
FROM temp_exclusion_step1 i
JOIN final_master_table f ON i."{patientid}" = f."{patientid}"
WHERE f."demographic_variable_b" IS NOT NULL;

-- STEP 2.3: Exclude participants with physiological state x
CREATE TEMP TABLE temp_exclusion_step3 AS
SELECT i."{patientid}"
FROM temp_exclusion_step2 i
JOIN final_master_table f ON i."{patientid}" = f."{patientid}"
WHERE f."physiological_state_x" IS NULL
   OR f."physiological_state_x" NOT IN ('Yes');

-- STEP 2.4: Exclude patients with Condition X (low blood lab a and measurement b)
CREATE TEMP TABLE temp_exclusion_step4 AS
SELECT i."{patientid}"
FROM temp_exclusion_step3 i
JOIN final_master_table f ON i."{patientid}" = f."{patientid}"
WHERE f."blood_lab_a_g_dl" > 12.0
   OR f."measurement_b_kg" > 50
   OR f."blood_lab_a_g_dl" IS NULL
   OR f."measurement_b_kg" IS NULL;

-- ========== STEP 3: Cohort ==========

-- The final temp table in the exclusion sequence becomes temp_cohort.
CREATE TEMP TABLE temp_cohort AS
SELECT "{patientid}"
FROM temp_exclusion_step4;

-- ========== STEP 4: Variables ==========

-- 4.1 Health Score
-- Calculate health score from inputs for cohort
CREATE TEMP TABLE temp_health_score AS
SELECT c."{patientid}",
       ((f."health_metric_a_mg" * 2.0) * (f."health_metric_b_kg" / 3.0)) AS "health_score"
FROM temp_cohort c
JOIN final_master_table f ON c."{patientid}" = f."{patientid}";

-- Compute quartile cutoffs for health score within cohort
CREATE TEMP TABLE temp_health_score_cutoffs AS
SELECT
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "health_score") AS q1,
  PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY "health_score") AS q2,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "health_score") AS q3
FROM temp_health_score;

-- Assign health score quartile group
CREATE TEMP TABLE temp_health_score_quartiles AS
SELECT "{patientid}",
  CASE
    WHEN "health_score" IS NULL THEN NULL
    WHEN "health_score" < (SELECT q1 FROM temp_health_score_cutoffs) THEN 'Q1'
    WHEN "health_score" < (SELECT q2 FROM temp_health_score_cutoffs) THEN 'Q2'
    WHEN "health_score" < (SELECT q3 FROM temp_health_score_cutoffs) THEN 'Q3'
    ELSE 'Q4'
  END AS "health_score"
FROM temp_health_score;

-- 4.2 Demographic variable C
-- Extract demographic_variable_c status
CREATE TEMP TABLE temp_demographic_variable_c AS
SELECT c."{patientid}", f."demographic_variable_c"
FROM temp_cohort c
JOIN final_master_table f ON c."{patientid}" = f."{patientid}";

-- 4.3 Alphabet Group XYZ
-- Map alphabet group xyz to binary
CREATE TEMP TABLE temp_alphabet_group_xyz AS
SELECT c."{patientid}",
  CASE f."alphabet_group_xyz"
    WHEN 'group alpha' THEN 'group alpha'
    WHEN 'group beta' THEN 'group non alpha'
    WHEN 'group gamma' THEN 'group non alpha'
    WHEN 'group delta' THEN 'group non alpha'
    ELSE NULL
  END AS "alphabet_group_xyz"
FROM temp_cohort c
JOIN final_master_table f ON c."{patientid}" = f."{patientid}";

-- 4.4 Vitamin intake XYZ
-- Extract vitamin intake variable from cohort
CREATE TEMP TABLE temp_vitamin_xyz AS
SELECT c."{patientid}", f."vitamin_xyz"
FROM temp_cohort c
JOIN final_master_table f ON c."{patientid}" = f."{patientid}";

-- Calculate tertile cutoffs for vitamin intake within cohort
CREATE TEMP TABLE temp_vitamin_xyz_cutoffs AS
SELECT
  PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY "vitamin_xyz") AS tertile1,
  PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY "vitamin_xyz") AS tertile2
FROM temp_vitamin_xyz;

-- Assign patients to vitamin intake tertile groups
CREATE TEMP TABLE temp_vitamin_xyz_tertile AS
SELECT "{patientid}",
  CASE
    WHEN "vitamin_xyz" IS NULL THEN NULL 
    WHEN "vitamin_xyz" < (SELECT tertile1 FROM temp_vitamin_xyz_cutoffs) THEN 'T1'
    WHEN "vitamin_xyz" < (SELECT tertile2 FROM temp_vitamin_xyz_cutoffs) THEN 'T2'
    ELSE 'T3'
  END AS "vitamin_xyz"
FROM temp_vitamin_xyz;

-- 4.5 Outcome XYZ
-- Compute metric_xyz
CREATE TEMP TABLE temp_metric_xyz AS
SELECT c."{patientid}",
  CASE
    WHEN f."condition_xyz" = 'A' AND f."category_xyz" = 'B' THEN (100 * f."serum_xyz" / 200.0)
    WHEN f."condition_xyz" != 'A' AND f."category_xyz" = 'B' THEN (100 * f."serum_xyz" / 300.0)
    WHEN f."condition_xyz" = 'A' AND f."category_xyz" != 'B' THEN (100 * f."serum_xyz" / 400.0)
    ELSE (100 * f."serum_xyz" / 500.0)
  END AS "metric_xyz"
FROM temp_cohort c
JOIN final_master_table f ON c."{patientid}" = f."{patientid}";

-- Compute lab_xyz = lab_xy * lab_z
CREATE TEMP TABLE temp_lab_xyz AS
SELECT c."{patientid}",
       (f."lab_xy" * f."lab_z") AS "lab_xyz"
FROM temp_cohort c
JOIN final_master_table f ON c."{patientid}" = f."{patientid}";

-- Determine outcome xyz
CREATE TEMP TABLE temp_outcome_xyz AS
SELECT c."{patientid}",
  CASE
    WHEN m."metric_xyz" < 20 OR l."lab_xyz" >= 50 THEN 1
    ELSE 0
  END AS "outcome_xyz"
FROM temp_cohort c
JOIN temp_metric_xyz m ON c."{patientid}" = m."{patientid}"
JOIN temp_lab_xyz l ON c."{patientid}" = l."{patientid}";

-- ========== STEP 5: Final Output ==========
CREATE TEMP TABLE temp_final_table AS
SELECT 
  c."{patientid}",
  hs."health_score",
  dc."demographic_variable_c",
  ag."alphabet_group_xyz",
  pred."vitamin_xyz",
  l."outcome_xyz"
FROM temp_cohort c
JOIN temp_health_score_quartiles hs ON c."{patientid}" = hs."{patientid}"
JOIN temp_demographic_variable_c dc ON c."{patientid}" = dc."{patientid}"
JOIN temp_alphabet_group_xyz ag ON c."{patientid}" = ag."{patientid}"
JOIN temp_vitamin_xyz_tertile pred ON c."{patientid}" = pred."{patientid}"
JOIN temp_outcome_xyz l ON c."{patientid}" = l."{patientid}";

-- ========== STEP 6: View Output ==========
SELECT * FROM temp_final_table;
"""
