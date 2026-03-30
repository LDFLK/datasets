# Data Validator Program

A command-line tool for validating datasets using configurable validator types.

---

## Getting Started

### Prerequisites

- Python 3.x
- `pip` and `venv`

### Local Setup

```bash
# Navigate to the project directory
cd scripts/validator

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Program

```bash
python main.py <path-to-dataset-directory> <validator-type>
```

**Example:**

```bash
python main.py ../../data/statistics tabular
```

---

## Supported Validators

| Validator | Description | Validations | Status |
|-----------|-------------|-------------|--------|
| `tabular` | Validates tabular data | `schema-validation` — Checks that the data conforms to a predefined schema (structures, types, constraints)<br><br>`duplicate-columns` — Detects columns that appear more than once<br><br>`row-column-mismatch` — Detects rows where the number of fields does not match the number of defined columns<br><br>`data-types-mismatch` — Identifies values that do not match the expected data type for their column (e.g. text in a numeric field)<br><br>`empty-values` — Flag cells that are null, blank, or contain only whitespace where a value is required<br><br>`value-overflow` — Catches values that exceed the maximum allowed length or numeric range for their column | ✅ Available |

---

## Project Structure

```
scripts/validator/
│
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
│
├── core/
│   ├── baseRunner.py     # Base runner logic
│   └── baseValidator.py  # Base validator interface
│
├── models/
│   └── tabularSchema.json  # Schema definition for tabular validation
│
├── utils/
│   └── utils.py          # Shared utility functions
│
└── validators/
    └── tabular.py        # Tabular validator implementation
```