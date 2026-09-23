# LATCH: LLM-Assisted Testing of Clinical Hypotheses

**LATCH** is a framework that translates natural-language clinical questions into reproducible statistical analyses with structured health data.

---

## Versioned Releases

Versioned releases of LATCH are available through GitHub Releases.

Current stable release: `v1.0.0`

Users seeking a fixed version of the code should use a tagged release rather than the continuously updated `main` branch.

---

## Getting Started

### Prerequisites

Install the following tools before setting up the project:

* [Conda or Miniconda](https://docs.conda.io/)
* [Docker](https://www.docker.com/)
* PostgreSQL (provided via Docker)

---

##  Environment Setup

### 1. Clone the Repository

```bash
git clone git@github.com:latch-project/LATCH.git
cd LATCH
```

### 2. Create and Activate the Conda Environment

```bash
conda env create -f environment.yml -n latch_conda
conda activate latch_conda
```

### 3. Configure Environment Variables

Create a `.env` file in the root `LATCH/` directory:

```env
# API Keys
GOOGLE_API_KEY=your_google_key

# Database Configuration
POSTGRES_DB=latch
POSTGRES_USER=latchuser
POSTGRES_PASSWORD=your_password
```

---

## Database Setup

Launch the PostgreSQL database using Docker:

```bash
docker compose -f database.yaml up -d
```

This maps PostgreSQL’s internal port (5432) to port **10010** on your local machine. You may change this to any available port.

---

## Datasets

LATCH currently supports the following datasets:

### NHANES

National Health and Nutrition Examination Survey
Publicly available from official NHANES sources.

### AI-READI

Artificial Intelligence Ready and Exploratory Atlas for Diabetes Insights
Access requires a request via:

[https://aireadi.org/dataset](https://aireadi.org/dataset)

---

## Data Processing Pipeline

After obtaining the datasets, organize AI-READI data as:

```
data/
└── aireadi/
    └── dataset/
        ├── clinical_data/
        ├── retinal_oct/
        ├── retinal_octa/
        └── ...
```

NHANES data can be downloaded directly by the pipeline.

Run preprocessing and harmonization:

```bash
python preprocessing/run_pipeline.py \
  --aireadi-dir /path/to/data/aireadi \
  --nhanes-dir /path/to/data/nhanes
```

---

## Analysis Applications

LATCH includes modular analysis workflows for study reproduction, extensions, and exploratory research.

### Directory Structure

```
analyses/
├── scripts/   # Analysis workflows and runnable scripts
├── prompts/   # Input prompts and configuration files
└── results/   # Generated outputs from previous runs
```

### analyses/scripts/

Executable workflows for:

- **Study reproduction** — reproduction of previously published analyses
- **Study extension** — targeted extensions of existing analyses
- **Hypothesis-generating studies** — exploratory analyses beginning from investigator-formulated research questions

Each script can be run independently and may reference prompts from `analyses/prompts/`.

### analyses/prompts/

Configuration files and prompts used as inputs to analysis scripts.

Workflow:

1. Create or edit a prompt
2. Run a script from `analyses/scripts/`
3. Review outputs in `analyses/results/`

### analyses/results/

Stores generated outputs (processed data, figures, logs) for reproducibility and reference.

### Typical Workflow

1. Edit or create a prompt in `analyses/prompts/`
2. Run a script from `analyses/scripts/`
3. Inspect outputs in `analyses/results/`

---

## Representative End-to-End Example

The repository contains the prompts, analysis scripts, and generated outputs for the study-reproduction analyses.

For a representative end-to-end example, see the following NHANES reproduction analysis:

- **Input prompt:** `analyses/prompts/fig2_reproduction/2_3.txt`
- **Analysis script:** `src/run_latch.py`
- **Generated output:** `analyses/results/fig2_reproduction/fig_2_2_3_google_gemini-2.5-flash_result_log.csv`

After completing the environment and database setup above, run:

```bash
PYTHONPATH="$PWD:$PWD/src" python src/run_latch.py \
  --result-folder analyses/results/fig2_reproduction \
  --analysis-name fig_2_2_3 \
  --llm-provider google_gemini-2.5-flash \
  --question "$(cat analyses/prompts/fig2_reproduction/2_3.txt)"
```

Then inspect the generated output in:

```text
analyses/results/fig2_reproduction/fig_2_2_3_google_gemini-2.5-flash_result_log.csv
```

This example demonstrates the workflow from the natural-language research prompt through study specification, variable mapping, analysis generation, statistical analysis, safeguards, and result logging.

## Expected Runtime

**Data preparation and setup.** Using the provided pipeline, NHANES data preparation typically requires approximately 2–3 hours from download through PostgreSQL loading and schema generation. Processing the tabular portion of AI-READI typically requires approximately 1–2 hours after the dataset has been downloaded. Runtime can vary depending on network conditions, local hardware, and available computing resources.

**Analysis runtime.** In the reported analyses, individual runs from natural-language input through statistical analysis and result generation typically required approximately 2–15 minutes. Runtime can vary depending on LLM API response latency, network conditions, database execution time, analysis complexity, and the specific model or provider used.

---

## Evaluation Framework

The repository includes evaluation pipelines and benchmark experiments.

### Directory Structure

```
evaluation/
├── api_variation/
├── content_evaluation/
├── logic_evaluation/
└── phrase_evaluation/
```

These directories contain datasets, experiment code, and results used to evaluate LATCH performance.

---

## Notes

These scripts are provided to document the workflow used in the study. LATCH includes stochastic LLM-assisted components, and exact generated outputs may differ across reruns. 

NHANES data are retrieved from external source URLs maintained by NHANES. Because these upstream resources may change over time, future reruns may be affected by changes in file availability, URLs, or source organization.

---

## Citation

If you use LATCH in your research, please cite:

```bibtex
@article{gim2026medrxiv,
  title   = {An LLM-assisted framework for accelerated and verifiable clinical hypothesis testing from electronic health records},
  author  = {Gim, Nayoon and Gim, In and Jiang, Yu and Kihara, Yuka and Blazes, Marian and Wu, Yue and Lee, Cecilia S. and Lee, Aaron Y.},
  journal = {medRxiv},
  year    = {2026},
  doi     = {10.64898/2026.02.10.26346008},
  url     = {https://doi.org/10.64898/2026.02.10.26346008}
}
```

---

