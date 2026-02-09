period1 = "2011-2020"
synonyms1 = {
    "dr": [
        ["diabetes affected eyes/had retinopathy", "default"],
        ["diabetes related retinopathy"],
        ["retinopathy caused by diabetes"],
        ["DR in diabetes"],
    ],
    "albumin": [
        ["serum albumin (g/dL)", "default"],
        ["albumin"],
        ["blood albumin"],
        ["serum ALB lab"],
    ],
    "gender": [
        ["gender", "default"],
        ["patient's gender"],
        [
            "subject's identified description of alignment with reproductive classification"
        ],
    ],
    "age": [
        ["age in years at screening", "default"],
        ["age at screening"],
        ["patient's age"],
        ["chronological age"],
        ["time on earth"],
        ["time one has been around"],
    ],
    "race": [
        ["race/hispanic origin", "default"],
        ["ethnic background"],
        ["self-identified race"],
    ],
    "glycohemoglobin": [
        ["glycohemoglobin HbA1C (%)", "default"],
        ["HbA1C values"],
        ["memory of sugar in blood"],
        ["slow-changing sugar signal"],
        ["lingering sugar imprint"],
    ],
    "diabetes_status": [
        ["doctor told you have diabetes", "default"],
        ["diabetes diagnosis"],
        ["A1C ≥ 6.5%"],
        ["T2DM"],
    ],
    "diabetes_age": [
        ["age when first told the patient had diabetes", "default"],
        ["age at diabetes diagnosis"],
        ["diabetes onset age"],
        ["when first informed about blood glucose disease"],
        ["years at initial blood sugar disease confirmation"],
    ],
}

free_q1 = f"""
Using NHANES data, We plan to conduct a logistic regression analysis to examine the relationship between {{albumin}} and {{dr}} using data from the years 2011 to 2020. 
The study will include all individuals whose {{age}} was 30 years or older who have complete data on both {{albumin}} and {{dr}} status.
Participants will be excluded if their {{age}} is less than 30 years old, or {{diabetes_age}} was before age 30, or had uncertain diabetes status. 
Uncertainty is based on their answer to the question "{{diabetes_status}}" and if they answer as borderline and either have a missing {{glycohemoglobin}} value or {{glycohemoglobin}} below 6.5%. 
We will also exclude anyone with missing data on {{albumin}} or {{dr}}.
The main predictor in the analysis will be {{albumin}}, categorized into quartiles Q1: <25%, Q2: ≥25 and <50, Q3: ≥50 and <75%, Q4: ≥75%. 
The outcome variable will be the presence or absence of diabetic retinopathy, based on responses to the question {{dr}}, coded as 1 for "Yes" and 0 for "No".
We will adjust the analysis for potential confounding factors including {{gender}}, {{age}}, and {{race}}, which will be categorized as White, Black, Mexican American, or Other.
"""


free_q2 = f"""
We will plan to do a weighted logistic regression using exam weights from NHANES data from 2007-2018. 
We will include participants who has diabetes when diabetes is defined as meeting any of the following requirements: reported yes when asked about self-reported doctor diagnosis of diabetes, or {{fasting_plasma_glucose}} ≥7.0 mmol/L, or glycohemoglobin (HbA1c) (%) ≥6.5%, or {{diabetes_med}}. 
We will exclude participants whose age at screening is less than 20, {{pregnancy}}, and had missing values of {{weight}}, {{waist_circumference}}.
We will exclude participants who are missing gender, race/hispanic origin, {{urine_albumin}}, or {{urine_creatinine}}, {{serum_creatinine}}. 
The predictor is weight-adjusted-waist (wwi) ratio which is calculated as {{waist_circumference}} divided by the square root of {{weight}}, categorized as quartiles(%) Q1: ≤25, Q2: >25 and ≤50, Q3: >50 and ≤75, Q4: >75.
The outcome of interest is the presence of kidney disease, defined as either an estimated glomerular filtration rate (eGFR) below 60 mL/min/1.73m^2 or a urine albumin-to-creatinine ratio (UACR) (mg/g) of 30 mg/g or greater. 
eGFR can be calculated using gender, {{serum_creatinine}}, age at screening, race/hispanic origin information for 4 different cases: 
1. if gender is female and race/hispanic origin is Non-Hispanic Black : 141 * min({{serum_creatinine}} / 0.7, 1) ** -0.329 * max({{serum_creatinine}} / 0.7, 1) ** -1.209 * (0.993 ** age at screening) * 1.018 * 1.159
2. if gender is female and race/hispanic origin is not Non-Hispanic Black : 141 * min({{serum_creatinine}} / 0.7, 1) ** -0.329 * max({{serum_creatinine}} / 0.7, 1) ** -1.209 * (0.993 ** age at screening) * 1.018
3. if gender is male and race/hispanic origin os Non-Hispanic Black : 141 * min({{serum_creatinine}} / 0.9, 1) ** -0.411 * max({{serum_creatinine}} / 0.9, 1) ** -1.209 * (0.993 ** age at screening) * 1.159
4. if gender is male and race/hispanic origin is not Non-Hispanic Black : 141 * min({{serum_creatinine}} / 0.9, 1) ** -0.411 * max({{serum_creatinine}} / 0.9, 1) ** -1.209 * (0.993 ** age at screening)
urine albumin-to-creatinine ratio (mg/g) is calculated as 100*({{urine_albumin}}/ {{urine_creatinine}}).
Adjust the analysis for race/hispanic origin (white and non white), gender, and age at screening (<60 and >=60).
"""


