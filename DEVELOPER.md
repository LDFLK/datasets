# Developer Guide

This guide provides instructions for using the utility scripts in this repository to manage and verify dataset ingestion into OpenGIN.

## Utility Scripts

### 1. Data Ingestion (`write_attributes.py`)

This script is responsible for traversing the local dataset directory structure and ingesting the data into OpenGIN. It creates the necessary entities (Categories, Datasets) and populates them with data from `data.json` files.

**Usage:**

```bash
python write_attributes.py --year <YEAR>
```

**Arguments:**

*   `--year`: The specific year directory to process (e.g., `2020`).

**Example:**

```bash
python write_attributes.py --year 2020
```

### 2. Data Verification (`verify.py`)

This script verifies that the datasets present in your local file system have been correctly ingested into OpenGIN. It compares the count of datasets per category between your local environment and the remote OpenGIN instance.

**Usage:**

```bash
python verify.py --year <YEAR>
```

**Arguments:**

*   `--year`: The specific year directory to verify (e.g., `2020`).

**Example:**

```bash
python verify.py --year 2020
```

**Output:**

The script will output a summary of the verification process, listing each category and the count of datasets found locally vs. remotely. Mismatches will be highlighted.

```text
Found 40 local datasets across 36 categories.
Searching OpenGIN for entities with kind.major='Dataset'...
Found 40 raw entities. Tracing parent categories...
Found 40 datasets in OpenGIN across 36 parent categories.

--- Detailed Verification ---
✅ Category 'annual_tourism_receipts': Local=1, Remote=1
...
✅ Verification SUCCESS: All local datasets accounted for.
```
