import pytest
from unittest.mock import patch, MagicMock
from core.baseRunner import run_validation

class MockValidator:
    def validate_data(self, path):
        # We'll override this in specific tests
        return [], []

@patch("core.baseRunner.Path")
def test_run_validation_no_files_found(mock_path_class, capsys):
    # Setup mock Path.rglob to return an empty list
    mock_path_instance = MagicMock()
    mock_path_instance.rglob.return_value = []
    mock_path_class.return_value = mock_path_instance

    with pytest.raises(SystemExit) as excinfo:
        run_validation("mock_dir", MockValidator)
    
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "[INFO] No data.json files found" in captured.out

@patch("core.baseRunner.Path")
def test_run_validation_all_valid(mock_path_class, capsys):
    # Setup mock paths to return two file
    mock_path_instance = MagicMock()
    # Need to return an interable for rglob
    mock_path_instance.rglob.return_value = ["mock_data_1.json", "mock_data_2.json"]
    mock_path_class.return_value = mock_path_instance

    class SuccessValidator(MockValidator):
        def validate(self, path):
            return [], []

    with pytest.raises(SystemExit) as excinfo:
        run_validation("mock_dir", SuccessValidator)

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "All data is valid ✅" in captured.out

@patch("core.baseRunner.Path")
def test_run_validation_with_errors_and_warnings(mock_path_class, capsys):
    mock_path_instance = MagicMock()
    mock_path_instance.rglob.return_value = ["mock_data.json"]
    mock_path_class.return_value = mock_path_instance

    class FailureValidator(MockValidator):
        def validate_data(self, path):
            errors = [{
                "type": "error", "file": str(path), "row": 1, "column": "id", "message": "is wrong"
            }]
            warnings = [{
                "type": "warning", "file": str(path), "row": 2, "column": "name", "message": "is empty"
            }]
            return errors, warnings

    with pytest.raises(SystemExit) as excinfo:
        run_validation("mock_dir", FailureValidator)

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "1 errors found" in captured.out
    assert "1 warnings found" in captured.out
    assert "[ERROR]" in captured.out
    assert "[WARNING]" in captured.out
