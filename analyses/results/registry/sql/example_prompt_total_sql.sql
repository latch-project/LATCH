-- TEMP TABLE FOR "age", "age", "age", "age"
DROP TABLE IF EXISTS temp_master_age;
CREATE TEMP TABLE temp_master_age AS
SELECT patient_id, "age" AS "age"
FROM registry.patient_demographics;
-- Add index for faster joins
CREATE INDEX idx_temp_master_age ON temp_master_age (patient_id);

-- TEMP TABLE FOR "type 2 diabetes", "type 2 diabetes"
DROP TABLE IF EXISTS temp_master_diabetes_type;
CREATE TEMP TABLE temp_master_diabetes_type AS
SELECT patient_id, "diabetes_type" AS "diabetes_type"
FROM registry.diabetes_history;
-- Add index for faster joins
CREATE INDEX idx_temp_master_diabetes_type ON temp_master_diabetes_type (patient_id);

-- TEMP TABLE FOR "insulin use", "insulin use"
DROP TABLE IF EXISTS temp_master_insulin_use_status;
CREATE TEMP TABLE temp_master_insulin_use_status AS
SELECT patient_id, "insulin_use_status" AS "insulin_use_status"
FROM registry.diabetes_history;
-- Add index for faster joins
CREATE INDEX idx_temp_master_insulin_use_status ON temp_master_insulin_use_status (patient_id);

-- TEMP TABLE FOR "private insurance", "private insurance"
DROP TABLE IF EXISTS temp_master_insurance_type;
CREATE TEMP TABLE temp_master_insurance_type AS
SELECT patient_id, "insurance_type" AS "insurance_type"
FROM registry.patient_demographics;
-- Add index for faster joins
CREATE INDEX idx_temp_master_insurance_type ON temp_master_insurance_type (patient_id);

-- TEMP TABLE FOR "cholesterol", "cholesterol"
DROP TABLE IF EXISTS temp_master_hdl_cholesterol_mg_dl;
CREATE TEMP TABLE temp_master_hdl_cholesterol_mg_dl AS
SELECT patient_id, "hdl_cholesterol_mg_dl" AS "hdl_cholesterol_mg_dl"
FROM registry.metabolic_laboratory;
-- Add index for faster joins
CREATE INDEX idx_temp_master_hdl_cholesterol_mg_dl ON temp_master_hdl_cholesterol_mg_dl (patient_id);

-- TEMP TABLE FOR "microaneurysm", "microaneurysm", "microaneurysm"
DROP TABLE IF EXISTS temp_master_microaneurysm_status;
CREATE TEMP TABLE temp_master_microaneurysm_status AS
SELECT patient_id, "microaneurysm_status" AS "microaneurysm_status"
FROM registry.diabetic_retinopathy;
-- Add index for faster joins
CREATE INDEX idx_temp_master_microaneurysm_status ON temp_master_microaneurysm_status (patient_id);

-- TEMP TABLE FOR "sex", "sex"
DROP TABLE IF EXISTS temp_master_sex_at_birth;
CREATE TEMP TABLE temp_master_sex_at_birth AS
SELECT patient_id, "sex_at_birth" AS "sex_at_birth"
FROM registry.patient_demographics;
-- Add index for faster joins
CREATE INDEX idx_temp_master_sex_at_birth ON temp_master_sex_at_birth (patient_id);

-- TEMP TABLE FOR "race", "race"
DROP TABLE IF EXISTS temp_master_race_group;
CREATE TEMP TABLE temp_master_race_group AS
SELECT patient_id, "race_group" AS "race_group"
FROM registry.patient_demographics;
-- Add index for faster joins
CREATE INDEX idx_temp_master_race_group ON temp_master_race_group (patient_id);

-- TEMP TABLE FOR "diabetes duration", "diabetes duration"
DROP TABLE IF EXISTS temp_master_diabetes_duration_years;
CREATE TEMP TABLE temp_master_diabetes_duration_years AS
SELECT patient_id, "diabetes_duration_years" AS "diabetes_duration_years"
FROM registry.diabetes_history;
-- Add index for faster joins
CREATE INDEX idx_temp_master_diabetes_duration_years ON temp_master_diabetes_duration_years (patient_id);

