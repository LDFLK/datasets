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

**Verification Logic:**

The verification process ensures accuracy through an exact comparison for the specified year:

1.  **Local Discovery**: The script identifies all categories present in your local file system for the specified `--year`.
2.  **Remote Resolution**: It queries OpenGIN to find all dataset entities. It filters these remote datasets by the `created` date to include only those matching the specified year.
3.  **Comparision**:
    *   **Category-wise Check**: It iterates through each category and confirms that the number of local files exactly matches the number of remote datasets for that year.
    *   **Total Count Check**: It also verifying that the *total* number of local datasets matches the *total* number of remote datasets found for that year.

    > [!NOTE]
    > **Exact Matching:**
    > Since the script now filters both local and remote datasets by the specified year (e.g., `--year 2021`), we expect an **exact count match** (e.g., `Local=1, Remote=1`). Any discrepancy indicates a missing or extra dataset for that specific year.

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

### 3. Missing Dataset Detection (`find_missing_datasets.py`)

This script scans your local data directory to identify "empty" datasets (i.e., `data.json` files that exist but have no content). This is useful for tracking data coverage and identifying which years or categories still need population.

**Features:**
- **Recursive Scan**: Crawls the entire data directory structure.
- **Empty Detection**: identifying `data.json` files that are empty or whitespace-only.
- **Pretty Output**: Generates a formatted Markdown table in the terminal (uses `rich` if installed).
- **File Export**: Can save the report to a Markdown file with Jekyll front matter for documentation sites.

**Usage:**

```bash
# Print report to terminal
python find_missing_datasets.py

# Save report to a file (e.g. for docs)
python find_missing_datasets.py --output-file docs/missing_datasets.md
```

**Arguments:**

*   `--dir`: The base data directory to scan (default: `data/statistics`).
*   `--output-file`: Optional path to write the generated markdown report. if provided, it adds Jekyll front matter (`layout: default`) to the file.

**Example Output:**

```text
# 🚨 Missing Datasets Report
Generated on: 2025-12-23 22:45:05

## 📅 Year: 2024 (Missing: 21)
| Category | Relative Path | Status |
| :--- | :--- | :--- |
| **annual_tourism_receipts** | `2024/...` | 🔴 Empty `data.json` |
...
```

## Limitations

> [!WARNING]
> **Type Inference Issues**
> There is a known issue in OpenGIN where type inference can be incorrect for certain numeric values (e.g., distinguishing between float/int or handling large numbers).
>
> **Known Issues:**
> - [Issue #409: Type Inference Logic Update](https://github.com/LDFLK/OpenGIN/issues/409)
>
> **Workaround:**
> As a temporary workaround, please use **decimal point values** in the first row of your dataset to enforce correct type inference.
> - **Overflowing Case:** Always prefer `float` for large numbers until this is officially supported.
