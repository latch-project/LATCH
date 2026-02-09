#!/usr/bin/env python3

import argparse
import os
import re
from typing import Dict

import pandas as pd
from tqdm import tqdm

# Selenium only needed if scraping the dictionary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

URL = "https://docs.aireadi.org/v3-omopAndClinicalTable"


def clean_var_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = re.sub(r"[ ,()\-\/%]", "_", name.strip().lower())
    name = re.sub(r"[^\w]", "_", name)
    return re.sub(r"_+", "_", name).strip("_")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def scrape_dictionary_to_csv(input_folder: str, headless: bool = True) -> str:
    """Scrape the docs table into input_folder/omop_dictionary.csv and return path."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Try to expand rows per page if a <select> exists
        try:
            dropdown = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select"))
            )
            sel = Select(dropdown)
            sel.select_by_index(len(sel.options) - 1)
            wait.until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr")) > 0
            )
        except Exception:
            pass

        html = driver.page_source
        df = pd.read_html(html)[0]
    finally:
        driver.quit()

    df.columns = [clean_var_name(c) for c in df.columns]
    df = df.apply(lambda col: col.str.lower() if col.dtype == "object" else col)

    out_path = os.path.join(input_folder, "omop_dictionary.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path} with rows: {len(df)}")
    return out_path


def load_inputs(input_folder: str):
    clinical = os.path.join(input_folder, "clinical_data")
    measurement_df = pd.read_csv(os.path.join(clinical, "measurement.csv"))
    observation_df = pd.read_csv(os.path.join(clinical, "observation.csv"))
    condition_df = pd.read_csv(os.path.join(clinical, "condition_occurrence.csv"))
    person_df = pd.read_csv(os.path.join(clinical, "person.csv"))
    return measurement_df, observation_df, condition_df, person_df


def write_person(person_df: pd.DataFrame, output_folder: str) -> None:
    filtered = person_df[["person_id", "year_of_birth"]].sort_values("person_id")
    out = os.path.join(output_folder, "person.csv")
    filtered.to_csv(out, index=False)
    print(f"Saved {out} ({len(filtered)} rows)")


def split_observation_for_condition(
    observation_df: pd.DataFrame, condition_df: pd.DataFrame
):
    """
    Your logic: find observation rows whose qualifier_concept_id matches
    condition_occurrence.condition_concept_id.
    """
    if "condition_concept_id" not in condition_df.columns:
        return observation_df.iloc[0:0].copy(), observation_df.copy()

    matching_observations = observation_df[
        observation_df["qualifier_concept_id"].isin(
            condition_df["condition_concept_id"]
        )
    ].copy()

    used_rows = observation_df["qualifier_concept_id"].isin(
        matching_observations["qualifier_concept_id"]
    )
    observation_remaining = observation_df[~used_rows].copy()
    return matching_observations, observation_remaining


def write_condition_occurrence(
    matching_observations: pd.DataFrame,
    dic_df: pd.DataFrame,
    condition_df: pd.DataFrame,
    person_df: pd.DataFrame,
    output_folder: str,
) -> None:
    # Filter dictionary rows for condition ids
    condition_ids = condition_df["condition_concept_id"].unique()
    matching_dic = dic_df[dic_df["qualifier_concept_id"].isin(condition_ids)].copy()

    result_df = matching_dic[
        ["qualifier_concept_id", "src_cd_description", "target_concept_name"]
    ].copy()

    # Clean src_cd_description
    result_df["cleaned_src_cd_description"] = (
        result_df["src_cd_description"].dropna().apply(clean_var_name)
    )

    merged = matching_observations.merge(
        result_df, on="qualifier_concept_id", how="inner"
    )
    final_df = merged[
        ["person_id", "value_as_number", "cleaned_src_cd_description"]
    ].copy()
    final_df["value"] = final_df["value_as_number"].map({1: "Yes", 0: "No"})

    pivot = final_df.pivot_table(
        index="person_id",
        columns="cleaned_src_cd_description",
        values="value",
        aggfunc="first",
    ).reset_index()
    pivot.columns.name = None
    pivot.columns = [str(c) for c in pivot.columns]

    final = (
        person_df[["person_id"]]
        .drop_duplicates()
        .merge(pivot, on="person_id", how="left")
    )

    # rename a couple columns
    rename_map = {
        "retinal_vascular_occlusion_stroke_in_the_eye_or_eye_vessels_in_one_or_both_eyes": "retinal_vascular_occlusion_stroke_in_the_eye",
        "age_related_macular_degeneration_amd_in_one_or_both_eyes": "age_related_macular_degeneration_amd_in_one_or_both",
    }
    final = final.rename(
        columns={k: v for k, v in rename_map.items() if k in final.columns}
    )
    final = final.sort_values("person_id")

    out = os.path.join(output_folder, "condition_occurrence.csv")
    final.to_csv(out, index=False)
    print(f"Saved {out} ({final.shape[0]} rows, {final.shape[1]} cols)")


def write_measurement(measurement_df: pd.DataFrame, output_folder: str) -> None:
    measurement_df = measurement_df[
        [
            "person_id",
            "measurement_source_value",
            "value_as_number",
            "unit_source_value",
        ]
    ].copy()

    dic_map = {
        "mlcsodfcl": "od_value_of_final_correct_letter_mesopic",
        "mlcsodmiss": "od_number_of_misses_prior_to_stoppin_mesopic",
        "mlcsodlog": "od_log_contrast_sensitivity_mesopic",
        "mlcsosfcl": "os_value_of_final_correct_letter_mesopic",
        "mlcsosmiss": "os_number_of_misses_prior_to_stoppin_mesopic",
        "mlcsoslog": "os_log_contrast_sensitivity_mesopic",
        "plcsodfcl": "od_value_of_final_correct_letter_photopic",
        "plcsodmiss": "od_number_of_misses_photopic",
        "plcsodlog": "od_log_contrast_sensitivity_photopic",
        "plcsosfcl": "os_value_of_final_correct_letter_photopic",
        "plcsosmiss": "os_number_of_misses_photopic",
        "plcsoslog": "os_log_contrast_sensitivity_photopic",
        "bp1_sysbp_vsorres": "systolic_mmhg_1st",
        "bp1_diabp_vsorres": "diastolic_mmhg_1st",
        "pulse_vsorres": "heart_rate_bpm_1st",
        "bp2_sysbp_vsorres": "systolic_mmhg_2nd",
        "bp2_diabp_vsorres": "diastolic_mmhg_2nd",
        "pulse_vsorres_2": "heart_rate_bpm_2nd",
        "import_nt_probnp": "natriuretic_peptide_b_pg_ml",
        "import_troponin_t": "troponin_t_cardiac_ng_l",
        "import_c_peptide": "c_peptide_ng_l",
        "import_insulin": "insulin_ng_l",
        "import_crp_hs": "c_reactive_protein_mg_l",
        "import_total_cholesterol": "total_cholesterol_mg_dl",
        "import_triglycerides": "triglyceride_mg_dl",
        "import_hdl_cholesterol": "hdl_cholesterol_mg_dl",
        "import_ldl_cholesterol": "ldl_cholesterol_mg_dl",
        "import_glucose": "glucose_mg_dl",
        "import_bun": "urea_nitrogen_mg_dl",
        "import_creatinine": "creatinine_mg_dl",
        "import_buncreatinineratio": "bun_creatinine_ratio",
        "import_sodium": "sodium_meq_l",
        "import_potassium": "potassium_meq_l",
        "import_chloride": "chloride_meq_l",
        "import_carbon_dioxide_total": "carbon_dioxide_total_meq_l",
        "import_calcium": "calcium_meq_l",
        "import_protein_total": "total_protein_g_dl",
        "moca_orientation": "moca_orientation",
        "import_albumin": "albumin_g_dl",
        "import_globulin_total": "globulin_total",
        "import_a_g_ratio": "albumin_globulin_ratio",
        "import_bilirubin_total": "bilirubin_total",
        "import_alkaline_phosphatase": "alkaline_phosphatase_iu_l",
        "import_ast_got": "ast_iu_l",
        "import_alt_got": "alt_iu_l",
        "import_hba1c": "glycohemoglobin_hba1c_percent",
        "import_urine_creatinine": "urine_creatinine_ug_ml",
        "import_urine_albumin": "urine_albumin_ug_ml",
        "lbscat_hct": "hematocrit_percent",
        "lbscat_mch": "mean_corpuscular_hemoglobin_pg",
        "lbscat_mchc": "mean_corpuscular_hemoglobin_concentration_g_dl",
        "lbscat_mcv": "mean_corpuscular_volume_fl",
        "lbscat_plt": "platelets_x10e3_per_ul",
        "lbscat_rbc": "red_blood_cells_x10e6_per_ul",
        "lbscat_rdw": "red_cell_distribution_width_percent",
    }

    def short_key(val):
        if pd.isna(val):
            return val
        return str(val).split(",", 1)[0].strip()

    def map_measurement_source_value(val):
        if pd.isna(val):
            return val
        s = str(val).strip()
        key = short_key(s)
        if key in dic_map:
            return dic_map[key]
        if "," in s:
            return s.split(",", 1)[1].strip()
        return s

    measurement_df["_short_key"] = measurement_df["measurement_source_value"].apply(
        short_key
    )
    measurement_df["_mapped_raw"] = measurement_df["measurement_source_value"].apply(
        map_measurement_source_value
    )
    measurement_df["measurement_source_value_map"] = measurement_df[
        "_mapped_raw"
    ].apply(clean_var_name)

    measurement_df = measurement_df[
        [
            "person_id",
            "measurement_source_value",
            "measurement_source_value_map",
            "value_as_number",
            "unit_source_value",
        ]
    ].copy()

    pivot_df = measurement_df.pivot_table(
        index="person_id",
        columns="measurement_source_value_map",
        values="value_as_number",
        aggfunc="first",
    ).reset_index()
    pivot_df.columns.name = None
    pivot_df = pivot_df.sort_values("person_id")

    out = os.path.join(output_folder, "measurement.csv")
    pivot_df.to_csv(out, index=False)
    print(f"Saved {out} (shape: {pivot_df.shape})")


def parse_rename_text_block(text_block: str) -> Dict[str, str]:
    chunks = text_block.strip().split("\n\n")
    rename_dict: Dict[str, str] = {}
    for chunk in chunks:
        lines = chunk.strip().split("\n")
        if len(lines) == 2:
            old_name, new_name = lines
            rename_dict[old_name.strip()] = new_name.strip()
    return rename_dict


def write_observation(
    observation_remaining: pd.DataFrame, dic_df: pd.DataFrame, output_folder: str
) -> None:
    columns_to_keep = [
        "person_id",
        "observation_concept_id",
        "value_as_number",
        "value_as_string",
        "observation_source_value",
    ]
    filtered_df = observation_remaining[columns_to_keep].copy()

    filtered_df["observation_source_value_formatted"] = (
        filtered_df["observation_source_value"].str.split(", ", n=1).str[-1].str.lower()
    )

    # Fix known broken strings
    mask = (
        filtered_df["observation_source_value_formatted"] == 'i could not "get going"'
    )
    filtered_df.loc[
        mask, "observation_source_value_formatted"
    ] = 'i could not "get going'
    filtered_df["observation_source_value_formatted"] = (
        filtered_df["observation_source_value_formatted"]
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )
    mask = (
        filtered_df["observation_source_value_formatted"]
        == "\"(i/we) couldn't afford to eat balanced me"
    )
    filtered_df.loc[mask, "observation_source_value_formatted"] = "eat balanced me"

    filtered_df = filtered_df.drop_duplicates()

    dic_filtered = dic_df[dic_df["target_domain_id"] == "observation"][
        [
            "target_concept_id",
            "src_cd_description",
            "choices_calculations_or_slider_labels",
        ]
    ].copy()

    filtered_df["observation_source_value_formatted"] = (
        filtered_df["observation_source_value_formatted"]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    dic_filtered["src_cd_description_clean"] = (
        dic_filtered["src_cd_description"].astype(str).str.strip().str.lower()
    )

    merged_rows = []
    for _, row in tqdm(
        filtered_df.iterrows(), total=len(filtered_df), desc="Merging dictionary info"
    ):
        obs_id = row["observation_concept_id"]
        obs_val = row["observation_source_value_formatted"]

        subset_dic = dic_filtered[dic_filtered["target_concept_id"] == obs_id]

        match_found = False
        for _, dic_row in subset_dic.iterrows():
            if obs_val in dic_row["src_cd_description_clean"]:
                combined = row.to_dict()
                combined.update(
                    {
                        "matched_target_concept_id": dic_row["target_concept_id"],
                        "matched_src_cd_description": dic_row["src_cd_description"],
                        "matched_choices": dic_row[
                            "choices_calculations_or_slider_labels"
                        ],
                    }
                )
                merged_rows.append(combined)
                match_found = True
                break

        if not match_found:
            combined = row.to_dict()
            combined.update(
                {
                    "matched_target_concept_id": pd.NA,
                    "matched_src_cd_description": pd.NA,
                    "matched_choices": pd.NA,
                }
            )
            merged_rows.append(combined)

    final_df = pd.DataFrame(merged_rows).drop_duplicates()

    def parse_choices(choice_str):
        mapping = {}
        parts = str(choice_str).split("|")
        for part in parts:
            items = part.strip().split(",", 1)
            if len(items) == 2:
                key = items[0].strip()
                val = items[1].strip()
                mapping[key] = val
        return mapping

    def get_label(row):
        choices = row["matched_choices"]
        val_num = row["value_as_number"]
        val_string = row["value_as_string"]

        if pd.notna(choices):
            choices_lower = str(choices).lower()
            mapping = parse_choices(choices_lower)

            if "c51773" in choices_lower:
                key = str(val_string).lower() if pd.notna(val_string) else ""
                label = mapping.get(key, None)
                return label if label is not None else val_string

            if "|" in str(choices):
                try:
                    label = mapping.get(str(int(val_num)), None)
                except (ValueError, TypeError):
                    label = None
                return label if label is not None else val_num

        return val_num

    final_df["value_label"] = final_df.apply(get_label, axis=1)
    final_df = final_df.drop_duplicates()

    # force-match some known items
    target_values = [
        "years_of_education",
        "moca_total_score_time",
        "test_upload_date",
        "clock_visuospatial_executive",
        "digitspan",
        "age_years_at_interview",
        "cage, Age (in years)",
        "brthyy, Year (e.g. 1967)",
    ]
    final_df.loc[
        final_df["observation_source_value"].isin(target_values),
        "matched_src_cd_description",
    ] = final_df["observation_source_value"]

    final_df = final_df.drop_duplicates()
    final_df = final_df[
        ["person_id", "matched_src_cd_description", "value_label"]
    ].drop_duplicates()

    exclude_values = [
        "date procedure performed",
        "how often in the past year?",
        "how often in your entire life?",
        "on a scale of 1-6, how stressful was this for you? 1 = not at all stressful; 6 = extremely stressful",
        "on a scale of 1-6, how stressful was this",
        "date device given to participant",
        "during the past 12 months, how many times",
        "about how long has it been since you last",
        "in the last 12 months, was there any time",
        "how often would you say that you engage i",
        "a doctor or nurse acts as if he or she is",
        "pre-consent survey completed timestamp (from redcap)",
        "optomed-disc centered-cfp",
        "optomed-mac centered-cfp",
        "eidon-uwf central-ir",
        "spec-onh-rc-hr-oct",
        "spec-ppole mac-hr-61 lines-oct",
        "spec-mac-20x20-hs-512 lines-octa",
        "cirrus-mac cube-512x128-oct",
        "eidon-uwf central-faf",
        "eidon-uwf central-cfp",
        "eidon-uwf nasal-cfp",
        "eidon-uwf temporal-cfp",
        "triton-macula 6x6-octa",
        "m2-3d macula 6x6-oct",
        "m2-mac 6x6-360x360-(rep3)-octa",
        "triton-3d(h)+radial 12x9-oct",
        "flio-mac-hs",
        "triton-macula 12x12-octa",
        "cirrus-macula 6x6-octa",
        "cirrus-disc cube-200x200-oct",
        "cirrus-disc 6x6-octa",
        "m2-3d wide(h) 12x9-oct",
        "if yes, which parent?",
        "if yes, please check all that apply:",
        "in what form do you usually use marijuana? (check all that apply)",
        "think about the place you live. do you have problems with any of the following? choose all that apply",
        "moca_total_score_time",
    ]
    initial_count = len(final_df)
    final_df = final_df[~final_df["matched_src_cd_description"].isin(exclude_values)]
    print(f"Observation rows: {initial_count} -> {len(final_df)} after exclude filter")

    pivot_df = final_df.pivot_table(
        index="person_id",
        columns="matched_src_cd_description",
        values="value_label",
        aggfunc="first",
    ).reset_index()

    pivot_df.columns = [clean_var_name(col) for col in pivot_df.columns]
    pivot_df.columns.name = None

    # Column rename mapping (your big text_block)
    text_block = """
