from core.baseValidator import BaseValidator
import json
from jsonschema import validate, ValidationError
from collections import Counter
from utils.utils import Utils
from pathlib import Path

class TabularValidator(BaseValidator):
    def __init__(self):
        with open(Path(__file__).parent / "../models/tabularSchema.json") as f:
            self.schema = json.load(f)

    def _check_duplicate_columns(self, file_path, columns):
        if len(columns) != len(set(columns)):
            column_counts = Counter(columns)
            duplicates = [col for col, count in column_counts.items() if count > 1]
            if duplicates:
                return [
                    {
                        "type": "error",
                        "file": file_path,
                        "row": None,
                        "column": duplicates,
                        "message": f"Duplicate column names found: {', '.join(duplicates)}",
                    }
                ]
        return []

    def _check_row_column_mismatch(self, file_path, index, row, num_cols):
        if len(row) != num_cols:
            return [{
            "type": "error",
            "file": file_path,
            "row": index,
            "column": None,
            "message": f"has {len(row)} value(s), expected {num_cols} value(s)",
        }]
        return []   

    def _check_data_types(self, file_path, index, row, first_row, columns):
        errors = []
        for j, value in enumerate(row):
            expected_type = type(first_row[j])
            if expected_type is float:
                allowed_types = (float, int)
                expected_msg = "float or whole number"
            else:
                allowed_types = (expected_type)
                expected_msg = expected_type.__name__
            
            if not isinstance(value, allowed_types):
                errors.append({
                    "type": "error",
                    "file": file_path,
                    "row": index,
                    "column": columns[j],
                    "message": f"has {value} ({type(value).__name__}), expected {expected_msg}",
                })
        return errors

    def _check_empty_values(self, file_path, index, row, columns):
        warnings = []
        for j, value in enumerate(row):
            str_value = str(value).strip() if value is not None else ""
            if str_value == "":
                warnings.append({
                            "type": "warning",
                            "file": file_path,
                            "row": index,
                            "column": columns[j],
                            "message": "has empty value",
                })
        return warnings

    def _check_value_overflow(self, file_path, index, row, columns):
        warnings = []
        for j, value in enumerate(row):
            if isinstance(value, int):
                if not Utils.fits_in_int32(value):
                        warnings.append({
                                "type": "warning",
                                "file": file_path,
                                "row": index,
                                "column": columns[j],
                                "message": f"has {value} ({type(value).__name__}), which is a BIGINT as it exceeds PostgreSQL's 32-bit integer limit.",
                        })
        return warnings

    def validate_data(self, file_path):
        errors = []
        warnings = []

        # Load JSON
        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            return [f"[ERROR] {file_path}: Invalid JSON ({e})"], []

        # 1. Schema validation
        try:
            # imported validate function from the jsonschema library
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            errors.append({
                "type": "error",
                "file": file_path,
                "row": None,
                "column": None,
                "message": f"Schema error → {e.message}"
            })
            return errors, warnings

        # 2. Custom validation
        columns = data.get("columns", [])
        rows = data.get("rows", [])
        num_cols = len(columns)

        if not rows or not columns:
            if not rows:
                message = "No rows found"
            elif not columns:
                message = "No columns found"
            else:
                message = "No rows or columns found"

            errors.append({
                    "type": "error",
                    "file": file_path,
                    "row": rows if rows else None,
                    "column": columns if columns else None,
                    "message": message
                })
            print(errors)
            return errors, warnings

        errors.extend(self._check_duplicate_columns(file_path, columns))

        for index, row in enumerate(rows, start=1):
            errors.extend(self._check_row_column_mismatch(file_path, index, row, num_cols))
            warnings.extend(self._check_empty_values(file_path, index, row, columns))
            warnings.extend(self._check_value_overflow(file_path, index, row, columns))
            errors.extend(self._check_data_types(file_path, index, row, rows[0], columns))

        return errors, warnings
   

