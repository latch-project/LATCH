import pandas as pd
import warnings
from rpy2.robjects import r, globalenv
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro


def description(analysis, df, id_column):
    analysis_lower = analysis.lower()
    if any(
        key in analysis_lower
        for key in ["logistic", "linear", "prevalence", "comparison"]
    ):
        outcome = [df.columns[-1]]
        outcome_roles = {df.columns[-1]: "outcome"}
    elif "mediation" in analysis_lower:
        outcome = list(df.columns[-3:])
        outcome_roles = {
            df.columns[-3]: "independent",
            df.columns[-2]: "mediator",
            df.columns[-1]: "outcome",
        }
    elif "cox" in analysis_lower or "survival" in analysis_lower:
        outcome = list(df.columns[-2:])
        last_two_cols = df.columns[-2:]
        allowed_values = {None, 0.0, 1.0, 0, 1}

        def is_outcome_col(series):
            unique_vals = set(series.dropna().astype(float).unique())
            return unique_vals.issubset(allowed_values)

        if is_outcome_col(df[last_two_cols[-1]]):
            outcome_roles = {
                last_two_cols[-2]: "event_to_time",
                last_two_cols[-1]: "outcome",
            }
        elif is_outcome_col(df[last_two_cols[-2]]):
            outcome_roles = {
                last_two_cols[-2]: "outcome",
                last_two_cols[-1]: "event_to_time",
            }

    else:
        outcome = []
        outcome_roles = {}

    if "weighted" in analysis_lower:
        survey_weight_var = "survey_weight"
        psu_var = "masked_variance_pseudo_psu"
        stratum_var = "masked_variance_pseudo_stratum"
        in_analysis_var = "in_analysis"
    else:
        survey_weight_var = psu_var = stratum_var = in_analysis_var = None

    outcome_r = ",".join([f'"{col}"' for col in outcome])
    weights = [
        w for w in [survey_weight_var, psu_var, stratum_var, in_analysis_var] if w
    ]
    weights_r = ",".join([f'"{w}"' for w in weights])
    has_weights = bool(weights)
    has_mediator = "mediator" in outcome_roles.values()
    has_event_to_time = "event_to_time" in outcome_roles.values()

    custom_roles_r = ";".join(
        [f'outcome_roles["{col}"] <- "{role}"' for col, role in outcome_roles.items()]
    )

    weight_post_summary_r = (
        (
            'weight_vars <- report$variable[report$category == "weight"]; '
            'cat("Weight Variables: "); print(weight_vars); '
            'psu_var <- weight_vars[grepl("psu", weight_vars, ignore.case = TRUE)][1]; '
            'cat("PSU:", psu_var); '
            'stratum_var <- weight_vars[grepl("stratum", weight_vars, ignore.case = TRUE)][1]; '
            'cat("Stratum:", stratum_var); '
            'weight_var <- weight_vars[grepl("weight", weight_vars, ignore.case = TRUE)][1]; '
            'cat("Weight:", weight_var); '
            'in_analysis_var <- weight_vars[grepl("in_analysis", weight_vars, ignore.case = TRUE)][1]; '
            'cat("In Analysis:", in_analysis_var)'
        )
        if has_weights
        else ""
    )

    weight_vars_r = f"weight_vars <- c({weights_r})\n" if has_weights else ""

    weight_cohort_r = (
        'cohort <- df[df$in_analysis == 1, names(df) != "in_analysis"]\n'
        if has_weights
        else "cohort <- df\n"
    )
    weight_block_r = (
        """

    } else if (name %in% weight_vars) {
        category <- "weight"
        summary_info <- "Weight variable" 
    """
        if has_weights
        else ""
    )

    mediator_block_r = (
        'mediator_var <- names(outcome_roles[outcome_roles == "mediator"])[1]\n'
        'cat("Mediator Variable:\\n"); print(mediator_var); cat("\\n")\n'
        'independent_var <- names(outcome_roles[outcome_roles == "independent"])[1]\n'
        'cat("Independent Variable:\\n"); print(independent_var); cat("\\n")'
        if has_mediator
        else ""
    )

    event_to_time_block_r = (
        'event_to_time_var <- names(outcome_roles[outcome_roles == "event_to_time"])[1]\ncat("Event-to-Time Variable:\\n"); print(event_to_time_var); cat("\\n")'
        if has_event_to_time
        else ""
    )

    description_r = f"""
    suppressPackageStartupMessages(library(dplyr))
    suppressPackageStartupMessages(library(broom))
    suppressPackageStartupMessages(library(tibble))

    identifier_vars <- c("{id_column}")
    outcome_vars <- c({outcome_r})
    {weight_vars_r}
    {weight_cohort_r}

    outcome_roles <- c()
    {custom_roles_r}


    summarize_variable <- function(column, name) {{
    n_unique <- length(unique(na.omit(column)))
    na_count <- sum(is.na(column))

    if (name %in% identifier_vars) {{
        category <- "identifier"
        summary_info <- paste0("Total rows = ", nrow(cohort))

    }} else if (name %in% outcome_vars) {{
        # Assign its special role (e.g., "outcome", "mediator")
        category <- ifelse(!is.na(outcome_roles[name]), outcome_roles[name], "outcome")

        # Generate a summary based on its underlying data type
        underlying_type <- case_when(
        n_unique == 2                                 ~ "binary",
        is.numeric(column) & n_unique > 2             ~ "numerical",
        is.character(column) | is.factor(column)      ~ "categorical",
        TRUE                                          ~ "other"
        )

        if (underlying_type == "numerical") {{
        mean_val <- round(mean(column, na.rm = TRUE), 3)
        sd_val   <- round(sd(column, na.rm = TRUE), 3)
        summary_info <- paste0("mean = ", mean_val, ", sd = ", sd_val)
        }} else if (underlying_type %in% c("categorical", "binary")) {{
        tbl <- prop.table(table(column)) * 100
        tbl <- round(tbl, 1)
        summary_info <- paste0(names(tbl), ": ", tbl, "%", collapse = "; ")
        }} else {{
        summary_info <- NA
        }}

    {weight_block_r}

    }} else {{
        # This block handles regular predictors
        category <- case_when(
        n_unique == 2                                 ~ "binary",
        is.numeric(column) & n_unique > 2             ~ "numerical",
        is.character(column) | is.factor(column)      ~ "categorical",
        TRUE                                          ~ "other"
        )

        if (category == "numerical") {{
        mean_val <- round(mean(column, na.rm = TRUE), 3)
        sd_val   <- round(sd(column, na.rm = TRUE), 3)
        summary_info <- paste0("mean = ", mean_val, ", sd = ", sd_val)
        }} else if (category %in% c("categorical", "binary")) {{
        tbl <- prop.table(table(column)) * 100
        tbl <- round(tbl, 1)
        summary_info <- paste0(names(tbl), ": ", tbl, "%", collapse = "; ")
        }} else {{
        summary_info <- NA
        }}
    }}

    data.frame(
        variable   = name,
        category   = category,
        n_unique   = n_unique,
        na_count   = na_count,
        summary    = summary_info,
        stringsAsFactors = FALSE
    )
    }}

    report <- bind_rows(
    lapply(names(cohort), function(col_name) {{
        summarize_variable(cohort[[col_name]], col_name)
    }})
    )

    identifier_vars  <- report$variable[report$category == "identifier"]
    cat("Identifier Variables:\\n");   print(identifier_vars);   cat("\\n")

    {weight_post_summary_r}

    binary_vars      <- report$variable[report$category == "binary"]
    cat("Binary Variables:\\n");       print(binary_vars);       cat("\\n")
    print(binary_vars)

    categorical_vars <- report$variable[report$category == "categorical"]
    cat("Categorical Variables:\\n");  print(categorical_vars);  cat("\\n")
    print(categorical_vars)

    numerical_vars   <- report$variable[report$category == "numerical"]
    cat("Numerical Variables:\\n");    print(numerical_vars);    cat("\\n")
    print(numerical_vars)

    {mediator_block_r}
    {event_to_time_block_r}

    outcome_var     <- report$variable[report$category %in% c("outcome")]
    cat("Outcome Variables:\\n");      print(outcome_var);      cat("\\n")
    """
    return description_r