person_id
person_id

i_we_couldn_t_afford_to_eat_balanced_meals_was_that_often_sometimes_or_never_true_for_you_your_household_in_the_last_12_months
could_not_afford_balanced_meals_in_the_last_12_months

a_doctor_or_nurse_acts_as_if_he_or_she_is_afraid_of_you
doctor_or_nurse_seems_afraid_of_you

a_doctor_or_nurse_acts_as_if_he_or_she_is_better_than_you
doctor_or_nurse_thinks_they_are_better_than_you

a_doctor_or_nurse_acts_as_if_he_or_she_thinks_you_are_not_smart
doctor_or_nurse_thinks_you_are_not_smart

about_how_easy_would_it_be_for_you_to_find_a_job_with_another_employer_with_approximately_the_same_income_and_fringe_benefits_you_now_have_would_you_say_very_easy_somewhat_easy_or_not_easy_at_all
ease_of_finding_similar_job_with_same_pay_and_benefits

about_how_long_has_it_been_since_you_last_saw_a_doctor_or_other_health_care_professional_about_your_health
time_since_last_health_visit_with_doctor_or_professional

about_how_long_has_it_been_since_you_last_saw_a_doctor_or_other_health_professional_for_a_wellness_visit_physical_or_general_purpose_check_up
time_since_last_wellness_visit