period2 = "2007-2018"
synonyms2 = {
    "fasting_plasma_glucose": [
        ["fasting glucose (mmol/l)", "default"],
        ["fasting glucose"],
        ["pre-meal blood sugar"],
        ["FPG"],
        ["zero-snack sugar measurement"],
        ["your body's 'nothing eaten yet' sugar score"],
        ["carb supply measure after no food"],
        ["carb availability in blood before eating"],
        ["empty-stomach carb check"],
        ["blood sweetness before any bites"],
    ],
    "urine_albumin": [
        ["albumin, urine (mg/l)", "default"],
        ["albumin urine concentration"],
        ["urine protein (albumin)"],
        ["urinary albumin"],
        ["renal albumin loss"],
    ],
    "diabetes_med": [
        ["take diabetic pills to lower blood sugar", "default"],
        ["antidiabetic drugs"],
        ["medication aimed at taming high glucose"],
        ["pharmaceutical help for sugar regulation"],
        ["treatment that keeps sugar from running wild"],
        ["supportive meds for metabolic balance"],
        ["oral hypoglycemics"],
    ],
    "weight": [
        ["weight (kg)", "default"],
        ["body mass"],
        ["how heavy the person is"],
        ["overall mass measurement"],
        ["total body load"],
        ["amount of body heft"],
        ["physical load someone carries"],
        ["body's physical burden"],
        ["full body heft score"],
    ],
    "waist_circumference": [
        ["waist circumference (cm)", "default"],
        ["circumference of waist"],
        ["abdominal circumference"],
        ["waist perimeter"],
        ["midsection circumference"],
        ["circle of the waistline"],
        ["encirclement of the waist"],
        ["waist contour"],
        ["midsection loop"],
    ],
    "urine_creatinine": [
        ["creatinine, urine (mg/dl)", "default"],
        ["creatinine content in urine sample"],
        ["creatinine in collected urine"],
        ["creatinine in urine"],
        ["urinary trace of creatinine"],
        ["urinary metabolite creatinine"],
        ["creatinine elimination in urine"],
        ["renal creatinine excretion"],
        ["creatinine discharge rate"],
        ["creatinine removal via urination"],
        ["the body's silent exhale (creatinine)"],
    ],
    "serum_creatinine": [
        ["creatinine (mg/dl)", "default"],
        ["creatinine blood value"],
        ["serological creatinine measurement"],
        ["serum creatinine diagnostic value"],
        ["creatinine test in blood"],
        ["creatinine blood assay"],
        ["kidney function creatinine test"],
        ["circulating marker of metabolism"],
        ["biochemical footprint of exertion"],
        ["metabolic residue in bloodstream"],
        ["the bloodstream's waste whisper"],
        ["the plasma's muscle memory"],
        ["the pulse of metabolic waste"],
        ["molecular shadow of muscle work"],
        ["SCr"],
    ],
    "pregnancy": [
        ["pregnancy status at exam", "default"],
        ["patient pregnancy evaluation"],
        ["active pregnancy status"],
        ["pregnancy condition"],
        ["pregnancy occurrence"],
        ["gestational presence"],
        ["gestational phase"],
        ["maternal gestational phase"],
        ["gravid state"],
        ["gravidity"],
    ],
}