def run_stat(analysis_type):
    regression_factoring_code = """
    # Identify predictors and factor candidates
    predictor_vars <- report$variable[report$category %in% c("categorical", "binary", "numerical")]
    factor_candidates <- report$variable[report$category %in% c("categorical", "binary")]

    # Convert binary/categorical variables to factor if not already
    for (var in factor_candidates) {
    if (!is.factor(df[[var]])) {
        df[[var]] <- as.factor(df[[var]])
    }
    }

    # Initialize reference_levels table
    reference_levels <- tibble(variable = character(), reference_level = character())

    # Clean, trim, and set reference levels for all factor variables
    for (col in factor_candidates) {
    df[[col]] <- factor(trimws(as.character(df[[col]])))
    levels_vec <- levels(df[[col]])

    # Try to find preferred reference
    preferred_order <- c("healthy", "none", "control", "reference", "ref", "normal","Q1", "low", "0", "1")
    matches <- tolower(levels_vec)  # lower case to standardize
    ref_level <- NA  # default

    for (keyword in preferred_order) {
    idx <- which(grepl(keyword, matches, ignore.case = TRUE))
    if (length(idx) > 0) {
        ref_level <- levels_vec[idx[1]]  # pick the first match for that keyword
        break  # stop at the highest-priority match
    }
    }


    # If none found, fall back to most common level
    if (is.na(ref_level)) {
        level_counts <- table(df[[col]])
        ref_level <- names(level_counts)[which.max(level_counts)]
    }

    # Set reference level
    df[[col]] <- relevel(df[[col]], ref = ref_level)

    # Record reference level
    reference_levels <- bind_rows(
        reference_levels,
        tibble(variable = col, reference_level = ref_level)
    )
    }
    """

    if "weighted" in analysis_type.lower() and "regression" in analysis_type.lower():
        factoring_code = f"""
    {regression_factoring_code}
        """

        package = """
    library(survey)
    options(survey.lonely.psu = "adjust")
        """

        design = """
    survey_design <- svydesign(
        ids     = as.formula(paste0("~", psu_var)),
        strata  = as.formula(paste0("~", stratum_var)),
        weights = as.formula(paste0("~", weight_var)),
        data    = df,
        nest    = TRUE
        )
    survey_design <- subset(survey_design, in_analysis ==1)
        """

        if (
            "logistic" in analysis_type.lower()
            and "stratified" not in analysis_type.lower()
        ):
            model = """
    model <- svyglm(formula,design = survey_design, family = quasibinomial()) 
            """

            formula = """
    x_raw <- df[[outcome_var]]
    x_chr <- trimws(tolower(as.character(x_raw)))

    none_tokens <- c("none", "nan", "na", "", "null", "nil", "missing")
    x_chr[x_chr %in% none_tokens] <- NA_character_
    y <- rep(NA_integer_, length(x_chr))
    y[x_chr %in% c("yes", "y", "true", "t")]  <- 1L
    y[x_chr %in% c("no",  "n", "false", "f")] <- 0L
    x_num <- suppressWarnings(as.numeric(x_chr))
    y[is.na(y) & !is.na(x_num) & x_num == 1] <- 1L
    y[is.na(y) & !is.na(x_num) & x_num == 0] <- 0L
    idx <- is.na(y) & !is.na(x_chr)
    if (any(idx)) {
    vals <- sort(unique(x_chr[idx]))
    if (length(vals) != 2) {
        stop(sprintf(
        "Outcome '%s' must have exactly 2 non-missing classes after excluding none. Found: %s",
        outcome_var, paste(vals, collapse = ", ")
        ))
    }
    tab <- table(x_chr[idx])
    minority <- names(tab)[which.min(tab)]
    majority <- setdiff(vals, minority)
    cat(sprintf(
        "Outcome '%s' recoding: 1 = %s (minority)  0 = %s (majority)",
        outcome_var, minority, majority
    ))
    y[idx] <- as.integer(x_chr[idx] == minority)
    }
    df[[outcome_var]] <- y
    u <- sort(unique(df[[outcome_var]][!is.na(df[[outcome_var]])]))
    if (!(length(u) == 2 && all(u == c(0, 1)))) {
    stop(sprintf(
        "After recoding, '%s' must contain both 0 and 1 (plus NA for none). Found: %s",
        outcome_var,
        ifelse(length(u) == 0, "<no non-missing values>", paste(u, collapse = ", "))
    ))
    }
    formula <- as.formula(paste0(outcome_var, " ~ ", paste(predictor_vars, collapse = " + ")))
            """

            result_table = """
    result_table <- tidy(model, conf.int = TRUE, exponentiate = TRUE) %>%
            select(term, estimate, p.value, conf.low, conf.high)
            """

        elif "linear" in analysis_type.lower():
            model = """
            model <- svyglm(formula,
    design = survey_design,
    family = gaussian()) 
            """
            formula = """
    formula <- as.formula(paste0(outcome_var, " ~ ", paste(predictor_vars, collapse = " + ")))

            """

            result_table = """
    result_table <- tidy(model, conf.int = TRUE) %>%
            select(term, estimate, p.value, conf.low, conf.high)
            """

        elif "cox" in analysis_type.lower():
            model = """
    model <- svycoxph(formula, design = survey_design)
            """
            formula = """
    if (!is.numeric(df[[outcome_var]])) {
        df[[outcome_var]] <- as.numeric(df[[outcome_var]])
    }

    if (!is.numeric(df[[event_to_time_var]])) {
        df[[event_to_time_var]] <- as.numeric(df[[event_to_time_var]])
    }
    formula <- as.formula(paste0("Surv(", event_to_time_var, ", ", outcome_var, ") ~ ", paste(predictor_vars, collapse = " + ")))
            """

            result_table = """
    result_table <- tidy(model, conf.int = TRUE, exponentiate = TRUE) %>%
            select(term, estimate, p.value, conf.low, conf.high)
            """

        elif "stratified" in analysis_type.lower():
            factoring_code = f"""
    {regression_factoring_code}

    # --- Stratification Variables ---
    # --- Ensure stratification variables are factors ---
    stratification_vars <- factor_candidates
    for (s_var in stratification_vars) {{
    if (!is.factor(df[[s_var]])) {{
        df[[s_var]] <- factor(trimws(as.character(df[[s_var]])))
    }}
    }}
            """

            model = """
    all_stratified_results <- list()

    for (strat_var in stratification_vars) {{
    current_predictors <- setdiff(predictor_vars, strat_var)
    if (length(current_predictors) == 0) next

    .formula <- as.formula(paste0(outcome_var, " ~ ", paste(current_predictors, collapse = " + ")))
    strat_levels <- levels(droplevels(df[[strat_var]]))  # drop unused

    for (level in strat_levels) {{
        cat(sprintf("Fitting survey model for %s = %s", strat_var, level))

        # Data sufficiency checks (aligned to in_analysis == 1)
        idx <- df$in_analysis == 1 & df[[strat_var]] == level
        n_sub <- sum(idx, na.rm = TRUE)
        y_vals <- df[[outcome_var]][idx]
        outcome_has_variation <- length(unique(na.omit(y_vals))) > 1

        if (n_sub > 10 && outcome_has_variation) {{

        sub_design <- subset(survey_design, get(strat_var) == level)

        fit_try <- try(svyglm(.formula, design = sub_design, family = quasibinomial()), silent = TRUE)
        if (inherits(fit_try, "try-error")) {{
            cat(sprintf("Could not fit model for %s = %s: %s",
                        strat_var, level, conditionMessage(attr(fit_try, "condition"))))
            next
        }}

        results_df_level <- broom::tidy(fit_try, conf.int = TRUE, exponentiate = TRUE) %>%
            mutate(stratification_variable = strat_var, stratum = level)

        all_stratified_results[[paste(strat_var, level, sep = "_")]] <- results_df_level
        }} else {{
        cat(sprintf("Skipping %s = %s due to insufficient data or single outcome class.",
                    strat_var, level))
        }}
    }}
    }}
            """

            formula = """
    df[[outcome_var]] <- ifelse(tolower(df[[outcome_var]]) == "yes", 1,
                        ifelse(tolower(df[[outcome_var]]) == "no", 0,
                        ifelse(grepl("1", as.character(df[[outcome_var]])), 1,
                        ifelse(grepl("0", as.character(df[[outcome_var]])), 0,
                                as.numeric(df[[outcome_var]])))))
            """

            result_table = """
    result_table <- bind_rows(all_stratified_results) %>%
    dplyr::select(stratification_variable, stratum, term, estimate, p.value, conf.low, conf.high, dplyr::everything())
            """

    elif "regression" in analysis_type.lower():
        factoring_code = f"""
    {regression_factoring_code}
        """
        package = """
        """

        design = """
        """

        if (
            "logistic" in analysis_type.lower()
            and "stratified" not in analysis_type.lower()
        ):
            model = """
    model <- glm(formula,
                data = df,
                family =  binomial(link = "logit"))
            """

            formula = """
    x_raw <- df[[outcome_var]]
    x_chr <- trimws(tolower(as.character(x_raw)))

    none_tokens <- c("none", "nan", "na", "", "null", "nil", "missing")
    x_chr[x_chr %in% none_tokens] <- NA_character_

    y <- rep(NA_integer_, length(x_chr))

    y[x_chr %in% c("yes", "y", "true", "t")]  <- 1L
    y[x_chr %in% c("no",  "n", "false", "f")] <- 0L

    x_num <- suppressWarnings(as.numeric(x_chr))
    y[is.na(y) & !is.na(x_num) & x_num == 1] <- 1L
    y[is.na(y) & !is.na(x_num) & x_num == 0] <- 0L

    idx <- is.na(y) & !is.na(x_chr)
    if (any(idx)) {
    vals <- sort(unique(x_chr[idx]))

    if (length(vals) != 2) {
        stop(sprintf(
        "Outcome '%s' must have exactly 2 non-missing classes after excluding none. Found: %s",
        outcome_var, paste(vals, collapse = ", ")
        ))
    }

    tab <- table(x_chr[idx])
    minority <- names(tab)[which.min(tab)]
    majority <- setdiff(vals, minority)

    cat(sprintf(
        "Outcome '%s' recoding: 1 = %s (minority)  0 = %s (majority)",
        outcome_var, minority, majority
    ))

    y[idx] <- as.integer(x_chr[idx] == minority)
    }

    df[[outcome_var]] <- y

    # Must contain both 0 and 1 somewhere (plus NA allowed)
    u <- sort(unique(df[[outcome_var]][!is.na(df[[outcome_var]])]))
    if (!(length(u) == 2 && all(u == c(0, 1)))) {
    stop(sprintf(
        "After recoding, '%s' must contain both 0 and 1 (plus NA for none). Found: %s",
        outcome_var,
        ifelse(length(u) == 0, "<no non-missing values>", paste(u, collapse = ", "))
    ))
    }

    formula <- as.formula(paste0(outcome_var, " ~ ", paste(predictor_vars, collapse = " + ")))
                """

            result_table = """
    result_table <- tidy(model, conf.int = TRUE, exponentiate = TRUE) %>%
        select(term, estimate, p.value, conf.low, conf.high)

            """

        elif "linear" in analysis_type.lower():
            model = """
    model <- lm(formula, data = df)

            """
            formula = """
    formula <- as.formula(paste0(outcome_var, " ~ ", paste(predictor_vars, collapse = " + ")))
            """

            result_table = """
    result_table <- tidy(model, conf.int = TRUE) %>%
            select(term, estimate, p.value, conf.low, conf.high)

            """

        elif "cox" in analysis_type.lower():
            model = """
    library(survival)
    model <- coxph(formula, data = df)
            """
            formula = """
    if (!is.numeric(df[[outcome_var]])) {
        df[[outcome_var]] <- as.numeric(df[[outcome_var]])
    }

    if (!is.numeric(df[[event_to_time_var]])) {
        df[[event_to_time_var]] <- as.numeric(df[[event_to_time_var]])
    }
    formula <- as.formula(paste0("Surv(", event_to_time_var, ", ", outcome_var, ") ~ ", paste(predictor_vars, collapse = " + ")))
            """

            result_table = """
    result_table <- tidy(model, conf.int = TRUE, exponentiate = TRUE) %>%
            select(term, estimate, p.value, conf.low, conf.high)
            """
        elif "stratified" in analysis_type.lower():
            factoring_code = f"""
    {regression_factoring_code}

    # --- Stratification Variables ---
    # All categorical and binary variables are identified as candidates for stratification.
    # This list is created by the regression_factoring_code block.
    stratification_vars <- factor_candidates

    # Ensure all stratification variables are converted to factors to properly group the data.
    for (s_var in stratification_vars) {{
        if (!is.factor(df[[s_var]])) {{
            df[[s_var]] <- factor(trimws(as.character(df[[s_var]])))
        }}
    }}
            """
            package = """
    library(dplyr)
    library(broom)
    library(tidyr)
            """

            design = """
            """
            formula = """
            """
            model = """
    # Initialize a list to hold all the resulting dataframes from each successful model fit.
    all_stratified_results <- list()

    # --- Stratification Loop ---
    for (strat_var in stratification_vars) {
    
    # Exclude the current stratification variable from the list of predictors
    # to avoid using it as both a predictor and a stratifier in the same model.
    current_predictors <- predictor_vars[!predictor_vars %in% strat_var]
    
    # If there are no predictors left after removing the stratifier, skip to the next variable.
    if (length(current_predictors) == 0) {
        next
    }
    
    # Create the model formula dynamically for the current set of predictors.
    df[[outcome_var]] <- ifelse(tolower(df[[outcome_var]]) == "yes", 1,
                ifelse(tolower(df[[outcome_var]]) == "no", 0,
                        as.numeric(df[[outcome_var]])))

    .formula <- as.formula(paste0(outcome_var, " ~ ", paste(current_predictors, collapse = " + ")))
    
    # Get the levels of the current stratification variable (e.g., 'Male', 'Female').
    strat_levels <- levels(df[[strat_var]])
    
    # --- Stratum Loop ---
    # Loop over each level (stratum) of the stratification variable.
    for (level in strat_levels) {
        
        cat(paste0("\\nFitting model for ", strat_var, " = ", level, "\\n"))
        
        # Use tryCatch to handle potential errors (e.g., from perfect separation)
        # in model fitting for a given stratum without stopping the entire script.
        tryCatch({
        
        # Create a subset of the data for the current level.
        subset_df <- filter(df, .data[[strat_var]] == level)
        
        # Check for sufficient data (>10 rows) and variance in the outcome (at least 2 unique values).
        if(nrow(subset_df) > 10 && length(unique(subset_df[[outcome_var]])) > 1) {
            
            # Fit the logistic regression model on the subset.
            model_level <- glm(.formula, data = subset_df, family = binomial(link = "logit"))
            
            # Use broom::tidy to get a clean dataframe of model results.
            # Add columns to identify the stratification variable and the specific stratum (level).
            results_df_level <- tidy(model_level, conf.int = TRUE, exponentiate = TRUE) %>%
            mutate(
                stratification_variable = strat_var,
                stratum = level
            )
            
            # Append the results dataframe to the main list, creating a unique name for the list element.
            all_stratified_results[[paste(strat_var, level, sep = "_")]] <- results_df_level
            
        } else {
            cat(paste0("Skipping ", strat_var, " = ", level, " due to insufficient data or single outcome class.\\n"))
        }
        
        }, error = function(e) {
        # If an error occurs, print a message and continue to the next level.
        cat(paste0("Could not fit model for ", strat_var, " = ", level, ": ", e$message, "\\n"))
        })
    }
    }
            """
            result_table = """
    # bind_rows combines all the dataframes in the list into a single, comprehensive table.
    result_table <- bind_rows(all_stratified_results) %>%
        # Reorder columns for clarity, bringing stratification info to the front.
        select(stratification_variable, stratum, term, estimate, p.value, conf.low, conf.high, everything())
            """

    elif "weighted" in analysis_type.lower() and "prevalence" in analysis_type.lower():
        factoring_code = """
    group_vars_list <- report$variable[report$category %in% c("categorical", "binary")]
    
    # Loop through the variables and ensure they are clean factors in the 'df' dataframe.
    for (var in group_vars_list) {
    if (var %in% names(df)) {
        df[[var]] <- factor(trimws(as.character(df[[var]])))
    }
    }
        """

        package = """
    library(survey)
    options(survey.lonely.psu = "adjust")
        """

        design = """
    survey_design <- svydesign(
        ids     = as.formula(paste0("~", psu_var)),
        strata  = as.formula(paste0("~", stratum_var)),
        weights = as.formula(paste0("~", weight_var)),
        data    = df,
        nest    = TRUE
        )
    survey_design <- subset(survey_design, in_analysis ==1)
        """
        formula = """
    df[[outcome_var]] <- ifelse(tolower(df[[outcome_var]]) == "yes", 1,
                    ifelse(tolower(df[[outcome_var]]) == "no", 0,
                    ifelse(grepl("1", as.character(df[[outcome_var]])), 1,
                    ifelse(grepl("0", as.character(df[[outcome_var]])), 0,
                            as.numeric(df[[outcome_var]])))))


    varformula <- as.formula(paste0("~", outcome_var))
        """

        model = f"""
    # Calculate Overall Prevalence.
    total_prev <- svymean(varformula, survey_design, na.rm = TRUE)
    total_conf <- confint(total_prev)

    # Initialize a list to store pairwise results
    pairwise_results <- list()

    # Loop through each grouping variable
    all_strat_results <- lapply(group_vars_list, function(current_group_var) {{

        byformula <- as.formula(paste0("~", current_group_var))
        test_formula <- as.formula(paste0(outcome_var, " ~ ", current_group_var))

        # Prevalence and confidence intervals
        strat_prev <- svyby(varformula, byformula, survey_design, svymean, na.rm = TRUE)
        strat_conf <- confint(strat_prev)

        strat_result <- as_tibble(strat_prev) %>%
            cbind(strat_conf) %>%
            rename(
                Group = 1,
                prevalence = 2,
                conf_low = `2.5 %`,
                conf_high = `97.5 %`
            ) %>%
            mutate(Variable = current_group_var, .before = 1)

        # --- Global P-value ---
        group_levels <- levels(factor(df[[current_group_var]]))
        num_levels <- length(group_levels)
        global_p_value <- NA_real_

        test_result <- NULL
        test_p <- NA_real_

        if (num_levels == 2) {{
            test_result <- tryCatch(
                svyttest(test_formula, survey_design),
                error = function(e) NULL
            )
        }} else if (num_levels > 2) {{
            chisq_formula <- as.formula(paste0("~", outcome_var, " + ", current_group_var))
            test_result <- tryCatch(
                svychisq(chisq_formula, survey_design),
                error = function(e) NULL
            )
        }}

        if (!is.null(test_result)) {{
            test_p <- tryCatch(test_result$p.value, error = function(e) NA_real_)
        }}
        global_p_value <- test_p

        # Add global p-value only to the first row
        strat_result$`P-value` <- ""
        strat_result$`P-value`[1] <- if (!is.na(global_p_value)) round(global_p_value, 4) else NA_character_

        # Keep only the columns needed in the final result table
        strat_result <- strat_result %>%
            dplyr::select(Variable, Group, prevalence, conf_low, conf_high, `P-value`)

        # --- Pairwise p-values table (kept as before) ---
        pairwise_df <- tibble(
            Variable = character(),
            Comparison = character(),
            `P-value` = numeric()
        )

        if (num_levels > 2) {{
            all_pairs <- combn(group_levels, 2, simplify = FALSE)
            for (pair in all_pairs) {{
                pair_name <- paste(pair[1], "vs", pair[2], sep = "_")
                pair_design <- subset(survey_design, get(current_group_var) %in% pair)
                test_result <- try(svyttest(test_formula, pair_design), silent = TRUE)
                if (!inherits(test_result, "try-error")) {{
                    pairwise_df <- bind_rows(pairwise_df, tibble(
                        Variable = current_group_var,
                        Comparison = pair_name,
                        `P-value` = round(test_result$p.value, 4)
                    ))
                }}
            }}
        }}

        # Store in global list
        pairwise_results[[current_group_var]] <<- pairwise_df

        return(strat_result)
    }})
"""

        result_table = """
    # Combine into a final result table
    total_result_df <- tibble(
        Variable = "Overall",
        Group = "Overall",
        prevalence = as.numeric(coef(total_prev)),
        conf_low = as.numeric(total_conf[1]),
        conf_high = as.numeric(total_conf[2]),
        `P-value` = ""
    )

    combined_strat_df <- bind_rows(all_strat_results)
    result_table <- bind_rows(total_result_df, combined_strat_df) %>%
        dplyr::select(Variable, Group, prevalence, conf_low, conf_high, `P-value`)

    # Combine pairwise p-values into one data frame (unchanged)
    pairwise_pvalue_table <- bind_rows(pairwise_results)
    """

    elif (
        "weighted" in analysis_type.lower()
        and "group" in analysis_type.lower()
        and "group comparison" in analysis_type.lower()
    ):
        package = """
    library(survey)
    library(dplyr)  
    options(survey.lonely.psu = "adjust")
        """

        factoring_code = """
    # Outcome is the grouping variable
    stopifnot(outcome_var %in% names(df))
    df[[outcome_var]] <- factor(trimws(as.character(df[[outcome_var]])))

    # Identify numeric predictors (metrics)
    if (exists('numerical_vars')) {
    metrics_list <- intersect(numerical_vars, names(df))
    } else {
    metrics_list <- names(df)[vapply(df, is.numeric, logical(1))]
    }

    # Drop non-metrics / design columns
    drop_cols <- c(psu_var, stratum_var, weight_var, 'in_analysis', outcome_var, 'id', 'person_id')
    metrics_list <- setdiff(metrics_list, drop_cols)
        """

        formula = """
    groupformula <- as.formula(paste0('~', outcome_var))
        """

        design = """
    survey_design <- svydesign(
    ids     = as.formula(paste0('~', psu_var)),
    strata  = as.formula(paste0('~', stratum_var)),
    weights = as.formula(paste0('~', weight_var)),
    data    = df,
    nest    = TRUE
    )
    survey_design <- subset(survey_design, in_analysis == 1)
        """

        model = """
    all_results <- lapply(metrics_list, function(metric_var) {

    # Skip invalids
    if (!nzchar(metric_var) || !(metric_var %in% names(df)) || !is.numeric(df[[metric_var]])) return(NULL)

    varformula <- as.formula(paste0('~', metric_var))

    # Weighted means by outcome group
    group_means <- svyby(varformula, groupformula, survey_design, svymean, na.rm = TRUE)
    group_conf  <- confint(group_means)

    # Global p-value per metric
    num_levels <- nlevels(droplevels(df[[outcome_var]]))
    p_value <- NA_real_

    if (num_levels == 2) {
        test_formula <- as.formula(paste0(metric_var, ' ~ ', outcome_var))
        ttest_result <- try(svyttest(test_formula, design = survey_design), silent = TRUE)
        if (!inherits(ttest_result, 'try-error')) p_value <- as.numeric(ttest_result$p.value)
    } else if (num_levels > 2) {
        model_formula <- as.formula(paste0(metric_var, ' ~ ', outcome_var))
        fit <- try(svyglm(model_formula, design = survey_design, na.action = na.omit), silent = TRUE)
        if (!inherits(fit, 'try-error')) {
        regtest <- try(regTermTest(fit, test.terms = outcome_var, method = 'Wald'), silent = TRUE)
        if (!inherits(regtest, 'try-error')) p_value <- as.numeric(regtest$p)
        }
    }

    # Tidy per-metric table
    result_table <- suppressMessages(as_tibble(group_means)) %>%
        cbind(group_conf) %>%
        rename(
        Group     = 1,
        mean      = 2,
        conf_low  = `2.5 %`,
        conf_high = `97.5 %`
        ) %>%
        mutate(
        Variable = metric_var,
        `P-value` = '',
        .before = 1
        )

    result_table$`P-value`[1] <- round(p_value, 4)
    return(result_table)
    })
        """

        result_table = """
    all_results <- Filter(Negate(is.null), all_results)
    result_table <- dplyr::bind_rows(all_results)
    result_table <- result_table %>% mutate(across(where(is.numeric), ~ round(., 4)))
        """

    elif analysis_type == "weighted_numerical_comparison":
        package = """
    # --- Load packages ---
    library(survey)
    library(dplyr)  
    options(survey.lonely.psu = "adjust")
        """

        factoring_code = """
    # --- Clean group variable ---
    group_vars_list <- report$variable[report$category %in% c("categorical", "binary")]

    # Loop through the variables and ensure they are clean factors in the 'df' dataframe.
    for (var in group_vars_list) {
    if (var %in% names(df)) {
        df[[var]] <- factor(trimws(as.character(df[[var]])))
    }
    }
        """
        formula = """
    # --- Define formula and survey design ---
    varformula <- as.formula(paste0("~", outcome_var))
        """

        design = """
    survey_design <- svydesign(
    ids     = as.formula(paste0("~", psu_var)),
    strata  = as.formula(paste0("~", stratum_var)),
    weights = as.formula(paste0("~", weight_var)),
    data    = df,
    nest    = TRUE
    )
    survey_design <- subset(survey_design, in_analysis ==1)
        """

        model = """
    all_results <- lapply(group_vars_list, function(group_var) {
    
    # Ensure valid variable
    if (!nzchar(group_var) || !(group_var %in% names(df))) return(NULL)
    
    groupformula <- as.formula(paste0("~", group_var))
    
    # Mean outcome by group
    group_means <- svyby(varformula, groupformula, survey_design, svymean, na.rm = TRUE)
    group_conf <- confint(group_means)
    
    # Number of levels
    num_levels <- length(levels(df[[group_var]]))
    p_value <- NA_real_
    
    # Select appropriate test
    if (num_levels == 2) {
        test_formula <- as.formula(paste0(outcome_var, " ~ ", group_var))
        ttest_result <- try(svyttest(test_formula, design = survey_design), silent = TRUE)
        if (!inherits(ttest_result, "try-error")) {
        p_value <- ttest_result$p.value
        }
    } else if (num_levels > 2) {
        model_formula <- as.formula(paste0(outcome_var, " ~ ", group_var))
        model <- svyglm(model_formula, design = survey_design)
        regtest <- try(regTermTest(model, test.terms = as.formula(paste0("~", group_var)), method = "LRT"), silent = TRUE)
        if (!inherits(regtest, "try-error")) {
        p_value <- regtest$p
        }
    }
    result_table <- as_tibble(group_means) %>%
    cbind(group_conf) %>%
    rename(
    Group = 1,
    mean = 2,
    conf_low = `2.5 %`,
    conf_high = `97.5 %`
    ) %>%
    mutate(
    Variable = group_var,
    `P-value` = "",
    .before = 1
    )

result_table$`P-value`[1] <- round(p_value, 4)

return(result_table)
})
        """
        result_table = """
    result_table <- bind_rows(all_results)
        """

    elif analysis_type == "group_comparison":
        factoring_code = f"""

    group_col_name <- outcome_var

    vars_to_factor <- c(categorical_vars, binary_vars, group_col_name)
    for (col in vars_to_factor) {{
        if (col %in% names(df) && !is.factor(df[[col]])) {{
        df[[col]] <- factor(trimws(as.character(df[[col]])))
        }}
    }}
        """
        package = """
        library(dplyr)
        library(tidyr)
        library(broom)
        library(purrr)
        """

        design = """
        """
        formula = """
        """
        model = """
    # --- NUMERIC COMPARISON ---
    # This uses the 'numerical_vars' list, which is expected to be in the R environment.
    numeric_results <- map_dfr(numerical_vars, function(col) {
        
        # Formula for the test (ANOVA or t-test)
        test_formula <- as.formula(paste0("`", col, "` ~ `", group_col_name, "`"))
        
        # Calculate summary statistics (n, mean, sd, ci) for each group
        summary_stats <- df %>%
        filter(!is.na(.data[[col]]) & !is.na(.data[[group_col_name]])) %>%
        group_by(.data[[group_col_name]]) %>%
        summarise(
            n = n(),
            mean = mean(.data[[col]], na.rm = TRUE),
            sd = sd(.data[[col]], na.rm = TRUE),
            .groups = 'drop'
        ) %>%
        mutate(
            se = sd / sqrt(n),
            ci_lower = mean - qt(0.975, df = n - 1) * se,
            ci_upper = mean + qt(0.975, df = n - 1) * se,
            # Format the output string
            summary_str = sprintf("%.2f (%.2f–%.2f)", mean, ci_lower, ci_upper)
        ) %>%
        select(-n, -mean, -sd, -se, -ci_lower, -ci_upper) %>%
        pivot_wider(names_from = all_of(group_col_name), values_from = summary_str)

        # Perform statistical test
        p_value <- tryCatch({
        if (length(unique(df[[group_col_name]])) > 2) {
            # ANOVA for more than 2 groups
            tidy(aov(test_formula, data = df))$p.value[1]
        } else {
            # T-test for 2 groups
            tidy(t.test(test_formula, data = df))$p.value
        }
        }, error = function(e) { NA })
        
        # Combine stats and p-value into a single row
        summary_stats %>%
        mutate(
            Variable = col,
            `P-value` = p_value,
            Level = "" # Add empty level column for merging
        )
    })


    # --- CATEGORICAL COMPARISON ---
    # This combines 'categorical_vars' and 'binary_vars' from the R environment.
    all_categorical_vars <- c(categorical_vars, binary_vars)

    categorical_results <- map_dfr(all_categorical_vars, function(col) {
        
        # Perform Chi-squared test
        p_value <- tryCatch({
        tidy(chisq.test(table(df[[col]], df[[group_col_name]]))) $p.value
        }, error = function(e) { NA })
        
        # Calculate proportions and Wilson CIs for each level of the variable
        df %>%
        filter(!is.na(.data[[col]]) & !is.na(.data[[group_col_name]])) %>%
        count(.data[[group_col_name]], .data[[col]], .drop = FALSE) %>%
        group_by(.data[[group_col_name]]) %>%
        mutate(
            total_n = sum(n),
            prop = n / total_n
        ) %>%
        # Wilson score interval calculation
        mutate(
            z = qnorm(0.975),
            ci_lower = (prop + z^2/(2*total_n) - z * sqrt((prop*(1-prop) + z^2/(4*total_n))/total_n)) / (1 + z^2/total_n),
            ci_upper = (prop + z^2/(2*total_n) + z * sqrt((prop*(1-prop) + z^2/(4*total_n))/total_n)) / (1 + z^2/total_n),
            # Format the output string
            summary_str = sprintf("%d (%.1f%%)", n, prop * 100)
        ) %>%
        ungroup() %>%
        select(all_of(group_col_name), Level = all_of(col), summary_str) %>%
        pivot_wider(names_from = all_of(group_col_name), values_from = summary_str, values_fill = "0 (0.0%)") %>%
        mutate(
            Variable = col,
            `P-value` = p_value
        )
    })

    # Combine numeric and categorical results
    # Use bind_rows to handle potentially different column orders
    combined_results <- bind_rows(numeric_results, categorical_results)
        """
        result_table = """
    result_table <- combined_results %>%
        # Move Variable, Level, and P-value to the front
        select(Variable, Level, `P-value`, everything()) %>%
        # Arrange the results by Variable and then by Level
        arrange(Variable, Level)
        """
    elif "weighted" and "group" in analysis_type:
        package = """
    suppressPackageStartupMessages({
    library(survey)
    library(dplyr)
    library(tibble)
    library(tidyr)
    library(purrr)
    })
    options(survey.lonely.psu = 'adjust')
        """

        factoring_code = """
    # Ensure categorical/binary/outcome vars are factors (trim)
        vars_to_factor <- c(categorical_vars, binary_vars, outcome_var)
    for (col in vars_to_factor) {{
        if (col %in% names(df) && !is.factor(df[[col]])) {{
        df[[col]] <- factor(trimws(as.character(df[[col]])))
        }}
    }}
        """

        design = """
    survey_design <- svydesign(
    ids     = as.formula(paste0('~', psu_var)),
    strata  = as.formula(paste0('~', stratum_var)),
    weights = as.formula(paste0('~', weight_var)),
    data    = df,
    nest    = TRUE
    )
    survey_design <- subset(survey_design, in_analysis == 1)
        """
        formula = """""" ""

        model = """
        vars_catbin   <- unique(c(categorical_vars, binary_vars))
        vars_to_factor <- unique(c(vars_catbin, outcome_var))
        for (col in intersect(vars_to_factor, names(survey_design$variables))) {
        if (is.factor(survey_design$variables[[col]])) {
            old_levels <- levels(survey_design$variables[[col]])
            survey_design$variables[[col]] <- droplevels(survey_design$variables[[col]])
            new_levels <- levels(survey_design$variables[[col]])
            dropped <- setdiff(old_levels, new_levels)
            if (length(dropped) > 0) {
            message(sprintf("Variable '%s' - dropped levels: %s",
                            col, paste(dropped, collapse = ", ")))
            }
        }
        }

        # =========================================
        # Helper functions for numerical analysis
        # =========================================
        n_groups <- nlevels(droplevels(model.frame(survey_design)[[outcome_var]]))

        analyze_one_num <- function(var) {
        stopifnot(var %in% names(df), is.numeric(df[[var]]))
        
        by_outcome <- svyby(
            as.formula(paste0("~", var)),
            as.formula(paste0("~", outcome_var)),
            survey_design,
            svymean,
            na.rm    = TRUE,
            vartype  = "ci",
            keep.names = TRUE
        ) %>% as.data.frame()
        
        ci_l_name <- dplyr::case_when(
            "ci_l" %in% names(by_outcome) ~ "ci_l",
            paste0(var, ".ci_l") %in% names(by_outcome) ~ paste0(var, ".ci_l"),
            TRUE ~ NA_character_
        )
        ci_u_name <- dplyr::case_when(
            "ci_u" %in% names(by_outcome) ~ "ci_u",
            paste0(var, ".ci_u") %in% names(by_outcome) ~ paste0(var, ".ci_u"),
            TRUE ~ NA_character_
        )
        
        stats_tidy <- by_outcome %>%
            transmute(
            variable = var,
            group    = .data[[outcome_var]],
            mean     = .data[[var]],
            ci_l     = if (!is.na(ci_l_name)) .data[[ci_l_name]] else NA_real_,
            ci_u     = if (!is.na(ci_u_name)) .data[[ci_u_name]] else NA_real_
            )
        
        p_val <- if (n_groups > 2) {
            fit <- svyglm(as.formula(paste0(var, " ~ ", outcome_var)), design = survey_design)
            regTermTest(fit, as.formula(paste0("~", outcome_var)), method = "Wald")$p
        } else if (n_groups == 2) {
            svyttest(as.formula(paste0(var, " ~ ", outcome_var)),
                    design = survey_design, na.rm = TRUE)$p.value
        } else {
            NA_real_
        }
        
        stats_tidy <- dplyr::mutate(stats_tidy, p_value = p_val)
        stats_tidy
        }

        # =========================================
        # Helper functions for categorical analysis
        # =========================================
        safe_pval <- function(var, design) {
        if (degf(design) <= 0) return(NA_real_)
        x <- design$variables[[var]]
        y <- design$variables[[outcome_var]]
        if (is.null(x) || is.null(y)) return(NA_real_)
        if (nlevels(droplevels(x)) < 2 || nlevels(droplevels(y)) < 2) return(NA_real_)
        chi_fml <- as.formula(sprintf("~`%s` + `%s`", var, outcome_var))
        out <- tryCatch(
            svychisq(chi_fml, design = design, statistic = "F", na.rm = TRUE),
            error = function(e) NULL
        )
        p <- if (is.null(out)) NA_real_ else suppressWarnings(unname(out$p.value))
        if (is.nan(p)) NA_real_ else p
        }

        tidy_svyby <- function(prop_results, var, outcome_var, design) {
        levs <- levels(design$variables[[var]])
        if (length(levs) < 1) return(tibble())
        purrr::map_dfr(seq_len(nrow(prop_results)), function(i){
            group_val <- prop_results[[outcome_var]][i]
            purrr::map_dfr(levs, function(lev){
            col  <- paste0(var, lev)
            lcol <- paste0("ci_l.", col)
            ucol <- paste0("ci_u.", col)
            tibble(
                variable = var,
                level    = lev,
                group    = as.character(group_val),
                prop     = suppressWarnings(as.numeric(prop_results[[col]][i])),
                ci_l     = suppressWarnings(as.numeric(prop_results[[lcol]][i])),
                ci_u     = suppressWarnings(as.numeric(prop_results[[ucol]][i]))
            )
            })
        })
        }

        analyze_categorical <- function(var) {
        p_val <- safe_pval(var, survey_design)
        by_fml  <- as.formula(sprintf("~`%s`", outcome_var))
        lev_fml <- as.formula(sprintf("~`%s`", var))
        
        prop_wide <- svyby(
            lev_fml, by_fml, survey_design,
            svymean, na.rm = TRUE, vartype = "ci"
        )
        
        tidy <- tidy_svyby(prop_wide, var, outcome_var, survey_design)
        if (nrow(tidy) == 0) return(tibble())
        
        tidy %>%
            mutate(p_value = p_val) %>%
            relocate(variable, level, group, prop, ci_l, ci_u, p_value)
        }
        """

        result_table = """
    numerical_results <- purrr::map_dfr(numerical_vars, analyze_one_num)
    categorical_results <- purrr::map_dfr(vars_catbin, analyze_categorical)

    # Add a type column so you know which is which
    numerical_results <- numerical_results %>%
    mutate(type = "numerical")
    categorical_results <- categorical_results %>%
    mutate(type = "categorical")

    # Combine them
    result_table <- bind_rows(numerical_results, categorical_results)
        """
    elif "mediation" in analysis_type.lower():
        package = """
    suppressPackageStartupMessages(library(mediation))
    suppressPackageStartupMessages(library(stats))
    suppressPackageStartupMessages(library(dplyr))
    suppressPackageStartupMessages(library(stringr))
        """
        factoring_code = f"""
    all_predictors <- c(categorical_vars, binary_vars, numerical_vars)

    # drop IV, mediator, outcome from covariates
    covariates <- setdiff(all_predictors, c(independent_var, mediator_var, outcome_var))


    # ----------------------------
    # 1) Factor IV + choose reference group
    # ----------------------------
    df[[independent_var]] <- trimws(as.character(df[[independent_var]]))
    df[[independent_var]] <- factor(df[[independent_var]])

    iv_levels <- levels(df[[independent_var]])
    preferred_refs <- grep("healthy|control|0", iv_levels, ignore.case = TRUE, value = TRUE)
    reference_group <- preferred_refs[1]
    if (is.na(reference_group)) reference_group <- iv_levels[1]

    df[[independent_var]] <- relevel(df[[independent_var]], ref = reference_group)
    cat(paste0("Reference group for '", independent_var, "' set to: ", reference_group, "\n"))

    # Other factor vars (optional but consistent)
    for (col in c(categorical_vars, binary_vars)) {{
    if (col %in% names(df) && !is.factor(df[[col]])) {{
        df[[col]] <- factor(trimws(as.character(df[[col]])))
    }}
    }}
    # ----------------------------
    # 2) Drop NAs for required columns
    # ----------------------------
    required_cols <- c(independent_var, mediator_var, outcome_var, covariates)
    required_cols <- required_cols[required_cols %in% names(df)]
    df2 <- df %>% tidyr::drop_na(dplyr::all_of(required_cols))
        """
        formula = """
    # ----------------------------
    # 3) Build formulas + fit models
    # ----------------------------
    cov_str <- if (length(covariates) > 0) paste(covariates, collapse = " + ") else ""

    mediator_formula <- as.formula(
    if (cov_str != "")
        paste(mediator_var, "~", independent_var, "+", cov_str)
    else
        paste(mediator_var, "~", independent_var)
    )

    outcome_formula <- as.formula(
    if (cov_str != "")
        paste(outcome_var, "~", independent_var, "+", mediator_var, "+", cov_str)
    else
        paste(outcome_var, "~", independent_var, "+", mediator_var)
    )

    cat(" Mediator Model Formula:\n"); print(mediator_formula)
    cat(" Outcome Model Formula:\n");  print(outcome_formula)
                """

        design = """
        """
        model = """
    med_fit <- lm(mediator_formula, data = df2)
    out_fit <- lm(outcome_formula, data = df2)

    # coefficient tables
    med_coef <- summary(med_fit)$coefficients
    out_coef <- summary(out_fit)$coefficients

    # ----------------------------
    # 4) Run mediate for each non-reference level vs reference
    # ----------------------------
    set.seed(123)

    treat_levels <- setdiff(levels(df2[[independent_var]]), reference_group)

    results_df <- do.call(rbind, lapply(treat_levels, function(g) {
    cat(paste0("Running mediation: Comparing '", g, "' (Treat) vs '", reference_group, "' (Control)\n"))

    m <- mediate(
        model.m = med_fit,
        model.y = out_fit,
        treat = independent_var,
        mediator = mediator_var,
        control.value = reference_group,
        treat.value = g,
        boot = TRUE,
        sims = 100
    )
    s <- summary(m)

    # Find rows for g in lm coefficient tables (robust to naming like varLevel / var_level)
    a_row <- grep(g, rownames(med_coef), value = TRUE)[1]
    cprime_row <- grep(g, rownames(out_coef), value = TRUE)[1]

    # a path: group -> mediator
    a_beta <- if (!is.na(a_row)) med_coef[a_row, "Estimate"] else NA
    a_p    <- if (!is.na(a_row)) med_coef[a_row, "Pr(>|t|)"] else NA

    # b path: mediator -> outcome
    b_beta <- out_coef[mediator_var, "Estimate"]
    b_p    <- out_coef[mediator_var, "Pr(>|t|)"]

    # c' path: group -> outcome (direct)
    cprime_beta <- if (!is.na(cprime_row)) out_coef[cprime_row, "Estimate"] else NA
    cprime_p    <- if (!is.na(cprime_row)) out_coef[cprime_row, "Pr(>|t|)"] else NA


    data.frame(
    Group_Comparison = g,

    Total_Effect_Tau_Estimate = s$tau.coef,
    Total_Effect_95CI_Lower   = s$tau.ci[1],
    Total_Effect_95CI_Upper   = s$tau.ci[2],
    Total_Effect_P_Value      = s$tau.p,

    Indirect_Effect_ACME_Estimate = s$d0,
    Indirect_Effect_95CI_Lower   = s$d0.ci[1],
    Indirect_Effect_95CI_Upper   = s$d0.ci[2],
    Indirect_Effect_P_Value     = s$d0.p,

    a_Path_Independent_Var_to_Mediator_Beta = a_beta,
    a_Path_Independent_Var_to_Mediator_P    = a_p,

    b_Path_Mediator_to_Outcome_Beta = b_beta,
    b_Path_Mediator_to_Outcome_P    = b_p,

    cprime_Path_Independent_Var_to_Outcome_Direct_Beta = cprime_beta,
    cprime_Path_Independent_Var_to_Outcome_Direct_P    = cprime_p,

    stringsAsFactors = FALSE
    )
    }))
        """
        result_table = """
    result_table <- results_df %>%
    mutate(Group_Comparison = gsub("_", " ", Group_Comparison)) 
        """

    stats = f"""
    {package}
    {factoring_code}
    {formula}
    {design}
    {model}
    {result_table}
    """

    return stats