-- TEMP TABLE FOR "smoking", "smoking"
DROP TABLE IF EXISTS temp_master_smoking_status;
CREATE TEMP TABLE temp_master_smoking_status AS
SELECT patient_id, "smoking_status" AS "smoking_status"
FROM registry.patient_demographics;
-- Add index for faster joins
CREATE INDEX idx_temp_master_smoking_status ON temp_master_smoking_status (patient_id);

-- TEMP TABLE FOR "blood pressure systolic", "blood pressure systolic", "blood pressure systolic"
DROP TABLE IF EXISTS temp_master_systolic_blood_pressure_mm_hg;
CREATE TEMP TABLE temp_master_systolic_blood_pressure_mm_hg AS
SELECT patient_id, "systolic_blood_pressure_mm_hg" AS "systolic_blood_pressure_mm_hg"
FROM registry.systemic_vitals;
-- Add index for faster joins
CREATE INDEX idx_temp_master_systolic_blood_pressure_mm_hg ON temp_master_systolic_blood_pressure_mm_hg (patient_id);

-- ALL UNIQUE PATIENT IDs
DROP TABLE IF EXISTS temp_all_ids;
CREATE TEMP TABLE temp_all_ids AS
SELECT patient_id FROM temp_master_age
UNION
SELECT patient_id FROM temp_master_diabetes_type
UNION
SELECT patient_id FROM temp_master_insulin_use_status
UNION
SELECT patient_id FROM temp_master_insurance_type
UNION
SELECT patient_id FROM temp_master_hdl_cholesterol_mg_dl
UNION
SELECT patient_id FROM temp_master_microaneurysm_status
UNION
SELECT patient_id FROM temp_master_sex_at_birth
UNION
SELECT patient_id FROM temp_master_race_group
UNION
SELECT patient_id FROM temp_master_diabetes_duration_years
UNION
SELECT patient_id FROM temp_master_smoking_status
UNION
SELECT patient_id FROM temp_master_systolic_blood_pressure_mm_hg;

-- Add index to the main ID table for the final join
CREATE INDEX idx_temp_all_ids_patient_id ON temp_all_ids (patient_id);

-- FINAL MASTER TABLE
DROP TABLE IF EXISTS final_master_table;
CREATE TABLE final_master_table AS
SELECT
    a.patient_id,
    t0."age",
    t1."diabetes_type",
    t2."insulin_use_status",
    t3."insurance_type",
    t4."hdl_cholesterol_mg_dl",
    t5."microaneurysm_status",
    t6."sex_at_birth",
    t7."race_group",
    t8."diabetes_duration_years",
    t9."smoking_status",
    t10."systolic_blood_pressure_mm_hg"
FROM temp_all_ids a
LEFT JOIN temp_master_age t0 ON a.patient_id = t0.patient_id 
LEFT JOIN temp_master_diabetes_type t1 ON a.patient_id = t1.patient_id 
LEFT JOIN temp_master_insulin_use_status t2 ON a.patient_id = t2.patient_id 
LEFT JOIN temp_master_insurance_type t3 ON a.patient_id = t3.patient_id 
LEFT JOIN temp_master_hdl_cholesterol_mg_dl t4 ON a.patient_id = t4.patient_id 
LEFT JOIN temp_master_microaneurysm_status t5 ON a.patient_id = t5.patient_id 
LEFT JOIN temp_master_sex_at_birth t6 ON a.patient_id = t6.patient_id 
LEFT JOIN temp_master_race_group t7 ON a.patient_id = t7.patient_id 
LEFT JOIN temp_master_diabetes_duration_years t8 ON a.patient_id = t8.patient_id 
LEFT JOIN temp_master_smoking_status t9 ON a.patient_id = t9.patient_id 
LEFT JOIN temp_master_systolic_blood_pressure_mm_hg t10 ON a.patient_id = t10.patient_id;

