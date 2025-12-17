import json
import os
import shutil

# Create a dummy JSON file
test_data = {
    "columns": ["A", "B"],
    "rows": [
        ["Row1", 10],
        ["Row2", 20],
        ["Row3", 30]
    ]
}

test_file = "test_data.json"

with open(test_file, 'w') as f:
    json.dump(test_data, f, indent=4)

print("Original content:")
with open(test_file, 'r') as f:
    print(f.read())

# Run the linter logic (importing the function would be better, but for quick verify I'll just run the script)
# Actually, I'll import the function since I wrote it in the same dir
import linter

print("\nRunning linter...")
linter.format_json_file(test_file)

print("\nFormatted content:")
with open(test_file, 'r') as f:
    content = f.read()
    print(content)

# Verification
expected_snippet = '        ["Row1", 10]'
if expected_snippet in content:
    print("\nSUCCESS: Row is compacted.")
else:
    print("\nFAILURE: Row is not compacted.")

# Cleanup
os.remove(test_file)