def run_description(analysis, df, schema):
    if "nhanes" in schema:
        id_column = "respondent_sequence_number"
    elif "aireadi" in schema:
        id_column = "person_id"

    r1 = description(analysis, df, id_column)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with localconverter(ro.default_converter + pandas2ri.converter):
                ro.globalenv["df"] = pandas2ri.py2rpy(df)

        ro.r(r1)
        with localconverter(ro.default_converter + pandas2ri.converter):
            report = ro.globalenv["report"]

        return report

    except Exception as e:
        print("R execution failed:", e)
        return None


def imputation_module(analysis, df, schema):
    if "nhanes" in schema:
        id_column = "respondent_sequence_number"
    elif "aireadi" in schema:
        id_column = "person_id"

    if "weighted" in analysis:
        r = f"""
    # ===================================================================
    # R CODE: IMPUTE A SUBSET AND MERGE BACK
    # ===================================================================

    # -- Step 1: Load Libraries and Define Helper Functions --

    library(dplyr)

    # Typed-NA-safe mode (works for character and factor)
    get_mode <- function(x) {{
    x_clean <- x[!is.na(x)]
    if (length(x_clean) == 0) return(x[NA][1])  # NA of same type
    ux <- unique(x_clean)
    ux[which.max(tabulate(match(x_clean, ux)))]
    }}

    # If a numeric column is all-NA, mean(na.rm=TRUE) is NaN; prefer NA instead
    mean_or_na <- function(x) {{
    m <- mean(x, na.rm = TRUE)
    if (is.nan(m)) NA_real_ else m
    }}

    # -- Step 2: Split, Impute, Merge --

    # Rows NOT to be imputed
    df_untouched <- df %>%
    filter(in_analysis != 1)

    # Rows to be imputed
    impute_numeric <- function(x) {{
    m <- mean(x, na.rm = TRUE)
    if (is.nan(m)) return(x)                # leave all-NA columns as NA
    if (is.integer(x)) {{
        m_int <- as.integer(round(m))
        dplyr::if_else(is.na(x), m_int, x)    # stays integer
    }} else {{
        dplyr::if_else(is.na(x), m, x)        # stays double
    }}
    }}

    # use it in your mutate for numeric vars:
    df_imputed <- df %>%
    dplyr::filter(in_analysis == 1) %>%
    dplyr::mutate(
        dplyr::across(all_of(numerical_vars), impute_numeric),
        dplyr::across(all_of(c(binary_vars, categorical_vars)),
                    ~ dplyr::if_else(is.na(.), get_mode(.), .)),
        dplyr::across(all_of(outcome_var), ~ if (is.numeric(.)) {{
        impute_numeric(.)
        }} else {{
        dplyr::if_else(is.na(.), get_mode(.), .)
        }})
    )


    # Combine and order
    final_df <- bind_rows(df_imputed, df_untouched) %>%
    arrange({id_column})   # assumes Python injects a bare column name

    # If not using f-strings to inject the name above, use:
    # final_df <- bind_rows(df_imputed, df_untouched) %>%
    #   arrange(.data[[id_column]])

    # Replace the original
    df <- final_df

        """
        rr = None
    elif "logistic" in analysis:
        print("logistic impute mice")
        r = None
        rr = """
    # --- make sure outcome_var is a single string EARLY ---
    outcome_var <- as.character(outcome_var)[1]

    # Identify predictors and factor candidates
    predictor_vars <- report$variable[report$category %in% c("categorical", "binary", "numerical")]
    factor_candidates <- report$variable[report$category %in% c("categorical", "binary")]

    predictor_vars <- intersect(predictor_vars, names(df))
    factor_candidates <- intersect(factor_candidates, names(df))

    # Convert binary/categorical variables to factor if not already
    for (var in factor_candidates) {
    if (!is.factor(df[[var]])) {
        df[[var]] <- as.factor(df[[var]])
    }
    }

    # Initialize reference_levels table
    reference_levels <- tibble(variable = character(), reference_level = character())

    # Clean, trim, and set reference levels for all factor variables
    preferred_order <- c("healthy","none","control","reference","ref","normal","Q1","low","0","1")

    for (col in factor_candidates) {
    df[[col]] <- factor(trimws(as.character(df[[col]])))
    levels_vec <- levels(df[[col]])
    matches <- tolower(levels_vec)
    ref_level <- NA_character_

    for (keyword in preferred_order) {
        idx <- which(grepl(keyword, matches, ignore.case = TRUE))
        if (length(idx) > 0) {
        ref_level <- levels_vec[idx[1]]
        break
        }
    }

    if (is.na(ref_level)) {
        level_counts <- table(df[[col]])
        ref_level <- names(level_counts)[which.max(level_counts)]
    }

    df[[col]] <- relevel(df[[col]], ref = ref_level)

    reference_levels <- bind_rows(
        reference_levels,
        tibble(variable = col, reference_level = ref_level)
    )
    }

    # -----------------------------
    # Recode outcome to 0/1, then convert to factor(0,1) for mice::logreg
    # -----------------------------
    x_raw <- df[[outcome_var]]
    x_chr <- trimws(tolower(as.character(x_raw)))

    none_tokens <- c("none", "nan", "na", "", "null", "nil", "missing")
    x_chr[x_chr %in% none_tokens] <- NA_character_

    y <- rep(NA_integer_, length(x_chr))
    y[x_chr %in% c("yes", "y", "true", "t")]  <- 1L
    y[x_chr %in% c("no",  "n", "false", "f")] <- 0L

    x_num <- suppressWarnings(as.numeric(x_chr))
    y[is.na(y) & !is.na(x_num) & x_num == 1] <- 1L
    y[is.na(y) & !is.na(x_num) & x_num == 0] <- 0L

    idx <- is.na(y) & !is.na(x_chr)
    if (any(idx)) {
    vals <- sort(unique(x_chr[idx]))
    if (length(vals) != 2) {
        stop(sprintf(
        "Outcome '%s' must have exactly 2 non-missing classes after excluding none. Found: %s",
        outcome_var, paste(vals, collapse = ", ")
        ))
    }
    tab <- table(x_chr[idx])
    minority <- names(tab)[which.min(tab)]
    y[idx] <- as.integer(x_chr[idx] == minority)
    }

    # set outcome and make it 2-level factor for logreg
    df[[outcome_var]] <- factor(y, levels = c(0, 1))

    # sanity check: observed values include both 0 and 1
    u <- sort(unique(df[[outcome_var]][!is.na(df[[outcome_var]])]))
    if (!(length(u) == 2 && all(u == c("0","1")))) {
    stop(sprintf(
        "After recoding, '%s' must contain both 0 and 1 (plus NA). Found: %s",
        outcome_var,
        ifelse(length(u) == 0, "<no non-missing values>", paste(u, collapse = ", "))
    ))
    }

    library(dplyr)
    library(mice)

    # ---- Prep: pick columns we intend to impute ----
    vars_to_impute <- unique(c(numerical_vars, binary_vars, categorical_vars, outcome_var))
    vars_to_impute <- intersect(vars_to_impute, names(df))

    exclude_from_impute <- c(NA_character_, "{id_column}")
    exclude_from_impute <- exclude_from_impute[!is.na(exclude_from_impute) & nzchar(exclude_from_impute)]
    vars_to_impute <- setdiff(vars_to_impute, exclude_from_impute)

    # Ensure binary/categorical are factors BUT DO NOT touch outcome (already factor(0,1))
    df <- df %>%
    mutate(across(
        all_of(setdiff(intersect(c(binary_vars, categorical_vars), names(df)), outcome_var)),
        ~ as.factor(.)
    ))

    # ---- Build mice method vector ----
    meth <- rep("", ncol(df)); names(meth) <- colnames(df)

    meth[intersect(numerical_vars, names(meth))]   <- "pmm"
    meth[intersect(binary_vars, names(meth))]      <- "logreg"
    meth[intersect(categorical_vars, names(meth))] <- "polyreg"

    # Outcome: logreg (binary factor)
    if (outcome_var %in% names(meth)) meth[outcome_var] <- "logreg"

    # Never impute columns not in vars_to_impute
    meth[setdiff(names(meth), vars_to_impute)] <- ""

    # ---- Predictor matrix ----
    pred <- make.predictorMatrix(df)

    exclude_predictors <- c(NA_character_, "{id_column}")
    exclude_predictors <- exclude_predictors[!is.na(exclude_predictors) & nzchar(exclude_predictors)]
    exclude_predictors <- intersect(exclude_predictors, colnames(df))

    pred[, exclude_predictors] <- 0
    pred[exclude_predictors, ] <- 0

    # --- 1. PREP: Final Column Selection ---
    # Identify all variables we need for both imputation and the final model
    vars_to_keep <- unique(c(vars_to_impute, outcome_var, predictor_vars))
    vars_to_keep <- intersect(vars_to_keep, names(df))

    # Create the final subsetted dataframe
    df_for_mice <- df[, vars_to_keep]

    # --- 2. RE-CALC MICE PARAMETERS ---
    # Method vector: align it with our subsetted dataframe
    meth_sub <- meth[vars_to_keep]

    # Predictor Matrix: Regenerate to match the dimensions of df_for_mice
    pred_sub <- make.predictorMatrix(df_for_mice)

    # Zero out ID columns in the predictor matrix (if they exist)
    exclude_pred <- intersect(c(NA_character_, "{id_column}"), vars_to_keep)
    if(length(exclude_pred) > 0) {
    pred_sub[, exclude_pred] <- 0
    pred_sub[exclude_pred, ] <- 0
    }

    # IMPORTANT: Re-calculate 'where' matrix for this specific subset
    # This ensures dimensions match and avoids the "object not found" error later
    where_sub <- is.na(df_for_mice)

    # --- 3. RUN MICE ---
    imp <- mice(
    df_for_mice,
    m = 5,
    maxit = 5,
    method = meth_sub,
    predictorMatrix = pred_sub,
    where = where_sub,
    seed = 123,
    printFlag = FALSE
    )
    print("print")
    print(colSums(is.na(complete(imp, 1))))
    
    # --- 4. ANALYSIS: Fitting the Pooled Model ---
    # Ensure outcome is not in the predictor list
    final_predictors <- intersect(predictor_vars, names(complete(imp, 1)))
    final_predictors <- setdiff(final_predictors, outcome_var)

    # Build a safe formula using backticks for the outcome and predictors
    formula_str <- paste0("`", outcome_var, "` ~ ", 
                        paste0("`", final_predictors, "`", collapse = " + "))

    # Fit the GLM across all imputed datasets
    fit_mi <- with(imp, glm(as.formula(formula_str), family = binomial(link = "logit")))

    # --- 5. POOL & SUMMARIZE ---
    pooled <- pool(fit_mi)
    summary_stats <- summary(pooled, conf.int = TRUE)

    # 1. Clean up column names to avoid "conf.low" duplicates
    # We drop the percentage columns first if they exist to prevent name collisions
    result_table <- summary_stats %>%
    dplyr::select(-any_of(c("2.5 %", "2.5%", "97.5 %", "97.5%"))) %>%
    # Now ensure we have the columns we need
    dplyr::mutate(
        estimate  = exp(estimate),
        conf.low  = exp(conf.low),
        conf.high = exp(conf.high)
    ) %>%
    dplyr::select(term, estimate, std.error, p.value, conf.low, conf.high)

            """

    else:
        r = """
    # Load the dplyr package (install with install.packages("dplyr") if needed)
    library(dplyr)

    # Helper function to calculate the mode (most frequent value)
    get_mode <- function(x) {
    # Remove NAs to ensure they don't affect the mode calculation
    x_clean <- x[!is.na(x)]
    if (length(x_clean) == 0) {
        # If all values were NA, return NA of the correct type
        return(NA_character_)
    }
    # Find unique values
    ux <- unique(x_clean)
    # Return the value with the highest frequency
    return(ux[which.max(tabulate(match(x_clean, ux)))])
    }
            
    # CORRECTED SYNTAX: The pipe operator %>% feeds 'df' into the mutate function,
    # and the result is assigned back to 'df', overwriting the original.
    df <- df %>%
    mutate(
        # Impute numerical variables with their mean
        across(all_of(numerical_vars), ~ ifelse(is.na(.), mean(., na.rm = TRUE), .)),
        
        # Impute binary and categorical variables with their mode
        across(all_of(c(binary_vars, categorical_vars)), ~ ifelse(is.na(.), get_mode(.), .)),
        
        # Impute the outcome variable based on its type
        # This logic handles both numeric (mean) and categorical (mode) outcomes
        across(all_of(outcome_var), ~ if (is.numeric(.)) {
            ifelse(is.na(.), mean(., na.rm = TRUE), .)
        } else {
            ifelse(is.na(.), get_mode(.), .)
        })
    )
        """
        rr = None

    return r, rr