CREATE INDEX idx_final_master_patient_id    
    ON final_master_table (patient_id);
-- ========== STEP 1: Inclusion ==========

-- STEP 1.1: Includes all patients over 20 years old
CREATE TEMP TABLE temp_inclusion_step1 AS
SELECT "patient_id"
FROM final_master_table
WHERE "age" > 20;

-- STEP 1.2: From the above group, include only those with Type 2 diabetes
CREATE TEMP TABLE temp_inclusion_step2 AS
SELECT i."patient_id"
FROM temp_inclusion_step1 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."diabetes_type" = 'Type 2';

-- STEP 1.3: From the above group, include only those who use insulin
CREATE TEMP TABLE temp_inclusion_step3 AS
SELECT i."patient_id"
FROM temp_inclusion_step2 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."insulin_use_status" = 'Yes';

-- STEP 1.4: From the above group, include only those with private insurance (Commercial)
CREATE TEMP TABLE temp_inclusion_step4 AS
SELECT i."patient_id"
FROM temp_inclusion_step3 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."insurance_type" = 'Commercial';

-- ========== STEP 2: Exclusions ==========

-- STEP 2.1: Exclude patients with missing cholesterol (hdl_cholesterol_mg_dl)
CREATE TEMP TABLE temp_exclusion_step1 AS
SELECT i."patient_id"
FROM temp_inclusion_step4 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."hdl_cholesterol_mg_dl" IS NOT NULL;

-- STEP 2.2: Exclude patients with missing microaneurysm status
CREATE TEMP TABLE temp_exclusion_step2 AS
SELECT i."patient_id"
FROM temp_exclusion_step1 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."microaneurysm_status" IS NOT NULL;

-- STEP 2.3: Exclude patients with missing age
CREATE TEMP TABLE temp_exclusion_step3 AS
SELECT i."patient_id"
FROM temp_exclusion_step2 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."age" IS NOT NULL;

-- STEP 2.4: Exclude patients with missing sex
CREATE TEMP TABLE temp_exclusion_step4 AS
SELECT i."patient_id"
FROM temp_exclusion_step3 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."sex_at_birth" IS NOT NULL;

-- STEP 2.5: Exclude patients with missing race
CREATE TEMP TABLE temp_exclusion_step5 AS
SELECT i."patient_id"
FROM temp_exclusion_step4 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."race_group" IS NOT NULL;

-- STEP 2.6: Exclude patients with missing diabetes duration
CREATE TEMP TABLE temp_exclusion_step6 AS
SELECT i."patient_id"
FROM temp_exclusion_step5 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."diabetes_duration_years" IS NOT NULL;

-- STEP 2.7: Exclude patients with missing smoking status
CREATE TEMP TABLE temp_exclusion_step7 AS
SELECT i."patient_id"
FROM temp_exclusion_step6 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."smoking_status" IS NOT NULL;

-- STEP 2.8: Exclude patients with missing systolic blood pressure
CREATE TEMP TABLE temp_exclusion_step8 AS
SELECT i."patient_id"
FROM temp_exclusion_step7 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."systolic_blood_pressure_mm_hg" IS NOT NULL;

-- STEP 2.9: Exclude patients with missing diabetes type (already handled by inclusion, but for completeness)
CREATE TEMP TABLE temp_exclusion_step9 AS
SELECT i."patient_id"
FROM temp_exclusion_step8 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."diabetes_type" IS NOT NULL;

-- STEP 2.10: Exclude patients with missing insulin use status (already handled by inclusion, but for completeness)
CREATE TEMP TABLE temp_exclusion_step10 AS
SELECT i."patient_id"
FROM temp_exclusion_step9 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."insulin_use_status" IS NOT NULL;

