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

| Validator | Description              | Status  |
|-----------|--------------------------|---------|
| `tabular` | Validates tabular data   | ✅ Available |

> **Note:** Additional validators are currently under development.

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