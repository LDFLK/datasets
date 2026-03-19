import sys
from pathlib import Path
from utils.utils import Utils

def run_validation(file_path, validator):
    validator = validator()
    all_errors = []
    all_warnings = []

    paths = list(Path(file_path).rglob("data.json"))

    if not paths:
        print("[INFO] No data.json files found")
        sys.exit(0)

    for path in paths:
        errors, warnings = validator.validate(path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    if all_errors:
        print(f" - {len(all_errors)} errors found")
        for error in all_errors:
            print(Utils.format_issue(error))

    if all_warnings:
        print(f" - {len(all_warnings)} warnings found")
        for warning in all_warnings:
            print(Utils.format_issue(warning))

    if not all_errors and not all_warnings:
        print("All data valid ✅")

    sys.exit(1 if all_errors else 0)
