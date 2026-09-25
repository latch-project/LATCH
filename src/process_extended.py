import utils_extended as utils
import stats
import prompts
import copy
import json
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path
import sys

sys.path.append(str(Path.cwd().parents[0]))
from config import other_config, data_config, config


class FileManager:
    def __init__(self, title, result_log, lookup_table=None, llm_log=None):
        if not result_log:
            raise ValueError("result_log path must be provided.")

        self.title = title
        self.lookup_table = lookup_table
        self.result_log = result_log
        self.llm_log = llm_log

        if lookup_table:
            utils.ensure_lookup_table(self.lookup_table)
        if llm_log:
            utils.ensure_llm_log(self.title, self.llm_log)


class QueryParser:
    def __init__(self, title, question, llm_provider, llm_log=None):
        self.title = title
        self.question = question
        self.llm_provider = llm_provider
        self.prompt0 = prompts.pre_review_step1_parse_request_free_text_extended()
        self.prompt1 = prompts.step1_parse_request_free_text_extended()
        self.prompt2 = prompts.step1_parse_request()
        usage_logs = []

        try:
            response, usage = utils.generate_ai_response(
                self.prompt0, self.question, llm_provider
            )
            print("safeguard")
            print(response)
            self.safeguard1 = response
            cost_details0 = utils.calculate_cost(llm_provider, usage)
            usage_logs.append(cost_details0)
        except Exception as e:
            raise RuntimeError("QueryParser failed at Safeguard 1 LLM call") from e

        if llm_log:
            utils.llm_log_to_csv(
                title, llm_log, "Safeguard 1", self.prompt0, self.question, response
            )

        try:
            response, usage = utils.generate_ai_response(
                self.prompt1, self.question, llm_provider
            )
            cost_details1 = utils.calculate_cost(llm_provider, usage)
            usage_logs.append(cost_details1)
        except Exception as e:
            raise RuntimeError("QueryParser failed at Step 0 free-text parse LLM call") from e
        try:
            self.question_structured = utils.get_first_code_block(response)
            print(self.question_structured)
        except Exception as e:
                raise RuntimeError(
                    f"QueryParser failed at extracting structured question code block. Raw response: {response}"
                ) from e
        
        if llm_log:
            utils.llm_log_to_csv(
                title, llm_log, "Step 0: Parse", self.prompt1, self.question, response
            )

        try:
            response, usage = utils.generate_ai_response(
                self.prompt2, self.question_structured, llm_provider
            )
            self.respone_test = response
            cost_details2 = utils.calculate_cost(llm_provider, usage)
            usage_logs.append(cost_details2)

        except Exception as e:
            raise RuntimeError("QueryParser failed at parse LLM call") from e

        if llm_log:
            utils.llm_log_to_csv(
                title,
                llm_log,
                "Step 1: Parse",
                self.prompt2,
                self.question_structured,
                response,
            )

        try:
            json_str = utils.get_json_block(response)
        except Exception:
            print("Parsing failed!")
            print(response)
            raise RuntimeError(
                f"QueryParser failed at JSON extraction. Raw response: {response}"
            ) from e
        else:
            print("Parsing succeeded")

        json_str = utils.get_json_block(response)

        try:
            self.question_parse = json.loads(json_str)
            # print(self.question_parse)

        except Exception as e:
            raise RuntimeError(
                f"QueryParser failed at JSON loading. JSON string: {json_str}"
            ) from e

        if "nhanes" in self.question_parse["dataset"].lower():
            schema_name = "nhanes"
        elif "aireadi" in self.question_parse["dataset"].lower():
            schema_name = "aireadi"
        elif "registry" in self.question_parse["dataset"].lower():
            schema_name = "registry"
        else:
            schema_name = "nhanes"
            print("dataset not properly detected")

        self.cost = usage_logs
        self.schema = schema_name
        self.schema_folder = data_config.schema_configs[schema_name]["schema_folder"]
        self.dictionary = data_config.schema_configs[schema_name]["dictionary"]
        self.analysis = utils.get_analysis_type(json_str)
        self.period = utils.get_period_of_interest(json_str)
        self.years = utils.match_periods(self.period)



