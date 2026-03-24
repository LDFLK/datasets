from utils.utils import Utils

def test_format_issue_with_row_and_single_column():
    issue = {
        "type": "error",
        "file": "data.json",
        "row": 5,
        "column": "name",
        "message": "is invalid"
    }
    result = Utils.format_issue(issue)
    assert result == "[ERROR] data.json: Row 5, Column 'name' is invalid"

def test_format_issue_with_row_and_multiple_columns():
    issue = {
        "type": "warning",
        "file": "data.csv",
        "row": 10,
        "column": ["age", "dob"],
        "message": "have conflicting values"
    }
    result = Utils.format_issue(issue)
    assert result == "[WARNING] data.csv: Row 10, Columns [age, dob] have conflicting values"

def test_format_issue_without_row_and_column():
    issue = {
        "type": "error",
        "file": "config.json",
        "message": "File not found or unreadable"
    }
    result = Utils.format_issue(issue)
    assert result == "[ERROR] config.json:  File not found or unreadable"

def test_format_issue_without_row_with_column():
    issue = {
        "type": "error",
        "file": "schema.json",
        "column": ["header1", "header2"],
        "message": "Duplicate columns"
    }
    result = Utils.format_issue(issue)
    assert result == "[ERROR] schema.json: Columns [header1, header2] Duplicate columns"

def test_fits_in_int32():
    # Boundary values
    assert Utils.fits_in_int32(-2_147_483_648) is True
    assert Utils.fits_in_int32(2_147_483_647) is True
    
    # Internal values
    assert Utils.fits_in_int32(0) is True
    assert Utils.fits_in_int32(1000) is True
    assert Utils.fits_in_int32(-50000) is True

    # Out of bounds
    assert Utils.fits_in_int32(-2_147_483_649) is False
    assert Utils.fits_in_int32(2_147_483_648) is False
    assert Utils.fits_in_int32(10_000_000_000) is False
