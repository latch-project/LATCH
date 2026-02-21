in_001 = [
    'inclusion: "The study will include all individuals whose age in years at screening was 30 years or older who have complete data on both serum albumin (g/dL) and diabetes affected eyes/had retinopathy"'
]
out_001 = [
    'exclusion: "Exclude participants if any required field is missing (serum albumin, glycoprotein HbA1c (%), diabetic retinopathy status, gender, race/Hispanic origin, age at screening, or age when first told diabetes. Participants will also be excluded if their age in years at screening is less than 30 years old, or age when first told the patient had diabetes was before age 30, or had uncertain diabetes status. Uncertainty is based on their answer to the question “Has a doctor ever told you that you have diabetes?” and if they answer as "borderline" and  either have a missing glycohemoglobin (HbA1c) value or an glycohemoglobin (HbA1c) below 6.5%"'
]
pred_001 = [
    'predictor: "The main predictor in the analysis will be serum albumin (g/dL), categorized into quartiles(%) Q1: <25, Q2: ≥25 and <50, Q3: ≥50 and <75, Q4: ≥75"'
]
outome_001 = [
    'outcome: "The outcome variable will be the presence or absence of diabetic retinopathy, based on responses to the question “diabetes affected eyes had retinopathy?”, coded as 1 for yes and 0 for no"'
]
covar_001 = [
    'covariates:"We will adjust the analysis for potential confounding factors including gender, age in years at screening, and race/Hispanic origin, which will be categorized as White, Black, Mexican American, or Other"'
]
in_002 = [
    'inclusion: "Include all individuals whose age in years at screening is 30 years or older, who answered yes to a question has a doctor ever told you that you have diabetes, who have a non-missing age when first told they had diabetes that is not less than 30 and not greater than age at screening, who have non-missing serum albumin (g/dL) and glycoprotein HbA1c (%), and who additionally satisfy the consistency rule that (age at screening minus age when first told diabetes) is at least 1 year"'
]
out_002 = [
    'exclusion: "Exclude participants if any required field is missing (serum albumin, glycoprotein HbA1c (%), retinopathy status, gender, race/Hispanic origin, age at screening, or age when first told diabetes), or if age when first told diabetes is less than 30 or greater than age at screening, or if glycohemoglobin HbA1c (%) is less than 5.0 or greater than 20.0, or if serum albumin (g/dL) is less than 1.0 or greater than 6.0"'
]
pred_002 = [
    'predictor:"The main predictor will be a single Index ABC, calculated as serum albumin (g/dL) divided by glycoprotein HbA1c (%), and then multiplied by 1.2 if gender is Female and multiplied by 0.8 if gender is Male, and categorized into three groups using fixed cutpoints: low (<0.45), medium (0.45 to <0.60), and high (>=0.60)"'
]
outome_002 = [
    'outcome:"The outcome variable will be diabetic retinopathy, coded as 1 if diabetes affected eyes/had retinopathy is yes and coded as 0 if it is no; participants with any response other than yes or no will be 0"'
]
covar_002 = [
    'covariates:"We will adjust for gender, race/Hispanic origin categorized as White, Black, Mexican American, or Other, age in years at screening categorized as 30-49, 45-60, 61-74, and >=75, age when first told diabetes categorized as 30-39, 40-49, and >=50, and an additional interaction covariate defined as the product of HbA1c (%) and an indicator for female gender (1 for female and 0 for else"'
]
in_0021 = [
    'inclusion: "The study will include individuals whose age in years at screening is 30 or older, who answered yes to a question has a doctor ever told you that you have diabetes, whose age when first told the patient had diabetes is 30 or older and not greater than age at screening, and whose glycoprotein HbA1c (%) is 6.5 or greater"'
]
out_0021 = [
    'exclusion: "Participants will be excluded if any required field is missing (serum albumin (g/dL), glycoprotein HbA1c (%), gender, race/Hispanic origin, age in years at screening, age when first told the patient had diabetes, or diabetic retinopathy status), or if age in years at screening is less than 30, or if age when first told the patient had diabetes is less than 30 or greater than age at screening, or if diabetes status is uncertain defined as answering "Borderline" to a question "has a doctor ever told you that you have diabetes" combined with either glycohemoglobin HbA1c (%) missing or below 6.5, or if glycohemoglobin HbA1c (%) is outside the allowable range of 3.0 to 20.0, or if serum albumin (g/dL) is outside the allowable range of 1.0 to 6.0""'
]
pred_0021 = [
    'predictor:"The main predictor will be a single composite Metric ABC, calculated as serum albumin (g/dL) divided by glycoprotein HbA1c (%), then multiplied by 1.1 if gender is female and multiplied by 0.9 if gender is male, and finally log-transformed Metric ABC; participants with log-transformed Metric ABC less than or equal to 0 will be excluded"'
]
outome_0021 = [
    'outcome:"The outcome variable will be binary diabetic retinopathy status coded as 1 only if diabetes affected eyes/had retinopathy is yes and glycoprotein HbA1c (%) is 7.0 or greater, and coded as 0 only if diabetes affected eyes/had retinopathy is no and glycoprotein HbA1c (%) is less than 7.0; all other combinations will be coded as 0"'
]
covar_0021 = [
    'covariates:"We will adjust for gender, race/Hispanic origin categorized as White, Black, Mexican American, or Other, age in years at screening included as a continuous variable and as an indicator for age 60 or older, and a diabetes-duration covariate calculated as age in years at screening minus age when first told the patient had diabetes, with diabetes duration truncated to a maximum of 40 years and participants with negative duration excluded"'
]
in_003 = [
    'inclusion: "Include all individuals whose age in years at screening is 30 years or older and whose glycoprotein HbA1c (%) is not less than the median glycoprotein HbA1c (%) calculated among participants of the same race/Hispanic origin and the same gender who were 30 years or older at screening"'
]
out_003 = [
    'exclusion: "Exclude participants if any required field is missing (serum albumin, glycoprotein HbA1c (%), retinopathy status, gender, race/Hispanic origin, age at screening, or age when first told diabetes), and additionally exclude participants whose serum albumin (g/dL) is below the 20th percentile of serum albumin (g/dL) calculated among included participants of the same race/Hispanic origin and whose age in years at screening is greater than or equal to 30"'
]
pred_003 = [
    'predictor: "The main predictor will be Index ABC, defined as the participants serum albumin (g/dL) divided by the mean serum albumin (g/dL) among study participants of the same race/Hispanic origin whose age in years at screening is greater than or equal to 45 and less than or equal to 59"'
]
outome_003 = [
    'outcome: "The outcome variable will be retinopathy risk status, coded as 1 if the participant answered yes to diabetes affected eyes/had retinopathy and their glycoprotein HbA1c (%) is not less than the 75th percentile of  glycoprotein HbA1c (%) calculated among study participants of the same gender and whose age in years at screening is greater than or equal to 60, and coded as 0 otherwise"'
]
covar_003 = [
    'covariates: "We will adjust for gender, race/Hispanic origin, age in years at screening, and two glycemic covariates: (1) an age standardized glycoprotein HbA1c (%) covariate defined as the participants glycoprotein HbA1c (%) minus the mean glycoprotein HbA1c (%) among study participants whose age in years at screening is greater than or equal to 45 and less than or equal to 59, and (2) a race standardized HbA1c indicator defined as whether the participants HbA1c (%) is greater than or equal to the median HbA1c (%) within their race/Hispanic origin group"'
]
in_0031 = [
    'inclusion:"Include all individuals whose age in years at screening is 30 years or older and whose glycoprotein HbA1c (%) is not less than the median glycoprotein HbA1c (%) calculated among participants of the same race/Hispanic origin and the same gender who were 30 years or older at screening"'
]
out_0031 = [
    'exclusion: "Exclude participants if any required field is missing (serum albumin, glycoprotein HbA1c (%), retinopathy status, gender, race/Hispanic origin, age at screening, or age when first told diabetes), and additionally exclude participants whose serum albumin (g/dL) is below the median serum albumin (g/dL) calculated among study participants of the same gender unless their glycoprotein HbA1c (%) is not less than the 75th percentile of glycohemoglibin HbA1c (%) calculated within their race/Hispanic origin group"'
]
pred_0031 = [
    'predictor:"The main predictor will be a Index ABC defined as serum albumin (g/dL) divided by the mean serum albumin (g/dL) within the participants race/Hispanic origin group. Then, within each gender group, the average of these race-adjusted albumin values is calculated across all participants of that gender. Finally, each participant\'s race-adjusted albumin value is divided by this gender specific average, and the resulting value is defined as Index ABC"'
]
outome_0031 = [
    'outcome:"The outcome variable will be elevated retinopathy risk coded as 1 only if diabetes affected eyes/had retinopathy is yes and the participants glycoprotein HbA1c (%) is not less than the race/Hispanic origin specific median glycohemoglobin HbA1c (%) among participants whose age in years at screening is 30 or older, and coded as 0 otherwise"'
]
covar_0031 = [
    'covariates:"We will adjust for gender, age in years at screening, race/Hispanic origin, and two covariates: (1) glycohemoglobin HbA1c deviation covariate defined as the participants glycoprotein HbA1c (%) minus the mean HbA1c (%) within their gender group, and (2) a diabetes-duration deviation covariate defined as (age in years at screening minus age when first told the patient had diabetes) minus the mean of this duration within their race/Hispanic origin group"'
]
in_004 = [
    'inclusion: "Include participants who are not excluded from the eligible cohort, where exclusion applies only to those who cannot be determined to not violate the following rule: the participants age in years at screening is not less than 30, however, even if a participant would otherwise be excluded for not meeting this rule, the participant is immediately retained unless it is simultaneously true that their glycoprotein HbA1c (%) is not less than the median glycohemoglobin HbA1c (%) within their race/Hispanic origin group and their gender is not female"'
]
out_004 = [
    'exclusion: "Exclude participants who are not in the set of individuals who cannot be determined to not have complete analytic information, where complete information is defined as non-missing serum albumin (g/dL), non-missing diabetic retinopathy status, and non-missing glycoprotein HbA1c (%)retinopathy status, gender, race/Hispanic origin, age at screening, or age when first told diabetes; nevertheless, if a participant would be excluded due to missingness, they are immediately re-included unless it is simultaneously true that their race/Hispanic origin is not White and their age in years at screening is not less than 60""'
]
pred_004 = [
    'predictor: "The main predictor will be Index ABC, initially defined as serum albumin (g/dL) divided by the mean serum albumin (g/dL) within the participants race/Hispanic origin group, but this value is not left unmodified unless it is not true that the participant cannot be determined to not have high glycemia; high glycemia is defined as glycoprotein HbA1c (%) not less than the 75th percentile within the participants gender group; if high glycemia is present, Index ABC is multiplied by 1.5, except that this multiplication is immediately reversed if the participant has been told by a doctor that they have diabetes"'
]
outome_004 = [
    'outcome: "The outcome variable will be a retinopathy risk status coded as 1 only if the participant is not in the protected state; the protected state is true if it is not false that the participant cannot be determined to not be low-risk, where low-risk is defined as either answering No to diabetes affected eyes/had retinopathy or having glycoprotein HbA1c (%) not greater than the median HbA1c (%) within their race/Hispanic origin group within the analytic cohort; however, even if a participant would otherwise be coded as 1, they are immediately coded as 0 unless it is simultaneously true that they answered yes to doctor told you have diabetes and their age in years at screening is not less than 45"'
]
covar_004 = [
    'covariates: "We will adjust for gender, race/Hispanic origin, age in years at screening, and a Deviation ABC covariate computed as glycoprotein HbA1c (%) minus the mean glycoprotein HbA1c (%) within the participants gender group, but this Deviation ABC covariate is not applied as computed unless it is not true that the participant cannot be determined to not belong to the buffered group, where buffered is defined as having been told by a doctor that they have diabetes; if buffered is true, the deviation ABC covariate is immediately set to 0"'
]
in_0041 = [
    'inclusion: "The study population will consist of individuals who cannot be classified as ineligible after sequential evaluation of eligibility rules, where ineligibility is defined as being younger than 30 years at screening or having an age when first told the patient had diabetes that exceeds age at screening; among those not ineligible, inclusion further requires that the participant is not below the race/Hispanic origin specific median glycoprotein HbA1c (%) calculated from the previously included cohort unless the participant answered yes to a question has a doctor ever told you that you have diabetes"'
]
out_0041 = [
    'exclusion: "Participants will be excluded if they are members of the set of individuals who cannot be determined to satisfy diabetes-status consistency or analytic completeness, where diabetes-status inconsistency is defined only when a participant answered borderline to the doctor told you have diabetes question and simultaneously has glycoprotein HbA1c (%) that is missing or below the race/Hispanic origin specific median HbA1c (%) calculated from the post-inclusion cohort, or when required data on serum albumin (g/dL), diabetic retinopathy status, gender, or race/Hispanic origin are missing""'
]
pred_0041 = [
    'predictor:"The primary predictor will be serum albumin index ABC, defined by first dividing serum albumin (g/dL) by the mean serum albumin within the participants race/Hispanic origin group calculated from the final analytic cohort, and then dividing that value by the median of the race/Hispanic origin group\'s serum albumin values within the participants gender group, resulting in a single continuous predictor"'
]
outome_0041 = [
    'outcome:"The outcome variable will be elevated diabetic retinopathy risk, coded as 1 for participants who are not classified as lacking evidence of diabetes-related eye disease, where lack of evidence is defined as answering no to diabetes affected eyes/had retinopathy or having glycoprotein HbA1c (%) below the 75th percentile of HbA1c (%) calculated within the participants race/Hispanic origin group using the analytic cohort; all other participants are coded as 0"'
]
covar_0041 = [
    'covariates:"The analysis will adjust for gender, race/Hispanic origin categorized as White, Black, Mexican American, or Other, and age in years at screening. Age in years at screening will be incorporated both as a continuous variable and as a hierarchical indicator distinguishing participants who are not younger than 60 years from those younger than 60 years. In addition, the model will adjust for two covariates that are defined only for participants who remain in the final analytic cohort: first, an age-group standardized glycoprotein HbA1c (%) deviation, defined as the participants HbA1c (%) minus the mean HbA1c (%) of participants in the same age group; and second, a race/Hispanic origin standardized diabetes-duration deviation, defined as the participants diabetes duration (age at screening minus age when first told the patient had diabetes) minus the mean diabetes duration of participants in the same race/Hispanic origin group"'
]
in_0 = [
    'inclusion: "Only include individuals whose glycohemoglobin (%) level is not less than one-tenth of their current age in years at screening multiplied by their ratio of their respective race/Hispanic orgin in all categories"'
]
in_2 = [
    'inclusion: "Only include individuals whose glycohemoglobin (%) level is not less than one-tenth of their current age in years at screening"'
]
out_1 = [
    'exclusion: "We will not include people who did not say yes to a question doctor told you have diabetes or failed to have values for serum albumin (g/dL) or diabetes affected eyes/had retinopathy'
]
pred_1 = [
    'predictor: "The predictor will be serum albumin (g/dL) categorized as low, normal, and high based on percentages and make normal has middle 60%"'
]
pred_2 = [
    'predictor: "The predictor is the risk level: risk-1 is when if the absence of the failure to meet poor control (glycohemoglobin Hba1c (%) greater than or equal to 7.0 (%)) is not present, and diabetes duration (age in years at screening - age when first told the patient had diabetes) is not longer than the cohort-wide 25th percentile duration, unless serum albumin (g/dl) value is not less than the 90th percentile of the distribution for their respective race/Hispanic origin group. risk-2 is if not risk-1 and gender is not prevented from being non-female and the record is not free from the absence of retinopathy (diabetes affected eyes/had retinopathy = no) being present, unless age in years at screening is not prevented from being below the cohort median age. risk-3 is if not risk-1 or risk-2 and their calculated metabolic ratio (glycoprotein hba1c (%) / serum albumin (g/dl)) is not lower than the 60th percentile of the ratio distribution for their specific race/Hispanic origin group, and the absence of a diabetes diagnosis (doctor told you have diabetes = no) is not false when age in years at screening is 65 or older. risk-4: assigned if not risk-1, risk-2, or risk-3, and whose age when first told the patient had diabetes is not unknown, will not fail to be assigned risk-4"'
]
outcome_1 = ['outcome: "The outcome will be diabetes affected eyes/had retinopathy"']