class VariableMatcher:
    def __init__(
        self,
        title,
        question_parse,
        dictionary_path,
        schema_path,
        years,
        schema,
        question,
        enable_lookup,
        enable_adding,
        llm_provider,
        lookup_table=None,
        llm_log=None,
    ): 
        print("--------------")
        print("years")
        print(years)
        try:
            if isinstance(question_parse, str):
                question_parse_dict = json.loads(question_parse)
            else:
                question_parse_dict = question_parse
        except Exception as e:
                raise RuntimeError("VariableMatcher failed at loading question_parse JSON") from e

        try:
            words = utils.get_bottom_level_variables(question_parse_dict).get(
                "bottom_level_variables", []
            )
        except Exception as e:
            raise RuntimeError(
                f"VariableMatcher failed at getting bottom-level variables. question_parse={question_parse_dict}"
            ) from e

        try:
            completed_dictionary, not_found_list = utils.build_keyword_lookup(
                lookup_table,
                words,
                years,
                lookup_enabled=enable_lookup,
            )

        except Exception as e:
            raise RuntimeError(
                f"VariableMatcher failed at lookup table matching. lookup_table={lookup_table}, words={words}, years={years}"
            ) from e
        
        try:
            not_found_keywords, year_list = utils.extract_keywords_and_years(not_found_list)
        except Exception as e:
            raise RuntimeError(
                f"VariableMatcher failed at extracting keywords and years. not_found_list={not_found_list}"
            ) from e

        try:
            (
                source_value_dictionary,
                usage,
                alert_message,
            ) = utils.make_multiple_dictionaries_grouped(
                title,
                schema,
                not_found_keywords,
                year_list,
                question,
                dictionary_path,
                schema_path,
                llm_provider,
                llm_log=llm_log,
            )

        except Exception as e:
            raise RuntimeError(
                f"VariableMatcher failed at LLM dictionary matching. not_found_keywords={not_found_keywords}, year_list={year_list}"
            ) from e

        try:
            if enable_adding is True:
                added = utils.add_to_lookup_table(source_value_dictionary, lookup_table)
        except Exception as e:
            raise RuntimeError(
                f"VariableMatcher failed at adding to lookup table. lookup_table={lookup_table}"
            ) from e
        
        try:
            final_source_value_dictionary = utils.merge_dicts(
                completed_dictionary, source_value_dictionary
            )
        except Exception as e:
            raise RuntimeError(
                "VariableMatcher failed at merging lookup dictionary and LLM dictionary"
            ) from e
        
        try:
            summary = utils.merge_question_with_metadata(
                copy.deepcopy(question_parse_dict), final_source_value_dictionary
            )
            self.summary = utils.process_data_structure(utils.clean_empty_fields(summary))

        except Exception as e:
            raise RuntimeError(
                "VariableMatcher failed at merging metadata into parsed question"
            ) from e
        try:
            verdict, warning = utils.check_column_consistency(self.summary)
            if verdict is False:
                self.prompt_qualify_control = True
                warning = warning
            else:
                self.prompt_qualify_control = False
                warning = None
        except Exception as e:
            raise RuntimeError("VariableMatcher failed at column consistency check") from e

        self.final_source_value_dictionary = final_source_value_dictionary
        self.cost = usage
        self.safeguard2 = alert_message


class SQLGenerator:
    def __init__(
        self,
        title,
        schema,
        question,
        analysis,
        variable_dic,
        years,
        parsed_question,
        summary,
        llm_provider,
        llm_log=None,
    ):
        
        try:
            master_sql, master_schema = utils.master_table_and_schema_creation(
                parsed_question, summary, data_config.schema_configs[schema]["patientid"]
            )
            # print("master_sql")
            # print(master_sql)

        except Exception as e:
            raise RuntimeError(
                f"SQLGenerator failed at master table/schema creation. schema={schema}"
            ) from e
        
        try:
            dataframe, sql, error, attempts, usage_logs, safeguard = utils.process_sql(
                title,
                master_sql,
                master_schema,
                data_config.schema_configs[schema]["patientid"],
                question,
                llm_provider,
                llm_log=llm_log,
            )
        
        except Exception as e:
            raise RuntimeError("SQLGenerator failed at LLM SQL generation/process_sql") from e

        try:
            weight, full_sql_script, cohort_track = utils.sql_refine(
                sql, master_sql, variable_dic, years, schema, analysis
            )

        except Exception as e:
            print("===== SQL REFINE ORIGINAL ERROR =====")
            print("Exception type:", type(e).__name__)
            print("Exception:", repr(e))
            print("SQL:", sql)
            print("years:", years)
            print("schema:", schema)
            print("analysis:", analysis)
            print("=====================================")

            raise
        try:
            cohort = utils.post_hoc_cohort(full_sql_script, cohort_track)
        except Exception as e:
                raise RuntimeError("SQLGenerator failed at post-hoc cohort creation") from e

        self.weight = weight
        self.master_sql = master_sql
        self.llm_based_sql = sql
        self.total_sql = full_sql_script

        try:
            self.dataframe = utils.execute_query(full_sql_script)
        except Exception as e:
            raise RuntimeError(
                f"SQLGenerator failed at final SQL execution. SQL script: {full_sql_script}"
            ) from e

        self.cohort = cohort
        self.error = error
        self.attempts = attempts
        self.cost = usage_logs
        self.safeguard = safeguard

