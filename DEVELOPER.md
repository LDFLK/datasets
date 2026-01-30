# Developer Guide

This guide describes the utility scripts in this repository for managing data, ingesting into OpenGIN, and building the website.

## Data Ingestion

Ingestion is handled by the `ingestion` module, which reads YAML manifest files and pushes categories and datasets into OpenGIN. For full setup (environment variables, OpenGIN services, backups), see [ingestion/README.md](ingestion/README.md).

### Ingestion Script (`ingestion/ingest_data_yaml.py`)

The script traverses a YAML data hierarchy file (e.g. under `data/statistics/<year>/`), resolves existing entities (governments, ministers, departments) in OpenGIN, creates categories and subcategories as needed, and adds each dataset as an attribute on the appropriate parent. Dataset content is read from `data.json` in the paths referenced by the YAML.

**Usage:**

```bash
# From project root
python -m ingestion.ingest_data_yaml <yaml_file> [--year YEAR]
```

**Arguments:**

- `yaml_file` (required): Path to the YAML file (e.g. `data/statistics/2020/data_hierarchy_2020.yaml`).
- `--year` (optional): Override the year derived from the filename.

**Example:**

```bash
python -m ingestion.ingest_data_yaml data/statistics/2020/data_hierarchy_2020.yaml
python -m ingestion.ingest_data_yaml data/statistics/2024/data_hierarchy_2024.yaml --year 2024
```

**Prerequisites:**

- OpenGIN Read and Ingestion services running.
- Environment variables set: `READ_BASE_URL`, `INGESTION_BASE_URL` (see `ingestion/.env.template`).

---

## Utility Scripts (`scripts/`)

These scripts are intended to be run from the **project root** (parent of `scripts/`).

### 1. Data Index for Website (`generate_data_index.py`)

Scans the `data/` tree and builds a JSON index of all datasets (with hierarchy, paths, empty flag, etc.) for the React DataBrowser. Output is written to `website/src/data/datasetIndex.json`.

**Usage:**

```bash
python scripts/generate_data_index.py
```

No arguments. Uses project layout to resolve `data/` and output path.

---

### 2. ZIP Downloads (`update_dataset_index.py`)

Creates one ZIP per year containing all JSON files under that year in `data/`. Output goes to `website/static/downloads/` for the website.

**Usage:**

```bash
python scripts/update_dataset_index.py
```

---

### 3. Prebuild Orchestrator (`prebuild.py`)

Runs the main build steps for the website in order:

1. `generate_data_index.py` – dataset index for the DataBrowser.
2. `update_dataset_index.py` – year ZIPs in `website/static/downloads/`.
3. `find_missing_datasets.py` – missing-datasets report.
4. Copy of assets from `docs/assets/` to `website/static/`.
5. Copy of existing downloads from `docs/downloads/` if present.

**Usage:**

```bash
python scripts/prebuild.py
```

Run this before building or deploying the site so the index, ZIPs, and docs are up to date.

---

### 4. JSON Linter (`linter.py`)

Formats dataset JSON files so that each row in the `rows` array is on a single line (columns keep indentation). Only touches files that look like dataset JSON (dict with `rows` list).

**Usage:**

```bash
python scripts/linter.py <directory>
```

**Example:**

```bash
python scripts/linter.py data
```

---

### 5. Other Scripts

- **`fix_2020_names.py`**, **`replicate_flat_structure.py`**: One-off/migration helpers; see script docstrings or comments.
- **`sources/`**: Scripts for fetching or generating source metadata (e.g. `fetch_sources.py`, `generate_readme.py`, `rename_files.py`). Use as needed for source and README upkeep.

---

## Limitations

> [!WARNING]
> **Type inference in OpenGIN**
> OpenGIN may infer types incorrectly for some numeric values (e.g. float vs int, or large numbers).
>
> **Workaround:** Use decimal values in the first row of the dataset where appropriate so the inferred type is correct.

---

## Git Large File Storage (LFS)

This repository uses [Git LFS](https://git-lfs.github.com/) for large files (e.g. PDFs under `data/sources/`).

**Setup:**

1. Install Git LFS:
   ```bash
   brew install git-lfs   # macOS
   sudo apt install git-lfs  # Ubuntu
   ```
2. Initialize in the repo:
   ```bash
   git lfs install
   ```

**When adding large files (e.g. PDFs):**

```bash
git lfs track "data/sources/**/*.pdf"
git add .gitattributes
```

**Policy:**

- **Mandatory:** Files larger than **100 MB** must be tracked with LFS (GitHub limit).
- **Recommended:** Use LFS for binary files (PDFs, images, archives) larger than **50 MB**.

**If push fails with “Large files detected”:**

1. The large file may have been committed as a normal object in an earlier commit.
2. Migrate to LFS and rewrite history, then force-push:
   ```bash
   git lfs migrate import --include="path/to/large/files/*.pdf" --everything
   ```
