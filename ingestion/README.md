# Data Ingestion Module

This module provides tools for ingesting structured datasets from YAML data hierarchy files through the OpenGIN services. It processes hierarchical data structures (ministers, departments, categories, subcategories, and datasets) and creates corresponding entities and relationships in the OpenGIN system.

## Overview

The ingestion system reads YAML data hierarchy files that describe the structure of datasets organized in a flexible hierarchy:
- **Ministers** → **Categories** → **Subcategories** → **Datasets**
- **Ministers** → **Categories** → **Datasets**
- **Ministers** → **Departments** → **Categories** → **Subcategories** → **Datasets**
- **Ministers** → **Departments** → **Categories** → **Datasets**

It also supports ingesting **citizen profiles** — personal datasets attached to individual citizen entities. Profiles are year-independent and are processed separately using the `--profiles` flag.

Each dataset is stored as a JSON file and is ingested as an attribute on the appropriate parent entity (category, subcategory, or citizen).

## Prerequisites

Before running the ingestion script, ensure you have completed the following setup steps:

### 1. Start OpenGIN Services

Make sure the OpenGIN services are up and running. The ingestion script requires:
- **Read Service**: For querying existing entities and relationships
- **Ingestion Service**: For creating and updating entities

### 2. Restore Data Backup

Restore the `0.0.1` data backup to ensure you have the base entities (ministers, departments, etc.) that the ingestion script will reference and build upon.

### 3. Set Up Python Environment

Create a virtual environment and install the required dependencies.

**Option 1: Using Mamba or Conda (Recommended)**

```bash
# Create the environment from environment.yml
mamba env create -f environment.yml

# Or using Conda:
# conda env create -f environment.yml

# Activate the environment
mamba activate datasets_env

# Or using Conda:
# conda activate datasets_env
```

**Option 2: Using Python venv**

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment

# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

The ingestion script requires the following environment variables:

- `READ_BASE_URL`: Base URL for the OpenGin Read Service
- `INGESTION_BASE_URL`: Base URL for the OpenGin Ingestion Service

You can set these in your environment or create a `.env` file in the `ingestion/` directory:

```bash
export READ_BASE_URL="http://localhost:8081"
export INGESTION_BASE_URL="http://localhost:8080"
```

Or create a `.env` file:
```
READ_BASE_URL=http://localhost:8081
INGESTION_BASE_URL=http://localhost:8080
```

If using a `.env` file, make sure you have `python-dotenv` installed (included in `requirements.txt`).

## Usage

Once all prerequisites are met, you can run the ingestion script:

```bash
# From the project root directory
python -m ingestion.ingest_data_yaml data/statistics/2020/data_hierarchy_2020.yaml

# Or with an explicit year override
python -m ingestion.ingest_data_yaml data/statistics/2020/data_hierarchy_2020.yaml --year 2020

# Ingest citizen profiles (no year required)
python -m ingestion.ingest_data_yaml data/people/profiles_hierarchy.yaml --profiles
```

### Command Line Arguments

| Argument | Type | Description |
|---|---|---|
| `yaml_file` | required | Path to the YAML manifest file |
| `--year` | optional | Override the year extracted from the filename |
| `--profiles` | optional flag | Process a profiles YAML — skips year extraction and only processes citizen entries |

### Standard Mode (without `--profiles`)

Used for ingesting statistical datasets organised by ministers, departments, and categories. A year is required (either extracted from the filename or provided via `--year`).

```bash
# Ingest 2020 data
python -m ingestion.ingest_data_yaml data/statistics/2020/data_hierarchy_2020.yaml

# Ingest 2021 data
python -m ingestion.ingest_data_yaml data/statistics/2021/data_hierarchy_2021.yaml
```

In this mode the script will:
- Extract the year from the filename (or use `--year`)
- Process governments, ministers, departments, categories, and their datasets

### Profiles Mode (`--profiles`)

Used for ingesting citizen profile datasets. Profiles are personal data records (e.g. name, political party, date of birth) attached to existing citizen entities. They are **not** year-specific.

```bash
# Ingest citizen profiles
python -m ingestion.ingest_data_yaml data/people/profiles_hierarchy.yaml --profiles
```

In this mode the script will:
- **Skip** year extraction entirely
- **Skip** government and minister processing
- Only process citizen entries and attach their profile datasets as attributes

## How It Works

### Standard Mode
1. **Parse YAML Manifest**: Reads the YAML file to extract the hierarchical structure
2. **Find Entities**: Uses the Read Service to find existing ministers and departments by name and year
3. **Create Categories**: Creates category and subcategory entities as needed
4. **Process Datasets**: Reads dataset JSON files and adds them as attributes to parent entities
5. **Create Relationships**: Establishes relationships between entities (e.g., `AS_CATEGORY`)

### Profiles Mode (`--profiles`)
1. **Parse YAML Manifest**: Reads the profiles YAML file to extract citizen entries
2. **Find Citizens**: Uses the Read Service to look up existing citizen entities by name
3. **Process Profiles**: Reads each citizen's profile `data.json` and attaches it as an attribute on the citizen entity using the citizen's own start/end time period

## Module Structure

```
ingestion/
├── ingest_data_yaml.py      # Main ingestion script
├── .env                     # Environment variables
├── exception/               # Exception handling
│   └── exceptions.py
├── models/                  # Data models and schemas
│   └── schema.py
├── services/                # Service layer
│   ├── entity_resolver.py   # Entity lookup and resolution
│   ├── ingestion_service.py # OpenGin Ingestion API client
│   ├── read_service.py      # OpenGin Read API client
│   └── yaml_parser.py       # YAML parsing utilities
├── utils/                   # Utility functions
│   ├── date_utils.py        # Date/time calculations
│   ├── http_client.py       # HTTP client for API calls
│   └── util_functions.py    # General utilities
└── requirements.txt         # Python dependencies
```

## Troubleshooting

### ModuleNotFoundError: No module named 'ingestion'

Make sure you're running the command from the project root directory (`/Users/LDF/Documents/datasets/`), not from within the `ingestion/` folder.

### Missing Dependencies

If you encounter import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Environment Variables Not Set

The script will exit with an error if `READ_BASE_URL` or `INGESTION_BASE_URL` are not set. Make sure these are configured before running.

### Connection Errors

If you see connection errors, verify that:
- OpenGin services are running
- The base URLs in your environment variables are correct
- Your network/firewall allows connections to these services

## Notes

- The script processes ministers and citizens sequentially
- Datasets are validated before ingestion; null values in rows are automatically converted to empty strings
- The script handles time period calculations for attributes based on parent entity time ranges and dataset years
- Categories and subcategories are checked for existence before creation to avoid duplicates
- In profiles mode, citizen entities must already exist in the system — if a citizen is not found, it is skipped with an error log
- If multiple citizen entities are found with the same name, a warning is logged and the first result is used