class SQLGenerator_One:
    def __init__(
        self,
        title,
        schema,
        question,
        analysis,
        variable_dic,
        years,
        parsed_question,
        summary,
        llm_provider,
        llm_log=None,
    ):
        
        try:
            master_sql, master_schema = utils.master_table_and_schema_creation(
                parsed_question, summary, data_config.schema_configs[schema]["patientid"]
            )
            # print("master_sql")
            # print(master_sql)

        except Exception as e:
            raise RuntimeError(
                f"SQLGenerator failed at master table/schema creation. schema={schema}"
            ) from e
        
        try:
            dataframe, sql, error, attempts, usage_logs, safeguard = utils.process_sql_oneshot(
                title,
                master_sql,
                master_schema,
                data_config.schema_configs[schema]["patientid"],
                question,
                llm_provider,
                llm_log=llm_log,
            )
        except Exception as e:
            raise RuntimeError("SQLGenerator failed at LLM SQL generation/process_sql") from e
        
        try:
            weight, full_sql_script, cohort_track = utils.sql_refine(
                sql, master_sql, variable_dic, years, schema, analysis
            )
        except Exception as e:
            raise RuntimeError(
                f"SQLGenerator failed at SQL refine. sql={sql}, years={years}, schema={schema}, analysis={analysis}"
            ) from e
        
        self.cohort_sql = cohort_track
        self.master_sql = master_sql
        self.total_sql = sql
        self.error = error
        self.attempts = attempts
        self.cost = usage_logs
        self.safeguard = safeguard

class ProcessStats:
    def __init__(self, dataframe, analysis_method, schema):
        
        try:
            (
                R,
                result,
                reference,
                formula,
                description,
                pairwise_if_exists,
                r_impute,
                result_impute,
                report_impute,
            ) = stats.run_r(analysis_method, dataframe, schema)
        except Exception as e:
            shape = getattr(dataframe, "shape", None)
            raise RuntimeError(
                f"ProcessStats failed at stats.run_r. analysis_method={analysis_method}, schema={schema}, dataframe_shape={shape}"
            ) from e
        
        try:
            if isinstance(pairwise_if_exists, pd.DataFrame):
                print(pairwise_if_exists.to_string())
        except Exception as e:
            raise RuntimeError("ProcessStats failed at printing pairwise dataframe") from e

        try:
            shapes = dataframe.shape
            self.variable = description
            self.R = R
            self.stat_method = analysis_method if analysis_method else ""
            self.stats_summary = result
            self.shape = shapes if shapes else ""
            self.impute_r = r_impute
            self.impute_stats_summary = result_impute
            self.impute_variable = report_impute
        except Exception as e:
            raise RuntimeError("ProcessStats failed at assigning stats outputs") from e