about_how_many_miles_did_you_personally_drive_during_the_past_12_months_in_all_motorized_vehicles
miles_did_you_personally_drive_during_the_past_12_months

age_years_at_interview
age_years_at_interview

any_other_type_of_health_insurance_coverage_or_health_coverage_plan
other_health_insurance_coverage 

at_what_age_did_you_start_drinking_alcohol_age_started_years_old
age_started_drinking_alcohol

at_what_age_did_you_start_smoking_age_started_years_old
age_started_smoking

at_what_age_did_you_start_using_marijuana_age_started_years_old
age_started_using_marijuana

at_what_age_did_you_start_vaping_or_using_e_cigarettes_age_started_years_old
age_started_vaping_or_e_cigs

because_of_your_eyesight_how_much_difficulty_do_you_have_noticing_objects_off_to_the_side_while_you_are_walking_along_would_you_say
difficulty_noticing_objects_peripherally

cesd_10_score
cesd_10_score

coping_with_complications_of_diabetes
coping_with_complications_of_diabetes

did_any_other_person_in_your_household_delay_getting_prescription_medicines_because_of_worry_about_the_cost
household_member_delayed_prescription_medicines_due_to_cost

did_the_subject_complete_the_study
subject_completed_study

diet_score
diet_score

do_you_drive_after_having_a_drink_even_if_it_is_only_one_drink
drive_after_drinking_even_one_drink

