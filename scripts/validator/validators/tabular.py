from validator.core.baseValidator import BaseValidator
import json
from jsonschema import validate, ValidationError

class TabularValidator(BaseValidator):
    def __init__(self):
        with open("./models/tabularSchema.json") as f:
            self.schema = json.load(f)
    
    def validate(self, file_path):
        errors = []

        # Load JSON
        try:
            with open(file_path) as f:
                data = json.load(f)
        except Exception as e:
            return [f"[ERROR] {file_path}: Invalid JSON ({e})"]

        # 1. Schema validation
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            return [f"[ERROR] {file_path}: Schema error → {e.message}"]

        # 2. Custom validation
        columns = data["columns"]
        rows = data["rows"]

        num_cols = len(columns)

        # Check duplicate columns
        if len(columns) != len(set(columns)):
            errors.append(f"[ERROR] {file_path}: Duplicate column names found")

        # Check rows and columns mismatches
        for i, row in enumerate(rows):
            if len(row) != num_cols:
                errors.append(
                    f"[ERROR] {file_path}: Row {i} has {len(row)} value(s), expected {num_cols} value(s)"
                )
        
        # Check data types
        # if the column's first value starts from a sepcific data type, all the values down to the end on that column should be of the same data type
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                expected_type = type(rows[0][j])
                if not isinstance(value, expected_type):
                    errors.append(
                        f"[ERROR] {file_path}: Row {i}, Column '{columns[j]}' has {value} ({type(value).__name__}), expected {expected_type.__name__}"
                    )
        
        # Check for empty values (missing values)
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                if value is None or value == "":
                    errors.append(
                        f"[WARNING] {file_path}: Row {i}, Column '{columns[j]}' has empty value"
                    )
        return errors