def run_r(analysis, df, schema):
    if "nhanes" in schema:
        id_column = "respondent_sequence_number"
    elif "aireadi" in schema:
        id_column = "person_id"

    r1 = description(analysis, df, id_column)

    r2 = run_stat(analysis)

    r = r1 + "\n" + r2

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with localconverter(ro.default_converter + pandas2ri.converter):
                ro.globalenv["df"] = pandas2ri.py2rpy(df)

        ro.r(r)

        with localconverter(ro.default_converter + pandas2ri.converter):
            result = ro.globalenv["result_table"]
            formula = ro.globalenv["formula"] if "formula" in ro.globalenv else ""
            reference_df = (
                ro.globalenv["reference_levels"]
                if "reference_levels" in ro.globalenv
                else ""
            )
            pairwise_pvalue_table = (
                ro.globalenv["pairwise_pvalue_table"]
                if "pairwise_pvalue_table" in ro.globalenv
                else ""
            )

            report = ro.globalenv["report"]
            print("2222")
            print(report.to_string())

            print("1111")
            print(result.to_string())
            if (report["na_count"] != 0).any():
                r_impute, mice = imputation_module(analysis, df, schema)

                if mice is None:
                    r_impute = r1 + "\n" + r_impute + "\n" + r2 + "\n" + r1
                    try:
                        with warnings.catch_warnings():
                            # This ignores warnings specifically within this block
                            warnings.simplefilter("ignore", UserWarning)

                            # Your rpy2 conversion code that causes the warning
                            with localconverter(
                                ro.default_converter + pandas2ri.converter
                            ):
                                ro.globalenv["df"] = pandas2ri.py2rpy(df)

                        ro.r(r_impute)

                        # --- 4. Get the final result back into Python ---
                        with localconverter(ro.default_converter + pandas2ri.converter):
                            result_impute = ro.globalenv["result_table"]
                            # print("imputed")
                            # print(result_impute.to_string())

                            report_impute = ro.globalenv["report"]
                            # print(report_impute.to_string())
                    except Exception as e:
                        print("R execution failed:", e)

                elif r_impute is None:
                    mice = r1 + "\n" + mice + "\n"
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", UserWarning)
                            with localconverter(
                                ro.default_converter + pandas2ri.converter
                            ):
                                ro.globalenv["df"] = pandas2ri.py2rpy(df)

                        ro.r(mice)

                        with localconverter(ro.default_converter + pandas2ri.converter):
                            result_impute = ro.globalenv["result_table"]
                            # print("imputed")
                            # print(result_impute.to_string())

                            report_impute = None  # ro.globalenv["report"]

                    except Exception as e:
                        print("R execution failed:", e)

                else:
                    r_impute = None
                    result_impute = None
                    report_impute = None
            else:
                r_impute = None
                result_impute = None
                report_impute = None

        return (
            r,
            result,
            reference_df,
            formula,
            report,
            pairwise_pvalue_table,
            r_impute,
            result_impute,
            report_impute,
        )

    except Exception as e:
        print("R execution failed:", e)
        return None, None, None, None, None, None

    #             if (report['na_count'] != 0).any():
    #                 r_impute = r1+"\n"+rr +"\n"+r1
    #                 try:
    #                     with warnings.catch_warnings():
    #                         warnings.simplefilter("ignore", UserWarning)
    #                         with localconverter(ro.default_converter + pandas2ri.converter):
    #                             ro.globalenv["df"] = pandas2ri.py2rpy(df)

    #                     ro.r(r_impute)

    #                     with localconverter(ro.default_converter + pandas2ri.converter):
    #                         result_impute = ro.globalenv["result_table"]
    #                         print("imputed")
    #                         print(result_impute.to_string())

    #                         report_impute = ro.globalenv["report"]
    #                         print(report_impute.to_string())
    #                 except Exception as e:
    #                     print("R execution failed:", e)

    #             else:
    #                 r_impute = None
    #                 result_impute = None
    #                 report_impute = None

    #         return r, result, reference_df, formula, report, pairwise_pvalue_table, r_impute, result_impute, report_impute,

    # except Exception as e:
    #     print("R execution failed:", e)
    #     return None, None, None, None, None, None