do_you_inject_insulin_to_control_your_blood_glucose_levels
inject_insulin_for_blood_sugar

do_you_smoke_now
current_smoker

do_you_speak_another_language_at_home
speak_other_language_at_home

do_you_take_pills_to_control_your_a1c_and_blood_glucose_levels_examples_metformin_glucophage_glumetza_fortamet_riomet_glucotrol_amaryl_diabeta_blynase_prestab_micronase_actos_avandia_precose_glyset_prandin_starlix_januvia_onglyza_tradjenta_nesina_invokana_farxiga_jardiance_welchol_and_cyclocet
take_pills_to_control_a1c_and_blood_glucose

do_you_use_lifestyle_changes_to_control_your_a1c_and_blood_glucose_levels_examples_regular_exercise_avoiding_sugary_foods_and_beverages_eating_a_balanced_diet_with_lots_of_vegetables_sticking_to_a_consistent_eating_schedule
lifestyle_changes_to_control_a1c_and_blood_glucose

do_you_use_marijuana_now
current_marijuana_use

do_you_use_other_injections_to_control_your_blood_glucose_levels_examples_victoza_ozempic_symlin_tanzeum_and_trulicity
use_other_injections_for_blood_sugar

do_you_vape_or_use_e_cigarettes_now
current_vape_or_e_cigarette_use

does_this_mean_you_currently_have_no_health_insurance_or_health_coverage_plan_in_answering_this_question_please_exclude_plans_that_pay_for_only_one_type_of_service_such_as_nursing_home_care_accidents_family_planning_or_dental_care_and_plans_that_only_provide_extra_cash_when_hospitalized
currently_no_health_insurance_exclude_limited_plans

during_the_average_week_how_many_1_5_oz_of_liquor_do_you_usually_drink_either_as_shots_or_in_mixed_cocktails_number_of_drinks_per_week
weekly_liquor_drinks_shots_or_mixed

