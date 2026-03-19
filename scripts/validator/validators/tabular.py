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
        errors = []
        if len(columns) != len(set(columns)):
            column_counts = Counter(columns)
            duplicates = [col for col, count in column_counts.items() if count > 1]
            if duplicates:
                errors.append(
                    {
                        "type": "error",
                        "file": file_path,
                        "row": None,
                        "column": duplicates,
                        "message": f"Duplicate column names found: {', '.join(duplicates)}",
                    }
                )
        return errors

    def _check_row_column_mismatches(self, file_path, rows, num_cols):
        errors = []
        for i, row in enumerate(rows):
            if len(row) != num_cols:
                errors.append(
                    {
                        "type": "error",
                        "file": file_path,
                        "row": i,
                        "column": None,
                        "message": f"has {len(row)} value(s), expected {num_cols} value(s)",
                    }
                )
        return errors

    def _check_data_types(self, file_path, rows, columns):
        errors = []
        if not rows:
            return errors
            
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                expected_type = type(rows[0][j])
                if expected_type is str:    
                    if not isinstance(value, str):
                        errors.append(
                            {
                                "type": "error",
                                "file": file_path,
                                "row": i,
                                "column": columns[j],
                                "message": f"has {value} ({type(value).__name__}), expected {expected_type.__name__}",
                            }
                        )
                elif expected_type is int:
                    if not isinstance(value, int):
                        errors.append(
                            {
                                "type": "error",
                                "file": file_path,
                                "row": i,
                                "column": columns[j],
                                "message": f"has {value} ({type(value).__name__}), expected {expected_type.__name__}",
                            }
                        )
                elif expected_type is float:
                    if not isinstance(value, (float, int)):
                        errors.append(
                            {
                                "type": "error",
                                "file": file_path,
                                "row": i,
                                "column": columns[j],
                                "message": f"has {value} ({type(value).__name__}), expected {expected_type.__name__}",
                            }
                        )
        return errors

    def _check_empty_values(self, file_path, rows, columns):
        warnings = []
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                if value is None or value == "":
                    warnings.append(
                        {
                            "type": "warning",
                            "file": file_path,
                            "row": i,
                            "column": columns[j],
                            "message": "has empty value",
                        }
                    )
        return warnings

    def _check_value_overflow(self, file_path, rows, columns):
        warnings = []
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                if isinstance(value, int):
                    if not Utils.fits_in_int32(value):
                        warnings.append(
                            {
                                "type": "warning",
                                "file": file_path,
                                "row": i,
                                "column": columns[j],
                                "message": f"has {value} ({type(value).__name__}), this is a big integer in postgres , consider when inserting into the database (postgres has 32 bit integer limit)",
                            }
                        )
        return warnings

    def validate(self, file_path):
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
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            return [f"[ERROR] {file_path}: Schema error → {e.message}"], []

        # 2. Custom validation
        columns = data.get("columns", [])
        rows = data.get("rows", [])
        num_cols = len(columns)

        # errors --------
        errors.extend(self._check_duplicate_columns(file_path, columns))
        errors.extend(self._check_row_column_mismatches(file_path, rows, num_cols))
        errors.extend(self._check_data_types(file_path, rows, columns))
        
        # warnings --------
        warnings.extend(self._check_empty_values(file_path, rows, columns))
        warnings.extend(self._check_value_overflow(file_path, rows, columns))

        return errors, warnings
   

