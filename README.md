# LATCH: LLM-Assisted Testing of Clinical Hypotheses

**LATCH** is a framework that translates natural-language clinical questions into reproducible statistical analyses with structured health data.

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

* **Study replication** — replication of published results
* **Study extension** — expand existing studies
* **New insights** — exploratory analyses

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

## Citation

If you use LATCH in your research, please cite:

```bibtex
@article{example2026medrxiv,
  title   = {An LLM-assisted framework for accelerated and verifiable clinical hypothesis testing from electronic health records},
  author  = {Gim, Nayoon and Gim, In and Jiang, Yu and Kihara, Yuka and Blazes, Marian and Wu, Yue and Lee, Cecilia S. and Lee, Aaron Y.},
  journal = {medRxiv},
  year    = {2026},
  doi     = {10.64898/2026.02.10.26346008},
  url     = {https://doi.org/10.64898/2026.02.10.26346008}
}
```

---