during_the_average_week_how_many_12_oz_bottles_or_cans_of_beer_do_you_usually_drink_number_of_bottles_or_cans_per_week
weekly_beer_cans_or_bottles

during_the_average_week_how_many_5_oz_glasses_of_wine_do_you_usually_drink_the_average_wine_bottle_has_5_servings_number_of_glasses_per_week
weekly_wine_glasses

during_the_past_12_months_have_you_been_hospitalized_overnight_do_not_include_an_overnight_stay_in_the_emergency_room
hospitalized_overnight_past_year

during_the_past_12_months_have_you_delayed_getting_medical_care_because_of_the_cost
delayed_medical_care_due_to_cost_past_year

during_the_past_12_months_how_many_times_have_you_gone_to_a_hospital_emergency_room_about_your_health_this_includes_emergency_room_visits_that_resulted_in_a_hospital_admission
emergency_room_visits_past_year

during_the_past_12_months_how_many_times_have_you_gone_to_an_urgent_care_center_or_a_clinic_in_a_drug_store_or_grocery_store_about_your_health_urgent_care_centers_and_clinics_in_drug_stores_or_grocery_stores_are_places_where_you_do_not_need_to_make_an_appointment_ahead_of_time_and_do_not_usually_see_the_same_health_care_provider_at_each_visit_this_is_different_from_a_hospital_emergency_room
urgent_care_or_clinic_visits_past_year

during_the_past_12_months_was_there_any_time_when_you_needed_medical_care_but_did_not_get_it_because_of_the_cost
needed_medical_care_but_did_not_get_due_to_cost

feeling_depressed_when_you_think_about_living_with_diabetes
feel_depressed_about_living_with_diabetes

feeling_scared_when_you_think_about_living_with_diabetes
feel_scared_about_living_with_diabetes

feeling_that_diabetes_is_taking_up_too_much_of_your_mental_and_physical_energy_every_day
diabetes_drains_mental_and_physical_energy

has_a_sibling_been_diagnosed_with_type_ii_diabetes
sibling_has_type_2_diabetes

have_you_been_diagnosed_with_any_conditions_not_listed_above_any_condition_not_just_eyes
diagnosed_with_other_medical_conditions

have_you_ever_consumed_alcohol
ever_consumed_alcohol

have_you_ever_used_marijuana_cannabis_this_includes_smoking_marijuana_using_cannabis_concentrates_and_edibles
ever_used_marijuana_or_cannabis

have_you_ever_vaped_or_used_e_cigarettes
ever_vaped_or_used_e_cigarettes

have_you_fallen_in_the_last_12_months_a_fall_is_defined_as_an_event_which_results_in_a_person_coming_to_rest_inadvertently_on_the_ground_or_floor_or_other_lower_level
fallen_in_last_12_months

have_you_had_any_beer_or_ale_in_the_past_year
had_beer_or_ale_past_year

have_you_had_any_liquor_in_the_past_year_such_as_brandy_whiskey_vodka_gin_schnapps_cocktails_or_liqueurs
had_liquor_past_year

have_you_had_any_wine_in_the_past_year
had_wine_past_year

have_you_smoked_at_least_100_cigarettes_or_more_in_your_lifetime_100_cigarettes_5_packs
smoked_100_plus_cigarettes_lifetime

have_you_taken_acetaminophen_medicines_such_as_tylenol_in_the_past_2_weeks
took_acetaminophen_past_2_weeks 

have_you_taken_antihistamines_such_as_cold_pills_or_allergy_pills_in_the_past_2_weeks
took_antihistamines_past_2_weeks

have_you_taken_aspirin_in_the_past_2_weeks
took_aspirin_past_2_weeks

have_you_taken_decongestants_such_as_cold_pills_or_allergy_pills_in_the_past_2_weeks
took_decongestants_past_2_weeks

have_you_taken_ibuprofen_or_ibuprofen_containing_medicines_such_as_advil_or_motrin_in_the_past_2_weeks
took_ibuprofen_or_advil_past_2_weeks

have_you_taken_sleeping_pills_in_the_past_2_weeks
took_sleeping_pills_past_2_weeks

how_many_hours_since_you_last_ate_number_of_hours
hours_since_last_meal

how_many_motor_vehicles_in_working_order_e_g_cars_trucks_motorcycles_are_there_at_your_household
motor_vehicles_in_household

how_many_regular_sodas_or_glasses_of_sweet_tea_did_you_drink_each_day
daily_sugary_drinks

how_many_servings_of_fruit_did_you_eat_each_day
daily_fruit_servings

how_many_servings_of_fruit_juice_did_you_drink_each_day
daily_fruit_juice_servings

how_many_servings_of_vegetables_did_you_eat_each_day
daily_vegetable_servings

how_many_times_a_week_did_you_eat_beans_like_pinto_or_black_beans_chicken_or_fish
weekly_beans_chicken_or_fish_intake

how_many_times_a_week_did_you_eat_desserts_and_other_sweets_not_the_low_fat_kind
weekly_desserts_or_sweets_intake

how_many_times_a_week_did_you_eat_fast_food_meals_or_snacks
weekly_fast_food_intake

how_many_times_a_week_did_you_eat_regular_snack_chips_or_crackers_not_low_fat
weekly_regular_chips_or_crackers

how_many_total_years_have_you_consumed_alcohol
total_years_alcohol_consumption

