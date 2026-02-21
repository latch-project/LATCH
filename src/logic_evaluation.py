#!/usr/bin/env python3 

from datetime import datetime
import argparse
import utils
from process import (
    FileManager,
    QueryParser,
    VariableMatcher,
    SQLGenerator,
)

import sys
from pathlib import Path

ROOT = Path.cwd().parents[0]
sys.path.append(str(ROOT))

from config import other_config, data_config, config

schema_configs = data_config.schema_configs
sys.path.append(str(ROOT / "evaluation" / "logic_evaluation"))
import evaluate_sql_question as q2


EVALUATE_SQL_PROMPT = """
Your goal is evaluate if the given sql accurately matches the given problem statement.
Be succinct. If correct then correct no comment if not, just say where was wrong.
""".strip()


def question_and_sql(question: str, sql: str) -> str:
    return f"""
The original problem statement was:
{question}

And the SQL formed was:
{sql}
""".strip()

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

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run SQL question generation/parsing/grounding/SQL-gen/eval with configurable settings."
    )

    parser.add_argument(
        "--special",
        type=str,
        default="jan_15_sql_run1",
        help="Run identifier name (used in output filenames).",
    )

    parser.add_argument(
        "--llm_provider",
        type=str,
        default="google_gemini-2.5-flash",
        help="LLM provider name (e.g., google_gemini-2.5-flash, openai_gpt-4o-2024-11-20, anthropic_claude-sonnet-4-20250514).",
    )

    parser.add_argument(
        "--basefolder",
        type=str,
        default="/home/nayoonkim/LATCH_Diabetes/data/results",
        help="Base folder where output CSV logs will be written.",
    )

    parser.add_argument(
        "--disable_lookup",
        action="store_true",
        help="Disable lookup against existing grounding lookup table (sets enable_lookup=False).",
    )

    parser.add_argument(
        "--disable_adding",
        action="store_true",
        help="Disable adding new entries into grounding lookup table (sets enable_adding=False).",
    )

    parser.add_argument(
        "--print_config",
        action="store_true",
        help="Print the resolved run configuration at startup.",
    )

    return parser.parse_args()

def build_all_questions():
    """
    Returns a list of dicts with:
        - question: str
        - topic: str  (a/b/c)
        - level: str  (easy/moderate/hard)
        - index: int  (1..N within that (topic,level))
        - var_name: str (e.g., sql_easy_a_1)
    """
    all_questions = []

    example_topic_pairs = [
        (q2.example, "a"),
        (q2.example_2, "b"),
        (q2.example_3, "c"),
    ]

    levels = ["easy", "moderate", "hard"]

    number_of_questions = [
        11, 11, 10,    # a: easy, moderate, hard
        11, 12, 12,    # b: easy, moderate, hard
        11, 11, 11     # c: easy, moderate, hard
    ]

    counter = 0

    for example, topic in example_topic_pairs:
        for level in levels:
            count = number_of_questions[counter]
            counter += 1

            for i in range(1, count + 1):
                var_name = f"sql_{level}_{topic}_{i}"

                try:
                    sql_value = getattr(q2, var_name)
                    text = build_text(example, sql_value)

                    all_questions.append(
                        {
                            "question": text,
                            "topic": topic,
                            "level": level,
                            "index": i,
                            "var_name": var_name,
                        }
                    )

                    print(f"[HIT] {var_name}")

                except AttributeError:
                    print(f"[MISS] {var_name} not found")

                except Exception as e:
                    print(f"[FAIL] {var_name}: {e}")
    
    return all_questions



def main() -> None:
    args = parse_args()

    special = args.special
    llm_provider = args.llm_provider
    basefolder = args.basefolder

    lookup_table = f"{basefolder}/{special}_{llm_provider}_lookup.csv"

    result_log = (
    f"{basefolder}/{special}_{llm_provider}_result_log.csv"
)
    llm_log = (
None  # f"{result_folder}/{analysis_name}_{llm_provider}_llm_log.csv"
)

    enable_lookup = not args.disable_lookup
    enable_adding = not args.disable_adding

    if args.print_config:
        print("===== RUN CONFIG =====")
        print(f"special: {special}")
        print(f"llm_provider: {llm_provider}")
        print(f"basefolder: {basefolder}")
        print(f"lookup_table: {lookup_table}")
        print(f"result_log: {result_log}")
        print(f"enable_lookup: {enable_lookup}")
        print(f"enable_adding: {enable_adding}")
        print("======================")

    all_items = build_all_questions()

    for global_idx, item in enumerate(all_items, start=1):

        question = item["question"]
        topic = item["topic"]
        level = item["level"]
        local_index = item["index"]
        var_name = item["var_name"]

        print("=========question number==========")
        print(global_idx - 1)
        print(f"topic={topic} level={level} i={local_index} var={var_name}")

        time_start = datetime.now()
        title = utils.random_id()

        manager = FileManager(title, result_log, lookup_table, llm_log)

        # ---- Parse question ----
        try:
            parsed_query_info = QueryParser(
                title=title,
                question=question,
                llm_provider=llm_provider,
                llm_log=llm_log,
            )
        except Exception as e:
            print(f"Failed parsing step on question #{global_idx}")
            continue

        # ---- Variable matching / schema grounding ----
        try:
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

        except Exception as e:
            import traceback
            print(f"Failed schema grounding on question #{global_idx}: {e}")
            traceback.print_exc()
            continue
        # except Exception as e:
        #     print(f"Failed schema grounding on question #{global_idx}")
        #     continue

        # ---- SQL generation ----
        try:
            sql = SQLGenerator(
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
        except Exception as e:
            print(f"Failed sql generation on question #{global_idx}")
            continue

        elapsed = (datetime.now() - time_start).total_seconds()

        # ---- LLM evaluation of SQL correctness ----
        response, usage = utils.generate_ai_response(
            str(EVALUATE_SQL_PROMPT),
            str(question_and_sql(question, sql.total_sql)),
            llm_provider,
        )

        # ---- Logging ----
        utils.log_manager_state_to_csv_3(
            result_log,
            title,
            parsed_query_info.schema,
            topic,
            level,
            question,
            parsed_query_info.question_structured,
            parsed_query_info.question_parse,
            variable_matcher.final_source_value_dictionary,
            sql.llm_based_sql,
            sql.safeguard,
            sql.error,
            sql.attempts,
            sql.cost,
            elapsed,
            response,
        )


if __name__ == "__main__":
    main()