-- STEP 2.11: Exclude patients with missing insurance type (already handled by inclusion, but for completeness)
CREATE TEMP TABLE temp_exclusion_step11 AS
SELECT i."patient_id"
FROM temp_exclusion_step10 i
JOIN final_master_table f ON i."patient_id" = f."patient_id"
WHERE f."insurance_type" IS NOT NULL;

-- ========== STEP 3: Cohort ==========

-- The final temp table in the exclusion sequence becomes temp_cohort.
CREATE TEMP TABLE temp_cohort AS
SELECT "patient_id"
FROM temp_exclusion_step11;

-- ========== STEP 4: Variables ==========

-- 4.1 Age
-- Bin age into custom categories
CREATE TEMP TABLE temp_age_binned AS
SELECT c."patient_id",
  CASE
    WHEN f."age" < 40 THEN '< 40'
    WHEN f."age" >= 40 AND f."age" < 60 THEN '>= 40 and < 60'
    WHEN f."age" >= 60 THEN '>= 60'
    ELSE NULL
  END AS "age"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- 4.2 Sex
-- Extract sex_at_birth
CREATE TEMP TABLE temp_sex AS
SELECT c."patient_id", f."sex_at_birth" AS "sex"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- 4.3 Race
-- Extract race_group
CREATE TEMP TABLE temp_race AS
SELECT c."patient_id", f."race_group" AS "race"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- 4.4 Diabetes Duration
-- Extract diabetes_duration_years
CREATE TEMP TABLE temp_diabetes_duration AS
SELECT c."patient_id", f."diabetes_duration_years" AS "diabetes_duration"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- 4.5 Smoking
-- Extract smoking_status
CREATE TEMP TABLE temp_smoking AS
SELECT c."patient_id", f."smoking_status" AS "smoking"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- 4.6 Blood Pressure Systolic
-- Bin systolic_blood_pressure_mm_hg into custom categories
CREATE TEMP TABLE temp_blood_pressure_systolic_binned AS
SELECT c."patient_id",
  CASE
    WHEN f."systolic_blood_pressure_mm_hg" < 130 THEN '< 130'
    WHEN f."systolic_blood_pressure_mm_hg" >= 130 THEN '>= 130'
    ELSE NULL
  END AS "blood_pressure_systolic"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- 4.7 Cholesterol (Predictor)
-- Extract hdl_cholesterol_mg_dl
CREATE TEMP TABLE temp_cholesterol AS
SELECT c."patient_id", f."hdl_cholesterol_mg_dl" AS "cholesterol"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- 4.8 Microaneurysm (Outcome)
-- Map microaneurysm_status to 1/0
CREATE TEMP TABLE temp_microaneurysm_mapped AS
SELECT c."patient_id",
  CASE f."microaneurysm_status"
    WHEN 'Present' THEN 1
    WHEN 'Absent' THEN 0
    ELSE NULL
  END AS "microaneurysm"
FROM temp_cohort c
JOIN final_master_table f ON c."patient_id" = f."patient_id";

-- ========== STEP 5: Final Table ==========
CREATE TEMP TABLE temp_final_table AS
SELECT
  c."patient_id",
  age_b."age",
  s."sex",
  r."race",
  dd."diabetes_duration",
  sm."smoking",
  bps."blood_pressure_systolic",
  chol."cholesterol",
  ma."microaneurysm"
FROM temp_cohort c
JOIN temp_age_binned age_b ON c."patient_id" = age_b."patient_id"
JOIN temp_sex s ON c."patient_id" = s."patient_id"
JOIN temp_race r ON c."patient_id" = r."patient_id"
JOIN temp_diabetes_duration dd ON c."patient_id" = dd."patient_id"
JOIN temp_smoking sm ON c."patient_id" = sm."patient_id"
JOIN temp_blood_pressure_systolic_binned bps ON c."patient_id" = bps."patient_id"
JOIN temp_cholesterol chol ON c."patient_id" = chol."patient_id"
JOIN temp_microaneurysm_mapped ma ON c."patient_id" = ma."patient_id";

-- ========== STEP 6: Final Output ==========
SELECT * FROM temp_final_table;