how_many_total_years_have_you_smoked
total_years_smoking 

how_many_total_years_have_you_used_marijuana
total_years_marijuana_use

how_many_total_years_have_you_vaped_or_used_e_cigarettes
total_years_vaping_or_e_cigareettes

how_much_difficulty_if_any_do_you_have_in_recognizing_a_friend_across_the_street_would_you_say
difficulty_recognizing_faces_across_street

how_much_difficulty_if_any_do_you_have_reading_print_in_newspapers_magazines_recipes_menus_or_numbers_on_the_telephone_would_you_say
difficulty_reading_small_print

how_much_margarine_butter_or_meat_fat_do_you_use_to_season_vegetables_or_put_on_potatoes_bread_or_corn
butter_or_fat_used_on_foods 

how_often_did_this_happen_almost_every_month_some_months_but_not_every_month_or_in_only_1_or_2_months
frequency_of_event

how_often_do_you_inspect_your_feet
foot_inspection_frequency

how_often_would_you_say_that_you_engage_in_daily_home_exercise_examples_stretching_calisthenics_or_yoga
frequency_of_home_exercise

how_often_would_you_say_that_you_engage_in_diabetes_health_education_examples_consulting_with_a_dietician_attending_support_groups_reading_books_on_diabetes_using_diabetes_focused_websites_watching_tv_shows_on_health_or_using_health_focused_apps_on_your_phone_or_tablet
frequency_of_diabetes_education_activities

i_could_not_get_going
i_could_not_get_going

i_felt_depressed
i_felt_depressed

i_felt_fearful
i_felt_fearful

i_felt_hopeful_about_the_future
i_felt_hopeful_about_the_future

i_felt_lonely
i_felt_lonely

i_felt_that_everything_i_did_was_an_effort
i_felt_that_everything_i_did_was_an_effort

i_had_trouble_keeping_my_mind_on_what_i_was_doing
i_had_trouble_keeping_my_mind_on_what_i_was_doing

i_see_many_people_being_physically_active_in_my_neighborhood_doing_things_like_walking_jogging_cycling_or_playing_sports_and_active_games_would_you_say_that_you
see_others_active_in_neighborhood

i_was_bothered_by_things_that_usually_don_t_bother_me
i_was_bothered_by_things_that_usually_don_t_bother_me

i_was_happy
i_was_happy

if_so_how_many_times_in_the_last_12_months
times_occurred_last_12_months

if_yes_at_what_age_were_you_first_diagnosed
if_yes_age_at_first_diagnosis

if_yes_please_check_all_that_apply
if_yes_check_all_that_apply

if_yes_please_choose_between
if_yes_choose_one

in_a_typical_day_how_many_servings_of_fruits_and_vegetables_do_you_consume
daily_fruit_and_vegetable_servings

in_a_typical_day_how_often_do_you_consume_whole_grains_examples_include_whole_wheat_brown_bread_or_brown_rice
daily_whole_grain_consumption 

in_a_typical_week_how_often_do_you_engage_in_vigorous_exercise_examples_hiking_jogging_at_6_mph_shoveling_carrying_heavy_loads_bicycling_fast_14_16_mph_playing_basketball_playing_soccer_playing_tennis_or_any_activity_during_which_you_cannot_say_more_than_a_few_words_without_taking_a_breath
weekly_vigorous_exercise_frequency

in_an_average_week_how_many_days_per_week_do_you_normally_drive_number_of_days
average_days_driven_per_week 

in_the_last_12_months_did_you_ever_eat_less_than_you_felt_you_should_because_there_wasn_t_enough_money_to_buy_food
ate_less_due_to_lack_of_money_past_12_months

in_the_last_12_months_have_you_delayed_getting_prescription_medicines_because_of_worry_about_the_cost
delayed_prescriptions_due_to_cost_past_12_months 

in_the_last_12_months_was_there_any_time_when_anyone_else_in_your_household_needed_prescription_medicines_but_did_not_get_them_because_you_they_couldn_t_afford_it
household_member_skipped_rx_due_to_cost_past_12_months

in_the_last_12_months_was_there_any_time_when_you_needed_prescription_medicines_but_did_not_get_them_because_you_couldn_t_afford_it
you_skipped_prescription_medicines_due_to_cost_past_12_months

in_the_last_12_months_were_you_ever_hungry_but_didn_t_eat_because_you_couldn_t_afford_enough_food
hungry_but_didnt_eat_due_to_cost_past_12_months

in_the_last_year_did_you_and_or_other_adults_in_your_household_ever_cut_the_size_of_your_meals_or_skip_meals_because_there_wasn_t_enough_money_for_food
cut_or_skipped_meals_due_to_cost_last_year

in_the_past_year
in_the_past_year

in_what_form_do_you_usually_use_marijuana_check_all_that_apply
form_of_marijuana_used

in_your_entire_life
in_your_entire_life

insurance_purchased_directly_from_an_insurance_company_by_you_or_another_family_member_this_would_include_coverage_purchased_through_an_exchange_or_marketplace_such_as_healthcare_gov
direct_purchase_or_marketplace_insurance 

insurance_through_a_current_or_former_employer_or_union_of_yours_or_another_family_member_s_this_would_include_cobra_coverage
employer_or_union_insurance_including_cobra

is_english_your_first_language
english_as_first_language

is_there_a_place_that_you_usually_go_to_if_you_are_sick_and_need_health_care
usual_place_for_health_care

