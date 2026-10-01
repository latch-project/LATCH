WITH counts AS (
    SELECT 0 AS step_num, 'Step 0' AS step, COUNT(*) AS count FROM temp_master_age
    UNION ALL
    SELECT 1 AS step_num, 'Step 1' AS step, COUNT(*) AS count FROM temp_master_diabetes_type
    UNION ALL
    SELECT 2 AS step_num, 'Step 2' AS step, COUNT(*) AS count FROM temp_master_insulin_use_status
    UNION ALL
    SELECT 3 AS step_num, 'Step 3' AS step, COUNT(*) AS count FROM temp_master_insurance_type
    UNION ALL
    SELECT 4 AS step_num, 'Step 4' AS step, COUNT(*) AS count FROM temp_master_hdl_cholesterol_mg_dl
    UNION ALL
    SELECT 5 AS step_num, 'Step 5' AS step, COUNT(*) AS count FROM temp_master_microaneurysm_status
    UNION ALL
    SELECT 6 AS step_num, 'Step 6' AS step, COUNT(*) AS count FROM temp_master_sex_at_birth
    UNION ALL
    SELECT 7 AS step_num, 'Step 7' AS step, COUNT(*) AS count FROM temp_master_race_group
    UNION ALL
    SELECT 8 AS step_num, 'Step 8' AS step, COUNT(*) AS count FROM temp_master_diabetes_duration_years
    UNION ALL
    SELECT 9 AS step_num, 'Step 9' AS step, COUNT(*) AS count FROM temp_master_smoking_status
    UNION ALL
    SELECT 10 AS step_num, 'Step 10' AS step, COUNT(*) AS count FROM temp_master_systolic_blood_pressure_mm_hg
    UNION ALL
    SELECT 11 AS step_num, 'Step 11' AS step, COUNT(*) AS count FROM temp_all_ids
    UNION ALL
    SELECT 12 AS step_num, 'STEP 1.1: Includes all patients over 20 years old' AS step, COUNT(*) AS count FROM temp_inclusion_step1
    UNION ALL
    SELECT 13 AS step_num, 'STEP 1.2: From the above group, include only those with Type 2 diabetes' AS step, COUNT(*) AS count FROM temp_inclusion_step2
    UNION ALL
    SELECT 14 AS step_num, 'STEP 1.3: From the above group, include only those who use insulin' AS step, COUNT(*) AS count FROM temp_inclusion_step3
    UNION ALL
    SELECT 15 AS step_num, 'STEP 1.4: From the above group, include only those with private insurance (Commercial)' AS step, COUNT(*) AS count FROM temp_inclusion_step4
    UNION ALL
    SELECT 16 AS step_num, 'STEP 2.1: Exclude patients with missing cholesterol (hdl_cholesterol_mg_dl)' AS step, COUNT(*) AS count FROM temp_exclusion_step1
    UNION ALL
    SELECT 17 AS step_num, 'STEP 2.2: Exclude patients with missing microaneurysm status' AS step, COUNT(*) AS count FROM temp_exclusion_step2
    UNION ALL
    SELECT 18 AS step_num, 'STEP 2.3: Exclude patients with missing age' AS step, COUNT(*) AS count FROM temp_exclusion_step3
    UNION ALL
    SELECT 19 AS step_num, 'STEP 2.4: Exclude patients with missing sex' AS step, COUNT(*) AS count FROM temp_exclusion_step4
    UNION ALL
    SELECT 20 AS step_num, 'STEP 2.5: Exclude patients with missing race' AS step, COUNT(*) AS count FROM temp_exclusion_step5
    UNION ALL
    SELECT 21 AS step_num, 'STEP 2.6: Exclude patients with missing diabetes duration' AS step, COUNT(*) AS count FROM temp_exclusion_step6
    UNION ALL
    SELECT 22 AS step_num, 'STEP 2.7: Exclude patients with missing smoking status' AS step, COUNT(*) AS count FROM temp_exclusion_step7
    UNION ALL
    SELECT 23 AS step_num, 'STEP 2.8: Exclude patients with missing systolic blood pressure' AS step, COUNT(*) AS count FROM temp_exclusion_step8
    UNION ALL
    SELECT 24 AS step_num, 'STEP 2.9: Exclude patients with missing diabetes type (already handled by inclusion, but for completeness)' AS step, COUNT(*) AS count FROM temp_exclusion_step9
    UNION ALL
    SELECT 25 AS step_num, 'STEP 2.10: Exclude patients with missing insulin use status (already handled by inclusion, but for completeness)' AS step, COUNT(*) AS count FROM temp_exclusion_step10
    UNION ALL
    SELECT 26 AS step_num, 'STEP 2.11: Exclude patients with missing insurance type (already handled by inclusion, but for completeness)' AS step, COUNT(*) AS count FROM temp_exclusion_step11
    UNION ALL
    SELECT 27 AS step_num, 'The final temp table in the exclusion sequence becomes temp_cohort.' AS step, COUNT(*) AS count FROM temp_cohort
    UNION ALL
    SELECT 28 AS step_num, 'Bin age into custom categories' AS step, COUNT(*) AS count FROM temp_age_binned
    UNION ALL
    SELECT 29 AS step_num, 'Extract sex_at_birth' AS step, COUNT(*) AS count FROM temp_sex
    UNION ALL
    SELECT 30 AS step_num, 'Extract race_group' AS step, COUNT(*) AS count FROM temp_race
    UNION ALL
    SELECT 31 AS step_num, 'Extract diabetes_duration_years' AS step, COUNT(*) AS count FROM temp_diabetes_duration
    UNION ALL
    SELECT 32 AS step_num, 'Extract smoking_status' AS step, COUNT(*) AS count FROM temp_smoking
    UNION ALL
    SELECT 33 AS step_num, 'Bin systolic_blood_pressure_mm_hg into custom categories' AS step, COUNT(*) AS count FROM temp_blood_pressure_systolic_binned
    UNION ALL
    SELECT 34 AS step_num, 'Extract hdl_cholesterol_mg_dl' AS step, COUNT(*) AS count FROM temp_cholesterol
    UNION ALL
    SELECT 35 AS step_num, 'Map microaneurysm_status to 1/0' AS step, COUNT(*) AS count FROM temp_microaneurysm_mapped
    UNION ALL
    SELECT 36 AS step_num, '========== STEP 5: Final Table ==========' AS step, COUNT(*) AS count FROM temp_final_table
),
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