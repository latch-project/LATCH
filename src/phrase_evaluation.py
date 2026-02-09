#!/usr/bin/env python3


import argparse
import ast
from datetime import datetime

import evaluate

import utils
import sys
from pathlib import Path

ROOT = Path.cwd().parents[0]
sys.path.append(str(ROOT))
# sys.path.append(str(Path.cwd().parents[0]))
from config import other_config, data_config, config

schema_configs = data_config.schema_configs
sys.path.append(str(ROOT / "evaluation" / "phrase_evaluation"))
import evaluate_phrase_deviation_question as q


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run phrase deviation tests and log results to CSV."
    )
    p.add_argument(
        "--special",
        type=str,
        default="jan_20_phrase_deviation mainrun",
        help='Run label used in log filename (default: "jan_20_phrase_deviation mainrun").',
    )
    p.add_argument(
        "--llm-provider",
        type=str,
        default="google_gemini-2.5-flash",
        help='LLM provider name (default: "google_gemini-2.5-flash").',
    )
    p.add_argument(
        "--basefolder",
        type=str,
        default="/home/nayoonkim/LATCH_Diabetes/data/results",
        help="Base folder for output CSV logs.",
    )
    p.add_argument(
        "--schema",
        type=str,
        default="nhanes",
        help='Schema name in config (default: "nhanes").',
    )
    return p


def main() -> None:
    args = build_argparser().parse_args()

    special: str = args.special
    llm_provider: str = args.llm_provider
    basefolder: str = args.basefolder
    schema: str = args.schema

    if schema not in schema_configs:
        raise ValueError(
            f"Unknown schema '{schema}'. Available: {', '.join(schema_configs.keys())}"
        )

    log_path = f"{basefolder}/{special}_{llm_provider}_result_log.csv"

    phrases = [
        [
            q.synonyms1,
            utils.match_periods(q.period1),
            q.free_q1,
            list(q.synonyms1.keys()),
        ],
        [
            q.synonyms2,
            utils.match_periods(q.period2),
            q.free_q2,
            list(q.synonyms2.keys()),
        ],
        [
            q.synonyms3,
            utils.match_periods(q.period3),
            q.free_q3,
            list(q.synonyms3.keys()),
        ],
    ]

    for p in phrases:
        dictionary = p[0]
        period = p[1]
        free_question = p[2]
        keys = p[3]

        for key in keys:
            print(key)
            scores = "{" + evaluate.get_score(dictionary, key) + "}"
            parsed = ast.literal_eval(scores)

            results = [item[0] for item in parsed[key][1:]]

            cases = evaluate.generate_test_cases1(free_question, dictionary)
            questions_for_results = [cases[f"{key}::{phrase}"] for phrase in results]

            for result_phrase, derived_question in zip(results, questions_for_results):
                default_phrase = None
                for phrase, value in parsed[key]:
                    if value == "default":
                        default_phrase = phrase
                        break
                    else:
                        print(phrase, value)

                score = None
                for phrase, value in parsed[key]:
                    if phrase == result_phrase:
                        score = value
                        break

                time1 = datetime.now()
                title = utils.random_id()
                word = result_phrase

                print(
                    f"Processing question {default_phrase} : {result_phrase} | title={title}"
                )

                try:
                    (
                        result_dict,
                        usage_logs,
                        alert_messages,
                    ) = utils.make_multiple_dictionaries_grouped(
                        title,
                        schema,
                        [result_phrase],
                        period,
                        derived_question,
                        schema_configs[schema]["dictionary"],
                        schema_configs[schema]["schema_folder"],
                        llm_provider,
                    )
                except Exception as e:
                    print(f"Failed on question #{word} & {derived_question}: {e}")
                    continue

                time2 = datetime.now()
                timea = (time2 - time1).total_seconds()

                print("savehere")

                print(f"{log_path}")

                utils.log_manager_state_to_csv_2(
                    log_path,
                    title,
                    schema,
                    key,
                    default_phrase,
                    list(result_dict.keys())[0],
                    score,
                    result_dict,
                    alert_messages,
                    usage_logs,
                    timea,
                )


if __name__ == "__main__":
    main()