it_is_within_a_10_15_minute_walk_to_a_transit_stop_such_as_bus_train_trolley_or_tram_from_my_home_would_you_say_that_you
within_15_min_walk_to_transit_from_home

many_shops_stores_markets_or_other_places_to_buy_things_i_need_are_within_easy_walking_distance_of_my_home_would_you_say_that_you
shops_within_easy_walking_distance

marital_status
marital_status

medicaid_medical_assistance_ma_the_children_s_health_insurance_program_chip_or_any_kind_of_state_or_government_sponsored_assistance_plan_based_on_income_or_a_disability
medicaid_chip_or_state_assistance_plan

medicare_for_people_65_and_older_or_people_with_certain_disabilities
medicare_for_65_plus_or_disabled

method_used_to_complete_form
method_used_to_complete_form

moca_total_score_time
moca_total_score_time

my_neighborhood_has_several_free_or_low_cost_recreation_facilities_such_as_parks_walking_trails_bike_paths_recreation_centers_playgrounds_public_swimming_pools_etc_would_you_say_that_you
access_to_free_or_low_cost_recreation_near_home

my_sleep_was_restless
my_sleep_was_restless

on_a_scale_of_1_6_how_stressful_was_this_for_you_1_not_at_all_stressful_6_extremely_stressful
stress_level_scale_1_to_6

on_average_how_many_cigarettes_do_did_you_usually_smoke_in_a_day_number_of_cigarettes_20_cigarettes_1_pack
avg_daily_cigarettes_smoked

paid_score
paid_score

participant_study_id
participant_study_id

places_for_bicycling_such_as_bike_paths_in_and_around_my_neighborhood_are_well_maintained_and_not_obstructed_would_you_say_that_you
bike_paths_well_maintained_near_home

provide_the_last_study_visit_stage_completed
last_study_stage_completed

since_you_speak_a_language_other_than_english_at_home_we_are_interested_in_your_own_opinion_of_how_well_you_speak_english_would_you_say_you_speak_english
self_rated_english_speaking_ability

test_upload_date
test_upload_date

the_crime_rate_in_my_neighborhood_makes_it_unsafe_to_go_on_walks_at_night_would_you_say_that_you
crime_makes_night_walks_unsafe

the_crime_rate_in_my_neighborhood_makes_it_unsafe_to_go_on_walks_during_the_day_would_you_say_that_you
crime_makes_day_walks_unsafe

the_first_statement_is_the_food_that_i_we_bought_just_didn_t_last_and_i_we_didn_t_have_money_to_get_more_was_that_often_sometimes_or_never_true_for_you_your_household_in_the_last_12_months
food_ran_out_and_had_no_money_to_get_more_in_past_12_months

the_sidewalks_in_my_neighborhood_are_well_maintained_paved_with_few_cracks_and_not_obstructed_would_you_say_that_you
sidewalks_well_maintained_near_home

there_are_facilities_to_bicycle_in_or_near_my_neighborhood_such_as_special_lanes_separate_paths_or_trails_shared_use_paths_for_cycles_and_pedestrians_would_you_say_that_you
bike_facilities_near_home 

there_are_many_four_way_intersections_in_my_neighborhood_would_you_say_that_you
many_four_way_intersections_near_home

there_are_many_interesting_things_to_look_at_while_walking_in_my_neighborhood_would_you_say_you
interesting_things_while_walking_near_home

there_are_many_places_to_go_within_easy_walking_distance_of_my_home_would_you_say_that_you
places_within_easy_walking_distance

there_are_sidewalks_on_most_of_the_streets_in_my_neighborhood_would_you_say_that_you
sidewalks_on_most_streets_near_home

there_is_so_much_traffic_on_the_streets_that_it_makes_it_difficult_or_unpleasant_to_ride_a_bicycle_in_my_neighborhood_would_you_say_that_you
traffic_makes_biking_unpleasant_near_home

there_is_so_much_traffic_on_the_streets_that_it_makes_it_difficult_or_unpleasant_to_walk_in_my_neighborhood_would_you_say_that_you
traffic_makes_walking_unpleasant_near_home

thinking_about_the_next_12_months_how_likely_do_you_think_it_is_that_you_will_lose_your_job_or_be_laid_off
job_loss_likelihood_next_12_months

tricare_or_other_military_health_care_including_va_health_care
military_or_va_health_coverage

type_i_diabetes
type_1_diabetes

was_this_a_wellness_visit_physical_or_general_purpose_check_up
was_this_a_wellness_checkup

were_either_of_your_parents_diagnosed_with_type_ii_diabetes
parent_diagnosed_with_type_2_diabetes

what_is_the_highest_grade_or_level_of_school_you_have_completed_or_the_highest_degree_you_have_received
highest_education_level_completed

what_is_the_main_type_of_housing_in_your_neighborhood
main_housing_type_in_neighborhood

what_is_your_living_situation_today
current_living_situation

what_kind_of_place_is_it_do_you_go_to_most_often_a_doctor_s_office_or_health_center_is_a_place_where_you_see_the_same_doctor_or_the_same_group_of_doctors_every_visit_where_you_usually_need_to_make_an_appointment_ahead_of_time_and_where_your_medical_records_are_on_file_urgent_care_centers_and_clinics_in_a_drug_store_or_grocery_store_are_places_where_you_do_not_need_to_make_an_appointment_ahead_of_time_and_do_not_usually_see_the_same_health_care_provider_at_each_visit
usual_source_of_medical_care_type

what_was_the_primary_reason_the_subject_discontinued
reason_subject_discontinued

