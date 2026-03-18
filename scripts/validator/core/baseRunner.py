from validator.validators.tabular import TabularValidator

def run_validation(file_path):
    validator = TabularValidator()
    return validator.validate(file_path)