period3 = "2011-2014"
synonyms3 = {
    "insulin_therapy_duration": [
        ["how long taking insulin", "default"],
        ["insulin treatment duration"],
        ["insulin administration"],
        ["use of an insulin pump"],
        ["insulin regimen"],
    ],
    "q1": [
        ["have little interest in doing things", "default"],
        ["lack of motivation or drive"],
        ["finding no pleasure in things you once enjoyed"],
        ["lost interest"],
        ["bored with life"],
        ["no mood for anything"],
        ["no desire"],
        ["can't enjoy life"],
        ["feel lifeless"],
        ["no thrill"],
        ["anhedonia"],
        ["joy feels distant or unreachable"],
        ["no drive"],
        ["feels like joy has gone missing"],
        ["used to love it, now I just don't"],
        ["no pleasure"],
        ["don't care anymore"],
        ["the color has drained out of life"],
        ["checked out"],
    ],
    "q2": [
        ["feeling down, depressed, or hopeless", "default"],
        ["feeling burdened by sadness or defeat"],
        ["depressed mood"],
        ["sense of futility or giving up"],
        ["feeling melancholic"],
        ["sense that joy is out of reach"],
        ["feeling emotionally drained or flat"],
        ["emotional state marked by weariness and loss"],
    ],
    "q3": [
        ["trouble sleeping or sleeping too much", "default"],
        ["difficulty falling or staying asleep"],
        ["unrestful sleep or daytime sleepiness"],
        ["altered sleep patterns"],
        ["wakeful nights or sluggish mornings"],
        ["disrupted sleep cycle"],
        ["restless through the night or heavy in the morning"],
        ["tossing and turning or lying in all day"],
        ["difficulties with resting patterns"],
        ["irregular rest habits"],
        ["lack of restorative rest"],
        ["up all night or down all day"],
        ["problems with rest duration"],
        ["days start late or nights never end"],
        ["inconsistent rest schedule"],
        ["body clock lost its map"],
    ],
    "q4": [
        ["feeling tired or having little energy", "default"],
        ["fatigue or lethargy"],
        ["feeling constantly drained or exhausted"],
        ["persistent tiredness"],
        ["tired beyond reason or rest"],
        ["fatigue that makes daily life harder"],
        ["pushing through a constant haze of fatigue"],
        ["unable to sustain usual activity levels"],
        ["body feels heavy, spirit feels flat"],
        ["drained of vitality"],
        ["dragging through the day without momentum"],
        ["energy burned out like a dying flame"],
        ["every motion feels uphill"],
        ["running on fumes"],
        ["nothing left in the tank"],
    ],
    "q5": [
        ["poor appetite or overeating", "default"],
        ["changes in appetite or eating habits"],
        ["neglecting meals or overdoing them"],
        ["compulsive eating or complete disinterest"],
        ["urge to eat when not hungry, or none when should"],
        ["unsteady eating rhythm"],
        ["hunger patterns unpredictable"],
        ["eating significantly more or less than usual"],
        ["ravenous days followed by fasting ones"],
        ["swinging between starvation and indulgence"],
        ["turning to food for solace or losing taste for it"],
        ["food as escape or as obligation"],
        ["consumption patterns completely off balance"],
        ["seeking comfort through taste or rejecting it"],
        ["irregular portions and unpredictable timing"],
    ],
    "q6": [
        ["feeling bad about yourself", "default"],
        ["believing you're a burden or disappointment"],
        ["self-worth tangled in regret or guilt"],
        ["feeling small or undeserving"],
        ["feeling fundamentally flawed or unfixable"],
        ["feeling unworthy of kindness or success"],
        ["living under the weight of your own criticism"],
        ["believing others are better than you"],
        ["carrying a sense of failure"],
        ["seeing yourself as undeserving of kindness"],
        ["constant comparison and self-doubt"],
        ["hard to forgive yourself for past actions"],
        ["expecting rejection or judgment constantly"],
    ],
    "q7": [
        ["trouble concentrating on things", "default"],
        ["difficulty concentrating or focusing"],
        ["feeling easily distracted"],
        ["distracted by everything or nothing"],
        ["attention drifts easily"],
        ["mind feels dull or unfocused"],
        ["struggling to stay mentally anchored"],
    ],
    "q8": [
        ["moving or speaking slowly or too fast", "default"],
        ["movement too quick for calm or too slow for clarity"],
        ["noticeable shift in how quickly you move or speak"],
        ["nervous gestures or heavy hesitation"],
        ["rushing without control or slowing without intent"],
        ["feeling physically slowed down"],
        ["gestures too quick or too faint to match intention"],
        ["feeling trapped between stillness and speed"],
        ["unable to sit still or unable to start moving"],
        ["physical rhythm feels broken or unstable"],
        ["body either in overdrive or low gear"],
        ["trapped between acceleration and paralysis"],
    ],
    "q9": [
        ["thought you would be better off dead", "default"],
        ["Contemplating that my absence would be better than my presence"],
        ["The internal script says I deserve oblivion"],
        ["Feeling like everyone would be relieved if I were gone"],
        ["My mind constantly suggests self-removal"],
        ["A persistent desire to fade away entirely"],
    ],
}

free_q3 = f"""
Among participants in the 2005-2012 NHANES data, include paricipants who meet all of these criteria: self-reported diagnosis of diabetes is yes and diabetes onset >=30  and age at screening >=30
We will exclude patients who were pregnant at the exam, exclude patipant whose difference between the duration of diabetes and {{insulin_therapy_duration}}, calculated as (age at screening - diabetes onset)- {{insulin_therapy_duration}} is equal or less than 1 year.
We will calculate the weighted prevalence using exam weights. We will look at prevalence of clinically relevant depression, defined by the following 9 questionaires:
"{{q1}}", "{{q2}}", "{{q3}}", "{{q4}}", "{{q5}}", "{{q6}}", "{{q7}}", "{{q8}}", "{{q9}}". 
The total score from the nine questions were calculated where each question has value of Not at all (0), Several days (1), More than half the days (2), Nearly every day (3), if value is null assign (0), and the total score >=10 was defined as clinically relevant depression and else was not. 
"""
