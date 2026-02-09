import os
from dotenv import load_dotenv
from pathlib import Path

# print(config.DB_NAME)
# print(data_config.nhanes_config)

# Path to the .env file in LATCH_final
root_path = Path(__file__).resolve().parent
env_path = root_path / ".env"
load_dotenv(dotenv_path=env_path)
data_path = root_path / "data"
results_path = root_path / "results"
figures_path = root_path / "figures"
analyses_path = root_path / "analyses"
evaluation_path = root_path / "evaluation"


class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Database
    DB_NAME = os.getenv("POSTGRES_DB", "latch")
    DB_USER = os.getenv("POSTGRES_USER", "latchuser")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = int(os.getenv("POSTGRES_PORT", 10010))


config = Config()


class DataConfig:
    root = data_path

    schema_configs = {
        "nhanes": {
            "schema_folder": f"{root}/nhanes/schema",
            "dictionary": f"{root}/nhanes/metadata/schema_summary.csv",
            "patientid": "respondent_sequence_number",
        },
        "aireadi": {
            "schema_folder": f"{root}/aireadi/schema",
            "dictionary": f"{root}/aireadi/schema_summary/schema_summary.csv",
            "patientid": "person_id",
        },
    }

    nhanes_config = {
        "keyword_column": "SAS Label",
        "columns_to_keep": [
            "SAS Label",
            "Data File Description",
            "Data File Name",
            "Variable Name",
            "Component",
            "Variable Description",
        ],
        "table_name_column": "Data File Name",
        "variable_name_column": "SAS Label",
        "display_input_column": [
            "SAS Label",
            "Data File Description",
            "Data File Name",
            "Variable Name",
            "Component",
            "Variable Description",
        ],
        "display_output_column": [
            "Year",
            "Keyword",
            "Matched Keyword",
            "Table Description",
            "Table",
            "Variable Code",
            "Domain",
            "Description",
            "Examples",
        ],
    }
    aireadi_config = {
        "keyword_column": "column_name",
        "columns_to_keep": [
            "column_name",
            "column_description",
            "table_name",
            "values",
        ],
        "table_name_column": "table_name",
        "variable_name_column": "column_name",
        "display_input_column": ["column_name", "table_name", "values"],
        "display_output_column": [
            "Year",
            "Keyword",
            "Matched Keyword",
            "Table",
            "Examples",
            "Examples",
        ],
    }

    config_map = {"nhanes": nhanes_config, "aireadi": aireadi_config}


data_config = DataConfig()


class OtherConfig:
    results_path = results_path
    figures_path = figures_path
    analyses_path = analyses_path
    evaluation_path = evaluation_path


other_config = OtherConfig()