outcome_2 = [
    'outcome: "individuals aged over 60 who belong to the third largest race/Hispanic origin group and have diabetic retinopathy are labeled positive (1), while all other individuals are labeled negative(0)"'
]
outcome_3 = [
    'outcome: "We will label the outcome as positive (1) only if the participants serum albumin (g/dL) is not less than the 60(%)of the distribution for their specific race/Hispanic origin group and have diabetic retinopathy otherwise the outcome is negative (0)"'
]
outcome_4 = [
    'outcome:"The outcome will be diabetes affected eyes/had retinopathy but we will label the outcome as positive(1) only if the participants have diabetic retinopathy and serum albumin (g/dL) is not less than the 50(%)of the distribution for their gender and the calculated cohort ratio (respective race/Hispanic origin group/total count multiplied by 5) is larger than a predefined external constant of 1, otherwise the outcome is negative (0)"'
]
covar_1 = ['covariates: "Consider gender and age at screening in this analysis"']

in_010 = [
    'inclusion: "We will include participants who has diabetes when diabetes is defined as meeting any of the following requirements: reported yes when asked doctor told you have diabetes, or fasting plasma glucose (FPG, mmol/L) ≥7.0 mmol/L, or glycohemoglobin (HbA1c) (%) ≥6.5%, or who takes diabetic pills to lower blood sugar"'
]
out_010 = [
    'exclusion: "We will exclude participants whose age at screening is less than 20, pregnant at the exam, and had missing values of weight (kg), waist circumference (cm). We will exclude participants who are missing gender, race/Hispanic origin, urine albumin (mg/L), or urine creatinine (mg/dL), serum creatinine (mg/dl)"'
]
pred_010 = [
    'predictor: "The predictor is weight-adjusted-waist (wwi) ratio which is calculated as waist circumference (cm) divided by the square root of weight(kg), categorized as quartiles(%) Q1: ≤25, Q2: >25 and ≤50, Q3: >50 and ≤75, Q4: >75"'
]
outome_010 = [
    'outcome:"The outcome of interest is the presence of kidney disease, defined as either an estimated glomerular filtration rate (eGFR) below 60 mL/min/1.73m^2 or a urine albumin-to-creatinine ratio (UACR) (mg/g) of 30 mg/g or greater. eGFR can be calculated using gender, serum creatinine (mg/dl), age at screening, race/Hispanic origin information for 4 different cases: 1. if gender is female and race/Hispanic origin is Non-Hispanic Black : 141 * min(serum creatinine (mg/dl) / 0.7, 1) ** -0.329 * max(serum creatinine (mg/dl) / 0.7, 1) ** -1.209 * (0.993 ** age at screening) * 1.018 * 1.159. 2. if gender is female and race/Hispanic origin is not Non-Hispanic Black : 141 * min(serum creatinine (mg/dl) / 0.7, 1) ** -0.329 * max(serum creatinine (mg/dl) / 0.7, 1) ** -1.209 * (0.993 ** age at screening) * 1.018. 3. if gender is male and race/Hispanic origin is Non-Hispanic Black : 141 * min(serum creatinine (mg/dl) / 0.9, 1) ** -0.411 * max(serum creatinine (mg/dl) / 0.9, 1) ** -1.209 * (0.993 ** age at screening) * 1.159. 4. if gender is male and race/Hispanic origin is not Non-Hispanic Black : 141 * min(serum creatinine (mg/dl) / 0.9, 1) ** -0.411 * max(serum creatinine (mg/dl) / 0.9, 1) ** -1.209 * (0.993 ** age at screening). Urine albumin-to-creatinine ratio (mg/g) is calculated as 100*(urine albumin mg/L / urine creatinine mg/dL) "'
]
covar_010 = [
    'covariates:"Adjust the analysis for race/Hispanic origin (white and non white), gender, and age at screening (<60 and >=60)"'
]
in_012 = [
    'inclusion: "Only include participants whose age at screening is greater than or equal to 20 years and whose fasting plasma glucose (FPG, mmol/L) is greater than or equal to 6.0"'
]
out_012 = [
    'exclusion: "Exclude participants who had missing values of weight (kg), waist circumference (cm), gender, race/Hispanic origin, urine albumin (mg/L), or urine creatinine (mg/dL), serum creatinine (mg/dl). Exclude participants whose age at screening is less than 20 years or whose serum creatinine (mg/dL) is greater than or equal to 2.0""'
]
pred_012 = [
    'predictor:"The predictor is a capped weight-adjusted-waist ratio (cWWI), calculated as waist circumference (cm) divided by the square root of weight (kg), with values above 20 set to 20 and values below 2 set to 2, used as a continuous variable"'
]
outome_012 = [
    'outcome:"The outcome is coded as 1 if the urine albumin-to-creatinine ratio (UACR), calculated as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL), is greater than or equal to 30 mg/g and the participants age at screening is greater than or equal to 45 years, and coded as 0 otherwise"'
]
covar_012 = [
    'covariates:"Consider race/Hispanic origin, gender, and age at screening, and additionally adjust for a composite glycemic status covariate defined as the sum of fasting plasma glucose (mmol/L) and glycoprotein HbA1c (%), where the sum is multiplied by 1.1 if the participant is take diabetic pills to lower blood sugar and multiplied by 0.9 if the participant reported no to qa question take diabetic pills to lower blood sugar"'
]
in_0121 = [
    'inclusion: "Only include participants whose waist circumference (cm) divided by weight (kg) is greater than 0.4 and whose serum creatinine (mg/dL) is less than 2.0"'
]
out_0121 = [
    'exclusion: "Exclude participants whose age at screening is less than 20, pregnant at the exam, and had missing values of weight (kg), waist circumference (cm), gender, race/Hispanic origin, urine albumin (mg/L), or urine creatinine (mg/dL), serum creatinine (mg/dl). Exclude participants whose weight-adjusted waist ratio (waist circumference (cm) divided by square root of weight (kg)) is less than 4.0 or greater than 20.0""'
]
pred_0121 = [
    'predictor:"The predictor is a log-transformed index, calculated as the natural logarithm of (1 plus waist circumference (cm) divided by the square root of weight (kg)), used as a continuous variable"'
]
outome_0121 = [
    'outcome:"The outcome is coded as 1 if UACR (mg/g), calculated as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL), is greater than or equal to 30 and glycoprotein HbA1c (%) is greater than or equal to 6.5, and coded as 0 otherwise"'
]
covar_0121 = [
    'covariates:"Consider race/Hispanic origin, gender, and age at screening, and additionally adjust for a renal-age scaling covariate defined as serum creatinine (mg/dL) divided by age at screening, then multiplied by 1.2 if urine albumin (mg/L) is greater than or equal to 30 and multiplied by 1.0 otherwise"'
]
in_013 = [
    'inclusion: "Only include participants whose fasting plasma glucose (FPG, mmol/L) is not less than the median fasting plasma glucose calculated within their gender group among participants aged 20 years or older"'
]
out_013 = [
    'exclusion: "Exclude participants who had missing values of weight (kg), waist circumference (cm), gender, race/Hispanic origin, urine albumin (mg/L), or urine creatinine (mg/dL), serum creatinine (mg/dl). Exclude participants whose glycoprotein HbA1c (%) is greater than the 90th percentile of glycoprotein HbA1c (%) calculated within their race/Hispanic origin group among participants who satisfy the study inclusion criteria and are aged 20 years or older""'
]
pred_013 = [
    'predictor:"The predictor is a two-stage benchmarked WWI score defined as WWI (waist circumference (cm) divided by the square root of weight (kg)) divided by the race/Hispanic origin specific mean WWI calculated among participants in the cohort, and then divided by the gender specific median of that race-standardized WWI calculated from the same eligible cohort, producing a single continuous predictor"'
]
outome_013 = [
    'outcome:"The outcome is coded as 1 only if the participant satisfies the following conditions. The participant must meet the renal condition, defined as having a urine albumin-to-creatinine ratio (UACR), calculated as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL), that is greater than or equal to the race/Hispanic origin specific median UACR calculated among participants in the cohort. Among participants who meet this renal condition, the participant must also meet at least one metabolic condition, defined as either fasting plasma glucose (mmol/L) being greater than or equal to the gender specific 75th percentile of fasting plasma glucose or glycoprotein HbA1c (%) being greater than or equal to the gender specific 75th percentile of glycohemoglobin HbA1c (%), with both percentiles calculated paritipants in the cohort. Participants failing either step are coded as 0"'
]
covar_013 = [
    'covariates:"Consider race/Hispanic origin, gender, age at screening, and define the covariate Race-Benchmarked HbA1c Index (RBHI) as the participants glycoprotein HbA1c (%) divided by the mean HbA1c (%) calculated within their race/Hispanic origin group among participants who satisfy the study inclusion criteria"'
]
in_0131 = [
    'inclusion: "Include those whose serum creatinine (mg/dL) is not greater than the mean calculated within their race/Hispanic origin group among participants aged less than 60 years and waist circumference (cm) is not smaller than the median calculated within their gender group"'
]
out_0131 = [
    'exclusion: "Exclude participants who had missing values of weight (kg), waist circumference (cm), gender, race/Hispanic origin, urine albumin (mg/L), or urine creatinine (mg/dL), serum creatinine (mg/dl). Exclude participants whose urine albumin-to-creatinine ratio (UACR, mg/g) calculated as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL) is greater than the gender specific 85th percentile of UACR calculated among inclusion-eligible participants aged less than 60 years""'
]
pred_0131 = [
    'predictor: "The predictor is an age-stratified index X computed in sequence as follows: first compute Index X as fasting plasma glucose (FPG, mmol/L) divided by WWI (waist circumference divided by square root of weight), then dividing it by the age-group specific mean Index X calculated separately for participants aged less than 60 years and those aged 60 years or older among participants in the cohort, yielding a single continuous predictor"'
]
outome_0131 = [
    'outcome: "The outcome is coded as 1 only if the participant satisfies both of the following benchmark-dependent conditions. First, the participants UACR (mg/g), calculated as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL), must be greater than or equal to the age-group specific 70th percentile of UACR calculated separately among participants aged less than 60 years and those aged 60 years or older who are in the cohort. Among participants meeting this albuminuria condition, the participants ratio of serum creatinine (mg/dL) to age at screening must be greater than or equal to the race/Hispanic origin specific median of this ratio, calculated from the same cohort. Participants who do not satisfy both conditions are coded as 0"'
]
covar_0131 = [
    'covariates:"Consider race/Hispanic origin, gender, age at screening, and define the covariate Age-Group Standardized Serum Creatinine Deviation (AG-SCrD) as the participants serum creatinine (mg/dL) minus the mean serum creatinine (mg/dL) calculated within their age group (age <60 and age ≥60) among participants who satisfy the study inclusion criteria, and then divided by the standard deviation of serum creatinine (mg/dL) within that same age group"'
]
in_014 = [
    'inclusion: "Only include participants who cannot be classified as failing eligibility, where failure is defined as having fasting plasma glucose (FPG, mmol/L) below the race/Hispanic origin specific median calculated among participants aged 20 years or older; participants who would otherwise fail are nevertheless included unless it is simultaneously true that their glycoprotein HbA1c (%) is below 6.5 and they are not taking diabetic pills to lower blood sugar"'
]
out_014 = [
    'exclusion: "Exclude participants who had missing values of weight (kg), waist circumference (cm), gender, race/Hispanic origin, urine albumin (mg/L), or urine creatinine (mg/dL), serum creatinine (mg/dl). Exclude participants who cannot be classified as remaining eligible after applying the following rule: eligibility holds if glycoprotein HbA1c (%) is not greater than the race/Hispanic origin specific 90th percentile calculated among participants who satisfy the study inclusion criteria and are aged 20 years or older; however, participants who would otherwise be excluded under this rule are retained unless it is simultaneously true that fasting plasma glucose (FPG, mmol/L) is greater than or equal to 7.0 and whether they take diabetic pills to lower blood sugar is yes""'
]
pred_014 = [
    'predictor:"The predictor is a standardized WWI value that is not left in its raw form unless the participant cannot be classified as exceeding the race/Hispanic origin specific 75th percentile of WWI calculated among participants in the cohort; if the participant exceeds this percentile, the predictor is redefined as the participants WWI divided by the race/Hispanic origin specific median WWI and then divided again by the gender specific median of that race-standardized quantity calculated from the same inclusion-eligible cohort, producing a single continuous predictor"'
]
outome_014 = [
    'outcome:"The outcome is coded as 1 for participants who cannot be classified as remaining in the protected metabolic renal state. The protected metabolic renal state is defined as follows. Participants must have a urine albumin-to-creatinine ratio (UACR), calculated as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL), that is below the race/Hispanic origin specific median UACR calculated among participants in the cohort. This is conditional on satisfying this renal requirement, the participant must also have both fasting plasma glucose (mmol/L) below the gender specific 75th percentile of fasting plasma glucose and glycoprotein HbA1c (%) below the gender specific 75th percentile of HbA1c, with both percentiles calculated among the participants in the cohort. Participants who fail to satisfy either level of the protected state are coded as 1 unless it is simultaneously true that they are aged 60 years or older and are taking diabetes medication, in which case they are reclassified as 0. All remaining participants are coded as 0"'
]
covar_014 = [
    'covariates:"Consider race/Hispanic origin, gender, age at screening, and define the covariate Confirmation Score ABC as follows: compute a base glycemic load as fasting plasma glucose (mmol/L) plus glycoprotein HbA1c (%); define diabetes-confirmed as having doctor told you have diabetes = Yes or take diabetic pills to lower blood sugar = Yes; Confirmation Score ABC equals the base glycemic load minus the race/Hispanic origin specific median base glycemic load calculated among participants who satisfy the study inclusion criteria, except when it is not true that the participant cannot be determined to not be diabetes-confirmed, in which case the Confirmation Score ABC is instead set to 0"'
]
in_0141 = [
    'inclusion: "Only include participants who are not determined to be ineligible, where ineligibility is defined as having a weight-adjusted waist ratio (waist circumference (cm) divided by square root of weight (kg)) below the age-group specific mean calculated separately for participants aged less than 60 years and those aged 60 years or older and have waist circumference (cm) value and weight (kg) value; participants below their age-group mean are nevertheless included unless their serum creatinine (mg/dL) exceeds the race/Hispanic origin specific 75th percentile"'
]
out_0141 = [
    'exclusion: "Exclude participants who had missing values of weight (kg), waist circumference (cm), gender, race/Hispanic origin, urine albumin (mg/L), or urine creatinine (mg/dL), serum creatinine (mg/dl). Exclude participants who are not in the set of individuals who cannot be determined to not violate the WWI constraint, where the WWI constraint is defined as having weight-adjusted waist ratio (waist circumference (cm) divided by square root of weight (kg)) not less than the mean WWI within their gender group calculated among participants who satisfy the study inclusion criteria and are aged 20 years or older; participants below this mean are nevertheless retained unless their serum creatinine (mg/dL) exceeds the race/Hispanic origin specific 75th percentile calculated from the same inclusion-eligible analytic cohort""'
]
pred_0141 = [
    'predictor:"The predictor is a renal-weighted glycemic index defined as fasting plasma glucose (FPG, mmol/L) divided by serum creatinine (mg/dL), which is not applied unmodified unless it is not true that the participant cannot be determined to not belong to the high creatinine stratum, where the high creatinine stratum is defined as serum creatinine (mg/dL) not less than the race/Hispanic origin specific median serum creatinine calculated among participants in the cohort; if the participant belongs to this stratum, the index is multiplied by the gender considered WWI factor defined as WWI divided by the gender specific mean WWI calculated from the same inclusion-eligible cohort, yielding a single continuous predictor"'
]
outome_0141 = [
    'outcome:"The outcome is coded as 1 for participants who are not determined to belong to the low risk class. The low risk class is defined as follows: the participant must have a urine albumin-to-creatinine ratio (UACR), calculated as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL), that is below the age group specific 70th percentile of UACR calculated among participants in the analytic cohort, and, conditional on meeting this albuminuria requirement, must also have a ratio of serum creatinine (mg/dL) to age at screening that is below the race/Hispanic origin specific median of this ratio calculated from the same cohort. Participants who do not satisfy this low risk class are coded as 1 unless it is additionally true that their fasting plasma glucose (mmol/L) is below 6.0 and their glycoprotein HbA1c (%) is below 6.5, in which case they are hierarchically reassigned to 0"'
]
covar_0141 = [
    'covariates:"Consider race/Hispanic origin, gender, age at screening, and define the covariate Index ABC as follows: compute UACR (mg/g) as 100 times urine albumin (mg/L) divided by urine creatinine (mg/dL); compute a renal ratio as serum creatinine (mg/dL) divided by age at screening; define high albuminuria as UACR greater than or equal to the race/Hispanic origin specific 75th percentile of UACR calculated among inclusion-eligible participants; the covariate Index ABC is defined as renal ratio multiplied by glycoprotein HbA1c (%), and this value is not left unmodified unless it is not true that the participant cannot be determined to not belong to the high-albuminuria class; if the participant is treated as belonging to the high-albuminuria class, multiply the covariate Index ABC by 2 for participants who are not younger than 60 years and multiply by 1 otherwise"'
]
in_10 = [
    'inclusion: "Only include individuals whose fasting plasma glucose (FPG, mmol/L) is not missing and not less than one-fifth of their current age in years at screening multiplied by their ratio of their respective race/Hispanic orgin in all categories"'
]
in_11 = [
    'inclusion: "Only include participants who has information on gender, race/Hispanic origin, urine albumin mg/L, urine creatinine (mg/dL), serum creatinine (mg/dl), weight (kg), waist circumference (cm)"'
]
in_14 = [
    'inclusion: "Only include participants who has information on gender, race/Hispanic origin, urine albumin mg/L, urine creatinine (mg/dL), serum creatinine (mg/dl),  weight (kg), waist circumference (cm). Only include participants whose fasting glucose (mmol/l) is strictly greater than the median fasting glucose (mmol/l) calculated from the subcohort who are not prevented from having a pregnancy status at exam and who are not taking diabetic pills to lower blood sugar, and additionally, the participant\'s glycoprotein HbA1C (%) must be less than 8.0"'
]
in_15 = [
    'inclusion: "Only include participants who has information on gender, race/Hispanic origin, urine albumin mg/L, urine creatinine (mg/dL), serum creatinine (mg/dl),  weight (kg), waist circumference (cm). Only include individuals whose weight-adjusted waist ratio (WWI) is not less than the mean WWI calculated within their race/Hispanic origin group, multiplied by the ratio of the count of their race/Hispanic origin group to the count of the second-largest race/Hispanic origin group in the cohort"'
]
out_10 = [
    'exclusion: "Exclude patients who do not have diabetes when diabetes is defined as meeting any of the criteria: who reported yes to doctor told you have diabetes or fasting plasma glucose (FPG, mmol/L) equal or more than 7.0 mmol/L or glycohemoglobin (HbA1c) (%) equal or more than 6.5%, or take diabetic pills to lower blood sugar"'
]
out_11 = [
    'exclusion: "Exclude patients who do not have diabetes when diabetes is defined as meeting any of the criteria: who reported yes to doctor told you have diabetes  or fasting plasma glucose (FPG, mmol/L) not less than 7.0 mmol/L or glycohemoglobin (HbA1c) (%) not smaller than 6.5%, or take diabetic pills to lower blood sugar"'
]
out_14 = [
    'exclusion: "Exclude any participant who is not among the 15th percentile (or lower) of waist circumference (cm) for the entire cohort unless their age in years at screening is exactly 40 and they are taking diabetic pills to lower blood sugar"'
]
out_17 = [
    'exclusion: "Exclude participants who has missing any information on gender, race/Hispanic origin, urine albumin mg/L, urine creatinine (mg/dL), serum creatinine (mg/dl), weight (kg), waist circumference (cm). Exclude patients who is not without evidence of diabetes when it is defined as meeting any of the criteria: who reported yes to doctor told you have diabetes or fasting plasma glucose (FPG, mmol/L) not less than 7.0 mmol/L or glycohemoglobin (HbA1c) (%) not smaller than 6.5%, or take diabetic pills to lower blood sugar"'
]
out_18 = [
    'exclusion: "Exclude any participant who is not in the set of individuals who cannot be determined to not satisfy the following inclusion rule: the participants fasting plasma glucose (FPG, mmol/L) is not missing and is not less than the participant specific threshold B, where B is defined as one-fifth of the participants age in years at screening multiplied by the ratio of the count of the participants race/Hispanic origin group to the total cohort size; however, even if a participant would otherwise be excluded under this rule, the participant is immediately re-included unless it is simultaneously true that they are not female, are not younger than 60 years, and are not take diabetic pills to lower blood sugar"'
]
pred_11 = [
    'predictor: "The predictor is modified weight-adjusted-waist (wwi) ratio which is calculated as waist circumference (cm) divided by the square root of weight(kg) for gender that is less common and we will do *2 to this value for gender that is more common.'
]
pred_12 = [
    'predictor: "The predictor is adjusted weight, which is the the square root of weight(kg) for gender that is less common and we will do *2 to this value for gender that is more common.'
]
pred_14 = [
    "predictor: \"The core Predictor is the Modified Ratio ABC, calculated as fasting glucose (mmol/l) divided by weight (kg). The result is multiplied by 3.0 if the participant's creatinine (mg/dl) is less than the 25th percentile for their respective race/Hispanic origin group and their gender is Female; otherwise, the Modified Ratio ABC is divided by the participant's glycoprotein HbA1C (%)\""
]
pred_15 = [
    'predictor: "Define the predictor benchmark ABC as the participant s weight-adjusted waist ratio (WWI), calculated as waist circumference (cm) divided by the square root of weight (kg), divided by the 70th percentile of WWI within the participants age group, where age groups are defined as younger than 30 years, 30 years or older and younger than 60 years, and 60 years or older, and then multiplied by the ratio of the size of the participants age group to the size of the largest age group in the cohort"'
]
outcome_11 = [
    'outcome: "The outcome is the presence of kidney disease, defined as a urine albumin-to-creatinine ratio (UACR) (mg/g) of 30 mg/g or greater  when the urine albumin-to-creatinine ratio (mg/g) is calculated as 100*(urine albumin mg/L / urine creatinine mg/dL)"'
]
outcome_12 = [
    'outcome:"The renal risk is a binary outcome classified as 1 (High Risk) only if a participant simultaneously satisfies three complex conditions and is classified as 0 (Low Risk) otherwise. The participant must first meet the threshold, requiring their Urine Albumin-to-Creatinine Ratio (UACR, in mg/g) to be 30mg/g where it is calculated as 100*(urine albumin mg/L / urine creatinine mg/dL). Second, they must also meet the assesment by satisfying at least one of two conditions: their fasting glucose must be not less than 5.0mmo/l/ or their ratio of serum creatinine to age in years at screening much be not smaller than 0.015. Finally, and most critically, to be considered High Risk, the participant must not be categorized in the controlled risk state. This controlled risk state is only true if all of its sub-conditions are met: the participant is a female over 60; they have either not been told by a doctor they have diabetes or are taking diabetic pills; and their glycoprotein HbA1C (%) is not more than 6.5 unless their weight is less than 75kg. If controlled risk, the participant is immediately assigned Low Risk (ADRR = 0), regardless of meeting the other two criteria"'
]
outcome_14 = [
    "outcome: \"The outcome is Flag ABC, which is High Risk (1) only if the Urine Albumin to Creatinine Ratio (UACR, 100 times albumin, urine (mg/l) divided by creatinine, urine (mg/dl)) is greater than or equal to 30 mg/g and their age in years at screening is greater than 75. However, Flag ABC is immediately Low Risk (0) if the participant's waist circumference (cm) is less than 90 cm or if their pregnancy status at exam indicates 'Yes, positive lab pregnancy test or self-reported pregnant at exam'\""
]
covar_11 = [
    'covariates: "Consider race/Hispanic origin, gender, and age at screening in the analysis"'
]
covar_12 = [
    'covariates: "The covariates include "race/Hispanic origin, gender, age at screening, and Score ABC. Score ABC is calculated by first finding the Glucose-to-Waist Ratio (GWR) as fasting glucose (mmol/L) divided by waist circumference (cm). This GWR is then conditionally adjusted: if the participant is not taking diabetic pills to lower blood sugar, the GWR is multiplied by the difference between their glycoprotein HbA1C (%) and 7(%); if the participant is taking diabetic pills, the GWR is divided by the same difference. Score ABC value is the absolute value of this conditional result"'
]
covar_14 = [
    'covariates: "The only covariates considered are race/Hispanic origin and gender"'
]
covar_15 = [
    'covariates: "Define the covariate Score X as the participants fasting plasma glucose (mmol/L) plus their glycohemoglobin (HbA1c, %), divided by the mean of the same summed quantity calculated among participants in the same race/Hispanic origin group who have been told by a doctor that they have diabetes or take diabetic pills to lower blood sugar, and then multiplied by the ratio of the size of the participants race/Hispanic origin group to the size of the smallest race/Hispanic origin group in the cohort"'
]
covar_16 = [
    'covariates: "Define the covariate Index Y as the participants waist-to-weight ratio (waist circumference (cm) divided by weight (kg)) multiplied by their serum creatinine (mg/dL), and then divided by the 65th percentile of this combined quantity within the participants age group (defined as <30 years, 30 to <60 years, and ≥60 years), and finally scaled by the ratio of the participants urine albumin-to-creatinine ratio (100 x urine albumin mg/L ÷ urine creatinine mg/dL) to the median urine albumin-to-creatinine ratio within that same age group"'
]
in_01 = [
    'inclusion: "The study will include age at screening >=20, who has diabetes, defined as meeting any of the following: who said yes or borderline when asked whether doctor told you have diabetes, reported taking diabetic pills to lower blood sugar, fasting plasma glucose (mg/dl) >126"'
]
out_01 = [
    'exclusion: "Exclude participants with missing values in adult food security questionaire and missing any of the depression questions: "have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself", "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead""'
]
pred_01 = [
    'predictor: "The main predictor is food insecurity level defined baesd on the answer to the adult food security question, categorized as severe food insecurity for participants who reported very low food security or low food security, mild food insecurity for participants who reported marginal food security, and food secure for who reported full food security"'
]
outcome_01 = [
    'outcome: "The outcome is depression outcome, which is based on the total score from the nine questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3), if value is null assign (0), and the total score >=10 was defined as clinically relevant depression and else was not"'
]
covar_01 = [
    'covariates: "Covariates include age in years at screening, gender, race/Hispanic origin"'
]
out_0221 = [
    'exclusion: "Participants with missing values in adult food security questionaire, missing any of the depression questions: "have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself",  "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead. Exclude participants whose fasting plasma glucose (mg/dl) <120 but reported borderline to ever being told by a doctor they have diabetes"'
]
pred_0221 = [
    'predictor: "The predictor is a binary Indicator ABC, defined as 1 if the participant reports very low or low food security and also reports reports any frequency other than "Not at all" for question thoughts of being better off dead and 0 otherwise"'
]
in_023 = [
    'inclusion: "To be included, participants must be at least 20 years old at screening and have a fasting plasma glucose (mg/dL) greater than the gender specific mean, calculated among participants with non-missing fasting plasma glucose and gender, and must additionally report at least two physical symptoms, defined as responses other than "Not at all" to feeling tired, poor appetite or overeating, or moving or speaking slowly or too fast"'
]
out_023 = [
    'exclusion: "Participants with missing values in adult food security questionaire, missing any of the depression questions: "have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself",  "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead. Exclude participants whose frequency of "trouble concentrating on things" is greater than the gender specific median frequency calculated among all inclusion criteria eligible participants aged less than 60 years"'
]
pred_023 = [
    'predictor: "The predictor is Index ABC defined as the individual food security score divided by the gender specific mean score calculated among the eligible cohort, and then divided again by the age group specific median (aged <60 vs ≥60) calculated from the same eligible cohort. The individual food security score is derived from the adult food security questionnaire, categorized as very low (0), low (1), marginal (2), or full food security (3)"'
]
outcome_023 = [
    'outcome:"The outcome is coded as 1 only if the participant meets two sequential conditions: first, the depression total score which is based on the total score from the nine depression questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3) must be more than 10. Among those meeting this score, the participants fasting plasma glucose (mg/dl) must be greater than or equal to the gender specific median calculated among the cohort. Participants failing either step are coded as 0"'
]
covar_023 = [
    'covariate:"Adjust for gender and age in years at screening, and define Index ABC as follows: calculate an individuals glycemic load, fasting plasma glucose (mg/dl) divided by 100—multiplied by their total depression score, which is calculated as the sum of the nine depression questionnaire items where each question is assigned a value of Not at all (0), Several days (1), More than half the days (2), or Nearly every day (3), and any null values are assigned 0; Index ABC is this product divided by the mean glycemic load calculated within the participants gender group among those who report any adult food insecurity status other than "Full" within the inclusion/exclusion eligible cohort"'
]
in_0231 = [
    'inclusion: "Include individuals whose age in years at screening is 35 or older who take diabetic pills to lower blood sugar but still show a fasting plasma glucose (mg/dl) above 110 mg/dl and who have a non-missing response to “feeling down, depressed, or hopeless”; among this subgroup, include only those whose item score (0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day) is greater than the subgroup median"'
]
out_0231 = [
    'exclusion: "participants with missing values in adult food security questionaire, missing any of the depression questions:"have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself",  "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead. Exclude participants whose reported frequency of "feeling down, depressed, or hopeless" is higher than the mean frequency calculated within their specific adult food security questionnaire category"'
]
pred_0231 = [
    'predictor: "The predictor is Level ABC, defined as the food security score divided by the mean fasting plasma glucose (mg/dl) calculated among participants of the same gender who have been told by a doctor they have diabetes. The individual food security score is an ordinal measure of food stability derived from the adult food security questionnaire, categorized as very low (0), low (1), marginal (2), or full food security (3)"'
]
outcome_0231 = [
    'outcome: "The outcome is coded as 1 if the participants depression total score which is based on the total score from the nine depression questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3) is more than 10 and their individual food security score, based on the adult food security questionaire where the values were calculated as Full = 1, Marginal = 2, Low = 3, and Very Low = 4, is below the cohort mean for their specific gender group; otherwise coded as 0"'
]
covar_0231 = [
    'covariate:"Consider race/Hispanic origin and gender, and define Score ABC as the participants total depression score calculated by summing the nine depression questionnaire items where each item is valued as Not at all (0), Several days (1), More than half the days (2), or Nearly every day (3), with nulls assigned 0 minus the mean total depression score calculated within their specific food security level (categorized as Very Low (0), Low (1), Marginal (2), or Full (3)) among inclusion/exclusion eligible participants, and then divided by the standard deviation of the total depression score within that same food security stratum"'
]
in_024 = [
    'inclusion: "Only include participants who cannot be classified as low-risk, where low-risk is defined as having a fasting plasma glucose (mg/dL) below the gender specific median; participants who would otherwise be low risk are nevertheless included unless it is simultaneously true that they have never been told they have diabetes and report no thoughts of being better off dead"'
]
out_024 = [
    'exclusion: "participants with missing values in adult food security questionaire, missing any of the depression questions: "have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself",  "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead. Exclude participants who are not in the set of individuals who cannot be determined to not violate the glucose security constraint, where the constraint is defined as having fasting plasma glucose (mg/dl) not less than the mean glucose within their adult food security questionnaire group; participants below this mean are nevertheless retained unless their frequency of "feeling tired or having little energy" exceeds the 75th percentile for their age group when age group is defined as age in years at screening <=50 and >50"'
]
pred_024 = [
    'predictor: "The predictor is Score ABC from the adult food security questionnaire and categorized as very low (0), low (1), marginal (2), or full food security (3) that is not left in its raw score form unless the participant cannot be classified as exceeding the age group specific 75th percentile of food insecurity (stratified by age in years at screening <50 or ≥50 years) calculated among the cohort; if the participant exceeds this percentile, the predictor is redefined as the participants food security score divided by the gender specific median score from the same cohort"'
]
outcome_024 = [
    'outcome: "The outcome is coded as 1 for participants not determined to belong to the "Low Risk Metabolic Mood" class. This class requires a depression total score (which is based on the total score from the nine depression questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3)) is less than 10 and a fasting plasma glucose (mg/dl) below the age group specific median (stratified by age at screening <50 or >=50). Participants failing this are coded as 1 unless it is additionally true that their adult food security questionaire is "Marginal" or "Full" and they report "Not at all" (0) for "thoughts of being better off dead", in which case they are hierarchically reassigned to 0"'
]
covar_024 = [
    'covariate: "Adjust for gender and age in years at screening and Score ABC as follows: compute a base distress score as the sum of responses to "thought you would be better off dead" and "feeling down, depressed, or hopeless" (assigning values of Not at all (0), Several days (1), More than half the days (2), or Nearly every day (3), and null values are assigned (0); define risk confirmed group as having fasting plasma glucose (mg/dl) ≥126 or take diabetic pills to lower blood sugar; Score ABC equals the base distress score minus the gender specific median distress score, except when it is not true that the participant cannot be determined to not be in the risk confirmed group, in which case Score ABC is instead multiplied by the participants food security score derived from the adult food security questionnaire and categorized as very low (0), low (1), marginal (2), or full food security (3)"'
]
in_0241 = [
    'inclusion: "Only include participants who are not determined to be ineligible, where ineligibility is defined as having a combined score for "feeling tired" and "poor appetite" below the age group specific mean when age group is categorized as age in years at screening <30 and >= 30; participants below that mean are nevertheless included unless their fasting plasma glucose (mg/dL) is below 126 and they are not taking diabetic pills to lower blood sugar"'
]
out_0241 = [
    'exclusion: "participants with missing values in adult food security questionaire, missing any of the depression questions:"have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself",  "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead. Exclude participants who are not in the set of individuals who cannot be determined to not violate the metabolic mood constraint, where the constraint is defined as having a fasting plasma glucose (mg/dl) not greater than the age specific mean; participants above this mean are nevertheless retained unless it is simultaneously true that they report some level of "little interest in doing things" and are classified in the lowest category of the adult food security questionnaire"'
]
pred_0241 = [
    'predictor:"The predictor is a complex food metabolic index that is not considered stable unless the participant is not in the set of individuals who can be determined to violate the "security medication" constraint (defined as reporting Very Low food security while not taking diabetic pills to lower blood sugar); if the constraint is violated, the predictor is redefined as the food security rank multiplied (lowest security as 0 and highest as 4) by the ratio of fasting plasma glucose to the age group specific (stratified by age in years at screening <50 or ≥50 years) median glucose from the same cohort"'
]
outcome_0241 = [
    'outcome:"The outcome is coded as 1 for participants who cannot be classified as "Low Symptom" defined as having a depression total score (which is based on the total score from the nine depression questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3)) below the gender specific 75th percentile. Participants failing this are coded as 1 unless it is simultaneously true that they are aged <50 and their fasting plasma glucose (mg/dl) is below the 50th percentile for the "Full" Food Security group, in which case they are reassigned to 0"'
]
covar_0241 = [
    'covariate: "Consider gender and age in years at screening, and define Index ABC as follows: compute the total depression score (the sum of the nine depression questionnaire items where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3)); define "high insecurity class" as belonging to the Very Low or Low adult food security levels; Index ABC is defined as the total depression score multiplied by the fasting plasma glucose (mg/dl) ratio (individual glucose divided by cohort median), and this value is not left unmodified unless it is not true that the participant cannot be determined to not belong to the high insecurity class; if the participant is treated as belonging to the high insecurity class, multiply Index ABC by 2.0 for participants who have been told by a doctor they have diabetes and by 1.2 otherwise"'
]
in_02 = [
    'inclusion: Include participants whose self-reported doctor diagnosis of diabetes is yes and whose fasting plasma glucose (mg/dL) is not less than the median fasting plasma glucose calculated among participants of the same gender who were 20 years or older at screening"'
]
out_02 = [
    'exclusion: "Exclude participants with missing responses to the adult food security questionnaire or any of the nine depression questions, "have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself",  "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead", only if the count of each missing depression items exceeds the 75th percentile of missing-item counts within their age group (defined as 20-49, 50-64, 65 or more years)"'
]
pred_02 = [
    'predictor: "The predictor is Score ABC, defined as the participants food insecurity level derived from the adult food security questionnaire (coded as 4 for very low food insecurity, 3 for low food insecurity, 1 for marginal food insecurity, and 0 for full food security), divided by the mean food insecurity level among participants of the same gender"'
]
outcome_02 = [
    'outcome: "The outcome is depression outcome, which is based on the total score from the nine questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3), if value is null assign (0), and the outcome is relative depression status, defined as 1 if the participant total depression score from the nine questions is greater than or equal to the 60th percentile of depression scores within their age group (stratified by age at screening <50 or >=50), and 0 otherwise; missing responses are assigned a value of 0 prior to score calculation"'
]
covar_02 = [
    'covariates: "Covariates include gender and an age standardized fasting plasma glucose value, defined as the participants fasting plasma glucose (mg/dL) minus the mean fasting plasma glucose among participants in the same age group (stratified as 20-49, 50-64, 65 or more years)"'
]
in_03 = [
    'inclusion: Include participants who are not excluded from the eligible cohort, where a participant is excluded only if it is not true that they cannot be determined to not satisfy both of the following requirements: age in years at screening is not less than 20, and diabetes is not absent, where diabetes is considered not absent if the participant does not fail to meet at least one of these criteria: doctor told you have diabetes questionnaire response is yes or borderline, reported taking diabetic pills to lower blood sugar, or fasting plasma glucose (mg/dL) is not less than 126"'
]
out_03 = [
    'exclusion: "Exclude participants who are not in the set of individuals who cannot be determined to not have complete psychosocial data, where complete psychosocial data is defined as having a non-missing adult food security questionnaire and not failing to provide responses to each of the nine depression questions ("have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself",  "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead"); nevertheless, if a participant would otherwise be excluded for incompleteness, the participant is immediately retained unless it is simultaneously true that they are not female, are not younger than 60 years, and are not taking diabetic pills to lower blood sugar"'
]
pred_03 = [
    'predictor: "Define the predictor as Hierarchically Adjusted Food Insecurity Exposure, where participants are first assigned a base food insecurity category from the adult food security questionnaire (severe food insecurity if very low or low food security, mild food insecurity if marginal food security, and food secure if full food security), and this category is not left unmodified unless it is not true that the participant cannot be determined to not be diabetes-positive; diabetes-positive is defined as not failing to meet at least one of the diabetes criteria (self-reported diabetes is “Yes” or “Borderline,” taking diabetic pills to lower blood sugar, or fasting plasma glucose (mg/dL) > 126); if diabetes-positive, the participants food insecurity category is escalated by one level (food secure to mild, mild to severe), except that this escalation is immediately reversed if the participant reports taking diabetic pills to lower blood sugar"'
]
outcome_03 = [
    'outcome: "Define the depression outcome as 1 only if the participant is not in State ABC; a participant is State ABC if it is not false that they cannot be determined to not have low depressive symptom burden, where low burden is defined as having depression score which is calculated as the sum of the nine depression questionnaire items where each question is assigned a value of Not at all (0), Several days (1), More than half the days (2), or Nearly every day (3), and any null values are assigned (0);that is not greater than or equal to 10; however, even if the score would otherwise indicate a case (total score ≥ 10), the participant is immediately assigned outcome = 0 unless it is simultaneously true that they are not taking diabetic pills to lower blood sugar and their response to doctor told you have diabetes is yes or borderline"'
]
covar_03 = [
    'covariates: "Covariates include age in years at screening and gender, and additionally include Indicator ABC that equals 1 if the participant is not in the set of individuals who cannot be determined to not be 60 years or older and equals 0 otherwise; however, this indicator is immediately set to 0 unless it is simultaneously true that the participant is not female and is not taking diabetic pills to lower blood sugar"'
]
pred_aa1 = [
    'predictor: "The main predictor in the analysis will be gender-based serum albumin (g/dL), which is calculated as  serum albumin (g/dL)*2 for participants whose gender is female and serum albumin (g/dL)*3 for participants whose gender is male"'
]
pred_bb1 = [
    'predictor: "The predictor is weight-adjusted-waist (wwi) ratio which is calculated as waist circumference (cm) divided by the square root of weight(kg) multiplied by 2, categorized as binary using median(%) group1: ≤50, group2: >50"'
]
outcome_bb2 = [
    'outcome:"The outcome is defined as a gender-urine albumin-to-creatinine ratio (UACR) (mg/g) of 60 mg/g or greater. Gender-urine albumin-to-creatinine ratio (mg/g) is calculated as 100*(urine albumin mg/L / urine creatinine mg/dL), multiplied by 3 for whose gender is female and multiplied by 2 whose gender is male "'
]
covar_bb3 = [
    'covariates:"Adjust the analysis for race/Hispanic origin, gender, and age at screening (<40, 41-50, and >50"'
]
in_cc1 = [
    'inclusion: "The study will include age at screening more than 30 and less than 60, who has diabetes, defined as meeting any of the following: who said yes or borderline when asked whether doctor told you have diabetes, reported taking diabetic pills to lower blood sugar, fasting plasma glucose (mg/dl) >126."'
]
out_cc2 = [
    'exclusion: "Exclude participants with missing values in adult food security questionaire and missing any of the depression questions: "have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself", "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead. We will also exclude people whose gender is female and age at screening is less than 35""'
]
pred_cc3 = [
    'predictor: "The main predictor is food insecurity metric, defined baesd on the answer to the adult food security question: categorized as 0 for who reported very low food security or low food security, 1 for  who reported marginal food security, and 3 for who reported full food security. Then mutiply this number by 100"'
]
outcome_cc4 = [
    'outcome: "The outcome is depression outcome, which is based on the total score from the nine questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3), if value is null assign (0), and the total score >=10 was defined as clinically relevant depression and else was not. Multiply the total score by 2"'
]
covar_cc5 = [
    'covariates: "Covariates include age in years at screening, categorized as <30, 31-40, and 40>, gender, race/Hispanic origin"'
]
in_ccc6 = [
    'inclusion: "The study will include age at screening more than 40, who did not say "No" when asked whether doctor told you have diabetes, fasting plasma glucose (mg/dl) >130."'
]
out_cc7 = [
    'exclusion: "Exclude participants with missing values in adult food security questionaire and missing any of the depression questions: "have little interest in doing things", "feeling down, depressed, or hopeless", "trouble sleeping or sleeping too much", "feeling tired or having little energy", "poor appetite or overeating", "feeling bad about yourself", "trouble concentrating on things", "moving or speaking slowly or too fast", "thought you would be better off dead. We will also exclude people whose gender is Male and age at screening is more than 60""'
]
outcome_cc9 = [
    'outcome: "The outcome is gender-depression outcome, which is based on the total score from the nine questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3), if value is null assign (0), and the total score >=10 was defined as clinically relevant depression and else was not. Multiply the total score by 3 for whose gender is female, and multiply the total score by 2 for whose gender is male"'
]
covar_cc10 = [
    'covariates: "Covariates include age in years at screening, categorized as <30, 31-40, and 40>, gender, race/Hispanic origin, categorized as white and else"'
]

