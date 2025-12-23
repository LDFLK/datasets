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
