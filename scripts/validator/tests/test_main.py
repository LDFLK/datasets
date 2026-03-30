from unittest.mock import patch
from main import main

@patch("main.sys.exit")
@patch("main.run_validation")
def test_main_valid_validator(mock_run_validation, mock_sys_exit):
    main("some_dir", "tabular")
    mock_run_validation.assert_called_once()
    assert mock_sys_exit.call_count == 0

@patch("main.sys.exit")
@patch("main.print")
def test_main_invalid_validator(mock_print, mock_sys_exit):
    main("some_dir", "unknown_validator")
    mock_print.assert_called_with("Invalid validator")
    mock_sys_exit.assert_called_with(1)
