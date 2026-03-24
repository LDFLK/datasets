import pytest
from core.baseValidator import BaseValidator

def test_base_validator_validate_raises_not_implemented():
    validator = BaseValidator()
    with pytest.raises(NotImplementedError):
        validator.validate("some_file.json")
