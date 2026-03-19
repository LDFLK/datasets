from core.baseValidator import BaseValidator
import json
from jsonschema import validate, ValidationError
from collections import Counter
from utils.utils import Utils

class TabularValidator(BaseValidator):
    def __init__(self):
        with open("./models/tabularSchema.json") as f:
            self.schema = json.load(f)

    def validate(self, file_path):
        errors = []
        warnings = []

        # Load JSON
        try:
            with open(file_path) as f:
                data = json.load(f)
        except Exception as e:
            return [f"[ERROR] {file_path}: Invalid JSON ({e})"], []

        # 1. Schema validation
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            return [f"[ERROR] {file_path}: Schema error → {e.message}"], []

        # 2. Custom validation
        columns = data["columns"]
        rows = data["rows"]

        num_cols = len(columns)

        # Check duplicate columns
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

        # Check rows and columns mismatches
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

        # Check data types
        # if the column's first value starts from a sepcific data type, all the values down to the end on that column should be of the same data type
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

        # Check for empty values (missing values)
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
        
        # Check for value overflow (temporary fix for opengin system)
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

        return errors, warnings
   

