import argparse
from pathlib import Path
from datetime import datetime

import utils_extended as utils
from process_extended import (
    FileManager,
    QueryParser,
    VariableMatcher,
    SQLGenerator_One,
    ResultLoggerBrief,
)


def main(result_folder, prompt_folder, sql_folder, analysis_name, llm_provider):
    result_folder = Path(result_folder)
    prompt_folder = Path(prompt_folder)
    sql_folder = Path(sql_folder)

    result_folder.mkdir(parents=True, exist_ok=True)
    sql_folder.mkdir(parents=True, exist_ok=True)
 
    question_files = sorted(prompt_folder.glob("*.txt"))
    enable_lookup = False
    enable_adding = False
    lookup_table = None
    llm_log = None

    for question_path in question_files:
        question_basename = question_path.stem

        result_log = (
            result_folder
            / f"{analysis_name}_{llm_provider}_{question_basename}_result_log.csv"
        )


    # for question_file in question_files:
    #     question_path = prompt_folder / question_file

    #     result_log = result_folder / f"{analysis_name}_{llm_provider}_{question_file}_result_log.csv"

        if result_log.exists():
            result_log.unlink()
        
        if not question_path.exists():
            print(f"Skipping {question_path.name}: file not found")
            continue

        with open(question_path, "r") as f:
            question = f.read().strip()

        if not question:
            print(f"Skipping {question_path.name}: file is empty")
            continue


        # if not question_path.exists():
        #     print(f"Skipping {question_file}: file not found")
        #     continue

        # with open(question_path, "r") as f:
        #     question = f.read().strip()

        # if not question:
        #     print(f"Skipping {question_file}: file is empty")
        #     continue

        start_time = datetime.now()
        title = utils.random_id()

        print(f"Processing {question_path.name} | title={title}")


        manager = FileManager(title, result_log, lookup_table, llm_log)

        parsed_query_info = QueryParser(
            title,
            question,
            llm_provider,
            llm_log,
        )

        variable_matcher = VariableMatcher(
            title=title,
            question_parse=parsed_query_info.question_parse,
            dictionary_path=parsed_query_info.dictionary,
            schema_path=parsed_query_info.schema_folder,
            years=parsed_query_info.years,
            schema=parsed_query_info.schema,
            question=question,
            enable_lookup=enable_lookup,
            enable_adding=enable_adding,
            llm_provider=llm_provider,
            lookup_table=manager.lookup_table,
            llm_log=llm_log,
        )

        sql = SQLGenerator_One(
            title,
            parsed_query_info.schema,
            question,
            parsed_query_info.analysis,
            variable_matcher.final_source_value_dictionary,
            parsed_query_info.years,
            parsed_query_info.question_parse,
            variable_matcher.summary,
            llm_provider,
            llm_log,
        )

        question_basename = question_path.stem

        with open(sql_folder / f"{question_basename}_total_sql.sql", "w") as f:
            f.write(sql.total_sql)

        with open(sql_folder / f"{question_basename}_cohort_sql.sql", "w") as f:
            f.write(sql.cohort_sql)

        total_time = (datetime.now() - start_time).total_seconds()

        ResultLoggerBrief(
            title,
            parsed_query_info.schema,
            parsed_query_info.question,
            parsed_query_info.question_structured,
            parsed_query_info.question_parse,
            variable_matcher.summary,
            sql.total_sql,
            sql.cohort_sql,
            parsed_query_info.analysis,
            parsed_query_info.period,
            parsed_query_info.years,
            parsed_query_info.llm_provider,
            parsed_query_info.safeguard1,
            variable_matcher.safeguard2,
            sql.safeguard,
            total_time,
            [parsed_query_info.cost, variable_matcher.cost, sql.cost],
            sql.error,
            sql.attempts,
            lookup_table,
            result_log,
            utils.retrieve_candidates(top_n=40,record=variable_matcher.summary).to_dict(orient="records"),
            llm_log,
        )

        print(f"Finished {question_path.name} in {total_time:.2f} seconds")

    print("All questions finished successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--result_folder", required=True)
    parser.add_argument("--prompt_folder", required=True)
    parser.add_argument("--sql_folder", required=True)
    parser.add_argument("--analysis_name", default="registry_sql")
    parser.add_argument("--llm_provider", default="google_gemini-2.5-flash")

    args = parser.parse_args()

    main(
        result_folder=args.result_folder,
        prompt_folder=args.prompt_folder,
        sql_folder=args.sql_folder,
        analysis_name=args.analysis_name,
        llm_provider=args.llm_provider,
    )