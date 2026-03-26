import pytest
import json
from unittest.mock import patch, mock_open
from validators.tabular import TabularValidator

@pytest.fixture
def tabular_validator():
    return TabularValidator()

def test_check_duplicate_columns(tabular_validator):
    # No duplicates
    errors = tabular_validator._check_duplicate_columns("mock.json", ["id", "name", "age"])
    assert len(errors) == 0

    # Duplicates exist
    errors = tabular_validator._check_duplicate_columns("mock.json", ["id", "name", "id", "age", "name"])
    assert len(errors) == 1
    assert errors[0]["type"] == "error"
    assert "Duplicate column names found" in errors[0]["message"]
    assert set(errors[0]["column"]) == {"id", "name"}

def test_check_row_column_mismatch(tabular_validator):
    # Match
    errors = tabular_validator._check_row_column_mismatch("mock.json", 0, [1, "test"], 2)
    assert len(errors) == 0

    # Mismatch
    errors = tabular_validator._check_row_column_mismatch("mock.json", 1, [1, "test", "extra"], 2)
    assert len(errors) == 1
    assert errors[0]["type"] == "error"
    assert errors[0]["row"] == 1
    assert "has 3 value(s), expected 2 value(s)" in errors[0]["message"]

def test_check_data_types(tabular_validator):
    columns = ["id", "score", "name"]
    first_row = [1, 5.5, "Alice"] # int, float, str
    
    # Valid row matching first row types
    row_valid = [2, 10.0, "Bob"]
    errors = tabular_validator._check_data_types("mock.json", 1, row_valid, first_row, columns)
    assert len(errors) == 0

    # Allow int for float columns
    row_valid_int_for_float = [3, 10, "Charlie"]
    errors = tabular_validator._check_data_types("mock.json", 2, row_valid_int_for_float, first_row, columns)
    assert len(errors) == 0

    # Invalid row
    row_invalid = ["four", "five", 6]
    errors = tabular_validator._check_data_types("mock.json", 3, row_invalid, first_row, columns)
    assert len(errors) == 3
    assert "expected int" in errors[0]["message"]
    assert "expected float or whole number" in errors[1]["message"]
    assert "expected str" in errors[2]["message"]

def test_check_empty_values(tabular_validator):
    columns = ["id", "name", "notes"]
    row_empty = [1, "", None]
    warnings = tabular_validator._check_empty_values("mock.json", 0, row_empty, columns)
    assert len(warnings) == 2
    assert warnings[0]["column"] == "name"
    assert warnings[0]["message"] == "has empty value"
    assert warnings[1]["column"] == "notes"
    assert warnings[1]["message"] == "has empty value"

def test_check_value_overflow(tabular_validator):
    columns = ["id", "big_num"]
    row = [1, 2_147_483_648] # Over max int32
    warnings = tabular_validator._check_value_overflow("mock.json", 0, row, columns)
    assert len(warnings) == 1
    assert warnings[0]["column"] == "big_num"
    assert "which is a BIGINT as it exceeds PostgreSQL's 32-bit integer limit." in warnings[0]["message"]

@patch("validators.tabular.open")
def test_validate_invalid_json(mock_file_open, tabular_validator):
    mock_file_open.side_effect = FileNotFoundError()
    errors, warnings = tabular_validator.validate_data("missing.json")
    assert len(errors) == 1
    assert len(warnings) == 0
    assert "Invalid JSON" in errors[0]

@patch("validators.tabular.open", new_callable=mock_open, read_data='{"invalid": "schema"}')
def test_validate_schema_error(_mock_file_open, tabular_validator):
    errors, warnings = tabular_validator.validate_data("schema_error.json")
    assert len(errors) == 1
    assert len(warnings) == 0
    assert "Schema error → 'columns' is a required property" in errors[0]["message"]

@patch("validators.tabular.open", new_callable=mock_open)
def test_validate_success(mock_file_open, tabular_validator):
    valid_data = {
        "columns": ["id", "name"],
        "rows": [
            [1, "Alice"],
            [2, "Bob"]
        ]
    }
    mock_file_open.return_value.read.return_value = json.dumps(valid_data)
    errors, warnings = tabular_validator.validate_data("valid.json")
    assert len(errors) == 0
    assert len(warnings) == 0

@patch("validators.tabular.open", new_callable=mock_open)
def test_validate_with_warnings_and_errors(mock_file_open, tabular_validator):
    invalid_data = {
        "columns": ["id", "id", "name"],
        "rows": [
            [1, 1, "Alice"],
            [2, "not-int", "Bob"]
        ]
    }
    mock_file_open.return_value.read.return_value = json.dumps(invalid_data)
    errors, warnings = tabular_validator.validate_data("invalid.json")
    
    # Should have duplicate column error, and type mismatch error for 'not-int'
    assert len(errors) >= 2 
