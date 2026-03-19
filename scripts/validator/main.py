from core.baseRunner import run_validation
from validators.tabular import TabularValidator
import sys

def main(file_path, validator):
    if validator == "tabular":
        run_validation(file_path, TabularValidator)
    else:
        print("Invalid validator")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <directory> <validator>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])