what_would_you_consider_your_typical_activity_level_to_be
typical_activity_level

when_reflecting_on_your_typical_eating_habits_which_of_the_following_best_describes_your_approach_to_portion_control
eating_portion_control_approach

when_reflecting_on_your_typical_eating_habits_which_of_the_following_options_best_describes_how_often_you_consume_simple_sugars
simple_sugar_consumption_frequency

when_was_the_last_time_you_had_an_eye_exam_in_which_the_pupils_were_dilated_this_would_have_made_you_temporarily_sensitive_to_bright_light
last_dilated_eye_exam

when_was_the_last_time_you_had_your_eyes_examined_by_an_eye_care_provider_ophthalmologist_or_optometrist
last_eye_exam_by_provider

when_you_used_marijuana_approximately_how_many_days_in_a_typical_week_would_you_use_it
weekly_marijuana_use_days 

when_you_vaped_or_used_e_cigarettes_approximately_how_many_days_in_a_typical_week_would_you_use_it
weekly_vaping_use_days

which_of_the_following_options_best_describes_you_with_respect_to_physician_care_and_medications
describe_physician_care_and_medication_status

worrying_about_the_future_and_the_possibility_of_serious_complications
worry_about_future_complications

years_of_education
years_of_education

you_are_treated_with_less_courtesy_than_other_people
you_are_treated_with_less_courtesy_than_other_people

you_are_treated_with_less_respect_than_other_people
you_are_treated_with_less_respect_than_other_people

you_feel_like_a_doctor_or_nurse_is_not_listening_to_what_you_were_saying
doctor_or_nurse_are_not_listening_to_you

you_have_indicated_that_you_have_not_seen_an_eye_care_professional_in_the_past_12_months_what_is_the_main_reason_you_have_not_visited_an_eye_care_professional_in_the_past_12_months
reason_for_no_eye_care_past_twelve_months

you_receive_poorer_service_than_others
you_receive_poorer_service_than_others

think_about_the_place_you_live_do_you_have_problems_with_any_of_the_following_choose_all_that_apply
think_about_where_you_live_problems_select_all
"""
    rename_dict = parse_rename_text_block(text_block)
    pivot_df = pivot_df.rename(
        columns={k: v for k, v in rename_dict.items() if k in pivot_df.columns}
    )

    pivot_df = pivot_df.sort_values("person_id")
    out = os.path.join(output_folder, "observation.csv")
    pivot_df.to_csv(out, index=False)
    print(f"Saved {out} (shape: {pivot_df.shape})")


def write_participants(input_folder: str, output_folder: str) -> None:
    tsv_path = os.path.join(input_folder, "participants.tsv")
    df = pd.read_csv(tsv_path, sep="\t")

    bool_cols = df.select_dtypes(include="bool").columns
    for col in bool_cols:
        df[col] = (
            df[col].replace({True: "available", False: "not available"}).astype(str)
        )

    out_df = df.rename(columns={"participant_id": "person_id"}).sort_values("person_id")
    out = os.path.join(output_folder, "participants.csv")
    out_df.to_csv(out, index=False)
    print(f"Saved {out} ({len(out_df)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root-folder",
        required=True,
        help="Root folder containing dataset/; output will be written to formatted_dataset/",
    )
    ap.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome headless (recommended on servers)",
    )
    ap.add_argument(
        "--no-scrape-dictionary", action="store_true", help="Skip selenium scrape step"
    )
    ap.add_argument(
        "--dictionary-csv",
        default=None,
        help="Use an existing omop_dictionary.csv instead of scraping",
    )
    args = ap.parse_args()

    root_folder = args.root_folder
    input_folder = os.path.join(root_folder, "dataset")
    output_folder = os.path.join(root_folder, "formatted_dataset")

    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Expected input folder not found: {input_folder}")

    ensure_dir(output_folder)

    # Dictionary
    if args.dictionary_csv:
        dic_path = args.dictionary_csv
    elif args.no_scrape_dictionary:
        dic_path = os.path.join(input_folder, "omop_dictionary.csv")
        if not os.path.exists(dic_path):
            raise FileNotFoundError(
                f"--no-scrape-dictionary set but {dic_path} not found. Provide --dictionary-csv or scrape."
            )
    else:
        dic_path = scrape_dictionary_to_csv(
            input_folder, headless=True if args.headless else True
        )

    dic_df = pd.read_csv(dic_path)
    dic_df.columns = [clean_var_name(c) for c in dic_df.columns]
    dic_df = dic_df.apply(lambda col: col.str.lower() if col.dtype == "object" else col)

    # Inputs
    measurement_df, observation_df, condition_df, person_df = load_inputs(input_folder)

    # person
    write_person(person_df, output_folder)

    # condition + remaining observation split
    matching_observations, observation_remaining = split_observation_for_condition(
        observation_df, condition_df
    )

    # condition_occurrence output
    write_condition_occurrence(
        matching_observations=matching_observations,
        dic_df=dic_df,
        condition_df=condition_df,
        person_df=person_df,
        output_folder=output_folder,
    )

    # measurement output
    write_measurement(measurement_df, output_folder)

    # observation output (from remaining)
    write_observation(observation_remaining, dic_df, output_folder)

    # participants output
    write_participants(input_folder, output_folder)

    print("\nDone.")


if __name__ == "__main__":
    main()

#  python convert_aireadi.py --root-folder /home/nayoonkim/LATCH_Diabetes/data/aireadi_year3_test