example = f"""
 We plan to conduct a logistic regression analysis to examine the relationship between serum albumin (g/dL) and diabetic retinopathy using NHANES data from the years 2011 to 2012. 
{{inclusion}}.
{{exclusion}}.
{{predictor}}.
{{outcome}}.
{{covariates}}.
"""
example_2 = f"""
 We will plan to do a weighted logistic regression using exam weights from NHANES data from 2007-2008. 
{{inclusion}}.
{{exclusion}}.
{{predictor}}.
{{outcome}}.
{{covariates}}.
"""
example_3 = f"""
 We will plan to do a weighted logistic regression using exam weights from NHANES data from 2011-2012.
{{inclusion}}.
{{exclusion}}.
{{predictor}}.
{{outcome}}.
{{covariates}}.
"""

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

sql_a = in_001 + out_001 + pred_001 + outome_001 + covar_001
sql_b = in_010 + out_010 + pred_010 + outome_010 + covar_010
sql_c = in_01 + out_01 + pred_01 + outcome_01 + covar_01
sql_easy_a_1 = in_002 + out_001 + pred_001 + outome_001 + covar_001
sql_easy_a_2 = in_001 + out_002 + pred_001 + outome_001 + covar_001
sql_easy_a_3 = in_001 + out_001 + pred_002 + outome_001 + covar_001
sql_easy_a_4 = in_001 + out_001 + pred_001 + outome_002 + covar_001
sql_easy_a_5 = in_001 + out_001 + pred_001 + outome_001 + covar_002
sql_easy_a_6 = in_001 + out_0021 + pred_001 + outome_001 + covar_001
sql_easy_a_7 = in_001 + out_001 + pred_0021 + outome_001 + covar_001
sql_easy_a_8 = in_001 + out_001 + pred_001 + outome_0021 + covar_001
sql_easy_a_9 = in_001 + out_001 + pred_001 + outome_001 + covar_0021
sql_easy_a_10 = in_2 + out_1 + pred_1 + outcome_2 + covar_1
sql_easy_a_11 = in_001 + out_001 + pred_aa1 + outome_001 + covar_001
sql_moderate_a_1 = in_003 + out_001 + pred_001 + outome_001 + covar_001
sql_moderate_a_2 = in_001 + out_003 + pred_001 + outome_001 + covar_001
sql_moderate_a_3 = in_001 + out_001 + pred_003 + outome_001 + covar_001
sql_moderate_a_4 = in_001 + out_001 + pred_001 + outome_003 + covar_003
sql_moderate_a_5 = in_0031 + out_001 + pred_001 + outome_001 + covar_001
sql_moderate_a_6 = in_001 + out_0031 + pred_001 + outome_001 + covar_001
sql_moderate_a_7 = in_001 + out_001 + pred_0031 + outome_001 + covar_001
sql_moderate_a_8 = in_001 + out_001 + pred_001 + outome_0031 + covar_001
sql_moderate_a_9 = in_001 + out_001 + pred_001 + outome_001 + covar_0031
sql_moderate_a_10 = in_0 + out_1 + pred_1 + outcome_1 + covar_1
sql_moderate_a_11 = in_2 + out_1 + pred_1 + outcome_3 + covar_1
sql_hard_a_1 = in_001 + out_001 + pred_004 + outome_001 + covar_001
sql_hard_a_2 = in_001 + out_001 + pred_001 + outome_004 + covar_001
sql_hard_a_3 = in_001 + out_001 + pred_001 + outome_001 + covar_004
sql_hard_a_4 = in_0041 + out_001 + pred_001 + outome_001 + covar_001
sql_hard_a_5 = in_001 + out_0041 + pred_001 + outome_001 + covar_001
sql_hard_a_6 = in_001 + out_001 + pred_0041 + outome_001 + covar_001
sql_hard_a_7 = in_001 + out_001 + pred_001 + outome_0041 + covar_001
sql_hard_a_8 = in_001 + out_001 + pred_001 + outome_001 + covar_0041
sql_hard_a_9 = in_2 + out_1 + pred_1 + outcome_4 + covar_1
sql_hard_a_10 = in_2 + out_1 + pred_2 + outcome_1 + covar_1
sql_easy_b_1 = in_012 + out_010 + pred_010 + outome_010 + covar_010
sql_easy_b_2 = in_010 + out_012 + pred_010 + outome_010 + covar_010
sql_easy_b_3 = in_010 + out_010 + pred_012 + outome_010 + covar_010
sql_easy_b_4 = in_010 + out_010 + pred_010 + outome_012 + covar_012
sql_easy_b_5 = in_0121 + out_010 + pred_010 + outome_010 + covar_010
sql_easy_b_6 = in_010 + out_010 + pred_0121 + outome_010 + covar_010
sql_easy_b_7 = in_010 + out_010 + pred_010 + outome_0121 + covar_010
sql_easy_b_8 = in_010 + out_010 + pred_010 + outome_010 + covar_0121
sql_easy_b_9 = in_010 + out_010 + pred_bb1 + outome_010 + covar_010
sql_easy_b_10 = in_010 + out_010 + pred_010 + outcome_bb2 + covar_010
sql_easy_b_11 = in_010 + out_010 + pred_010 + outome_010 + covar_bb3
sql_moderate_b_1 = in_013 + out_010 + pred_010 + outome_010 + covar_010
sql_moderate_b_2 = in_010 + out_010 + pred_013 + outome_010 + covar_010
sql_moderate_b_3 = in_010 + out_010 + pred_010 + outome_013 + covar_010
sql_moderate_b_4 = in_0131 + out_010 + pred_010 + outome_010 + covar_010
sql_moderate_b_5 = in_010 + out_0131 + pred_010 + outome_010 + covar_010
sql_moderate_b_6 = in_010 + out_010 + pred_0131 + outome_010 + covar_010
sql_moderate_b_7 = in_010 + out_010 + pred_010 + outome_0131 + covar_010
sql_moderate_b_8 = in_15 + out_11 + pred_11 + outcome_11 + covar_11
sql_moderate_b_9 = in_11 + out_11 + pred_15 + outcome_11 + covar_11
sql_moderate_b_10 = in_11 + out_11 + pred_11 + outcome_11 + covar_15
sql_moderate_b_11 = in_10 + out_11 + pred_15 + outcome_11 + covar_11
sql_moderate_b_12 = in_10 + out_17 + pred_11 + outcome_11 + covar_11
sql_hard_b_1 = in_014 + out_010 + pred_010 + outome_010 + covar_010
sql_hard_b_2 = in_010 + out_014 + pred_010 + outome_010 + covar_010
sql_hard_b_3 = in_010 + out_010 + pred_010 + outome_014 + covar_010
sql_hard_b_4 = in_010 + out_010 + pred_010 + outome_010 + covar_014
sql_hard_b_5 = in_0141 + out_010 + pred_010 + outome_010 + covar_010
sql_hard_b_6 = in_010 + out_0141 + pred_010 + outome_010 + covar_010
sql_hard_b_7 = in_010 + out_010 + pred_010 + outome_0141 + covar_010
sql_hard_b_8 = in_010 + out_010 + pred_010 + outome_010 + covar_0141
sql_hard_b_9 = in_11 + out_11 + pred_12 + outcome_11 + covar_12
sql_hard_b_10 = in_11 + out_11 + pred_11 + outcome_12 + covar_11
sql_hard_b_11 = in_14 + out_14 + pred_14 + outcome_14 + covar_14
sql_hard_b_12 = in_10 + out_18 + pred_15 + outcome_11 + covar_16
sql_easy_c_1 = in_01 + out_0221 + pred_01 + outcome_01 + covar_01
sql_easy_c_2 = in_01 + out_01 + pred_0221 + outcome_01 + covar_01
sql_easy_c_3 = in_cc1 + out_01 + pred_01 + outcome_01 + covar_01
sql_easy_c_4 = in_01 + out_cc2 + pred_01 + outcome_01 + covar_01
sql_easy_c_5 = in_01 + out_01 + pred_01 + outcome_01 + covar_01
sql_easy_c_6 = in_01 + out_01 + pred_cc3 + outcome_cc4 + covar_01
sql_easy_c_7 = in_01 + out_01 + pred_01 + outcome_01 + covar_cc5
sql_easy_c_8 = in_ccc6 + out_01 + pred_01 + outcome_01 + covar_01
sql_easy_c_9 = in_01 + out_cc7 + pred_01 + outcome_01 + covar_01
sql_easy_c_10 = in_01 + out_01 + pred_01 + outcome_cc9 + covar_01
sql_easy_c_11 = in_01 + out_01 + pred_01 + outcome_01 + covar_cc10
sql_moderate_c_1 = in_023 + out_01 + pred_01 + outcome_01 + covar_01
sql_moderate_c_2 = in_01 + out_023 + pred_01 + outcome_01 + covar_01
sql_moderate_c_3 = in_01 + out_01 + pred_023 + outcome_01 + covar_01
sql_moderate_c_4 = in_01 + out_01 + pred_01 + outcome_023 + covar_01
sql_moderate_c_5 = in_0231 + out_01 + pred_01 + outcome_01 + covar_01
sql_moderate_c_6 = in_01 + out_0231 + pred_01 + outcome_01 + covar_01
sql_moderate_c_7 = in_01 + out_01 + pred_0231 + outcome_01 + covar_01
sql_moderate_c_8 = in_02 + out_01 + pred_01 + outcome_01 + covar_01
sql_moderate_c_9 = in_01 + out_01 + pred_02 + outcome_01 + covar_01
sql_moderate_c_10 = in_01 + out_02 + pred_01 + outcome_02 + covar_01
sql_moderate_c_11 = in_01 + out_01 + pred_01 + outcome_01 + covar_02
sql_hard_c_1 = in_024 + out_01 + pred_01 + outcome_01 + covar_01
sql_hard_c_2 = in_01 + out_024 + pred_01 + outcome_01 + covar_01
sql_hard_c_3 = in_01 + out_01 + pred_01 + outcome_024 + covar_01
sql_hard_c_4 = in_0241 + out_01 + pred_01 + outcome_01 + covar_01
sql_hard_c_5 = in_01 + out_0241 + pred_01 + outcome_01 + covar_01
sql_hard_c_6 = in_01 + out_01 + pred_01 + outcome_0241 + covar_01
sql_hard_c_7 = in_03 + out_01 + pred_01 + outcome_01 + covar_01
sql_hard_c_8 = in_01 + out_03 + pred_01 + outcome_01 + covar_01
sql_hard_c_9 = in_01 + out_01 + pred_03 + outcome_01 + covar_01
sql_hard_c_10 = in_01 + out_01 + pred_01 + outcome_03 + covar_01
sql_hard_c_11 = in_01 + out_01 + pred_01 + outcome_01 + covar_03