class ResultLogger:
    def __init__(
        self,
        title,
        schema,
        question,
        question_structured,
        question_parse,
        variable_summary,
        weight,
        sql,
        cohort,
        dataframeshape,
        R,
        variable_stat,
        stat_summary,
        impute_R,
        impute_stats,
        impute_variable,
        analysis,
        period,
        years,
        llm_provider,
        safeguard1,
        safeguard2,
        safeguard3,
        total_time,
        total_cost,
        sql_error,
        sql_attempts,
        lookup_table,
        result_log,
        candidates,
        llm_log=None,
    ): 
        self.title = title
        self.schema = schema
        self.question = question
        self.question_structured = question_structured
        self.parsed_question = question_parse
        self.summary = variable_summary
        self.weight = weight
        self.sql = sql
        self.cohort = cohort
        self.dataframeshape = dataframeshape
        self.R = R
        self.variable_stat = variable_stat
        self.stats_summary = stat_summary
        self.impute_r = impute_R
        self.impute_stats = impute_stats
        self.impute_variable = impute_variable
        self.analysis = analysis
        self.period = period
        self.years = years
        self.llm_provider = llm_provider
        self.safeguard1 = safeguard1
        self.safeguard2 = safeguard2
        self.safeguard3 = safeguard3
        self.totaltime = total_time
        self.totalcost = total_cost
        self.sql_error = sql_error
        self.sql_attempts = sql_attempts
        self.lookup_table = lookup_table
        self.result_log = result_log
        self.candidates = candidates
        self.llm_log = llm_log

        headers = [
            "Title",
            "Schema",
            "Question",
            "Structured Question",
            "Parsed Question",
            "Schema Incorportation",
            "Weight",
            "SQL",
            "Cohort",
            "Dataframeshape",
            "R",
            "Variables",
            "Statistics",
            "Impute R",
            "Impute Stats",
            "Impute Variable",
            "Analysis",
            "Period",
            "Years",
            "LLM provider",
            "Safeguard1",
            "Safeguard2",
            "Safeguard3",
            "Total Time",
            "Total Cost",
            "SQL Error",
            "SQL Attempts",
            "Lookup Table",
            "Result Log",
            "Candidates",
            "LLM Log",
        ]

        values = {
            "Title": title,
            "Schema": schema,
            "Question": question,
            "Structured Question": question_structured,
            "Parsed Question": question_parse,
            "Schema Incorportation": variable_summary,
            "Weight": weight,
            "SQL": sql,
            "Cohort": cohort,
            "Dataframeshape": dataframeshape,
            "R": R,
            "Variables": (
                variable_stat.to_dict(orient="records")
                if hasattr(variable_stat, "to_dict")
                else variable_stat
            ),
            "Statistics": (
                stat_summary.to_dict(orient="records")
                if hasattr(stat_summary, "to_dict")
                else stat_summary
            ),
            "Impute R": impute_R,
            "Impute Stats": (
                impute_stats.to_dict(orient="records")
                if hasattr(impute_stats, "to_dict")
                else impute_stats
            ),
            "Impute Variable": (
                impute_variable.to_dict(orient="records")
                if hasattr(impute_variable, "to_dict")
                else impute_variable
            ),
            "Analysis": analysis,
            "Period": period,
            "Years": years,
            "LLM provider": llm_provider,
            "Safeguard1": safeguard1,
            "Safeguard2": safeguard2,
            "Safeguard3": safeguard3,
            "Total Time": total_time,
            "Total Cost": total_cost,
            "SQL Error": sql_error,
            "SQL Attempts": sql_attempts,
            "Lookup Table": lookup_table,
            "Result Log": result_log,
            "Candidates": candidates,
            "LLM Log": llm_log,
        }

        utils.log_row_to_csv(result_log, headers, values)
        if llm_log:
            utils.llm_log_to_csv(
                title,
                llm_log,
                "Step 4:Logging Result for Tracking",
                self.question,
                self.dataframeshape,
                self.stats_summary,
            )



class ResultLoggerBrief:
    def __init__(
        self,
        title,
        schema,
        question,
        question_structured,
        question_parse,
        variable_summary,
        sql,
        cohort,
        analysis,
        period,
        years,
        llm_provider,
        safeguard1,
        safeguard2,
        safeguard3,
        total_time,
        total_cost,
        sql_error,
        sql_attempts,
        lookup_table,
        result_log,
        candidates,
        llm_log=None,
    ):
        self.title = title
        self.schema = schema
        self.question = question
        self.question_structured = question_structured
        self.parsed_question = question_parse
        self.summary = variable_summary
        self.sql = sql
        self.cohort = cohort
        self.analysis = analysis
        self.period = period
        self.years = years
        self.llm_provider = llm_provider
        self.safeguard1 = safeguard1
        self.safeguard2 = safeguard2
        self.safeguard3 = safeguard3
        self.totaltime = total_time
        self.totalcost = total_cost
        self.sql_error = sql_error
        self.sql_attempts = sql_attempts
        self.lookup_table = lookup_table
        self.result_log = result_log
        self.candidates = candidates
        self.llm_log = llm_log

        headers = [
            "Title",
            "Schema",
            "Question",
            "Structured Question",
            "Parsed Question",
            "Schema Incorportation",
            "SQL",
            "Analysis",
            "Period",
            "Years",
            "LLM provider",
            "Safeguard1",
            "Safeguard2",
            "Safeguard3",
            "Total Time",
            "Total Cost",
            "SQL Error",
            "SQL Attempts",
            "Lookup Table",
            "Result Log",
            "Candidates",
            "LLM Log",
        ]

        values = {
            "Title": title,
            "Schema": schema,
            "Question": question,
            "Structured Question": question_structured,
            "Parsed Question": question_parse,
            "Schema Incorportation": variable_summary,
            "SQL": sql,
            "Analysis": analysis,
            "Period": period,
            "Years": years,
            "LLM provider": llm_provider,
            "Safeguard1": safeguard1,
            "Safeguard2": safeguard2,
            "Safeguard3": safeguard3,
            "Total Time": total_time,
            "Total Cost": total_cost,
            "SQL Error": sql_error,
            "SQL Attempts": sql_attempts,
            "Lookup Table": lookup_table,
            "Result Log": result_log,
            "Candidates": candidates,
            "LLM Log": llm_log,
        }

        utils.log_row_to_csv(result_log, headers, values)
        if llm_log:
            utils.llm_log_to_csv(
                title,
                llm_log,
                "Step 4:Logging Result for Tracking",
                self.question,
                self.dataframeshape,
                self.stats_summary,
            )
