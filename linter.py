import json
import os
import sys

def format_json_file(file_path):
    """
    Formats a JSON file such that each row in the 'rows' list is on a single line.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if the structure matches expected format
        if not isinstance(data, dict) or 'rows' not in data or not isinstance(data['rows'], list):
            # If not matching the specific structure, just dump with default indent
            # But the requirement is specifically for the 'rows' structure.
            # If it's a different file, we might want to skip or just standard format.
            # For now, let's assume we only touch files that look like the target data.
            return

        # Custom formatting
        # We want to construct the string manually to ensure specific formatting
        
        # Format columns
        columns_str = json.dumps(data.get('columns', []), indent=4)
        
        # Format rows
        rows = data['rows']
        formatted_rows = []
        for row in rows:
            # Dump each row as a compact string
            formatted_rows.append("        " + json.dumps(row))
        
        rows_str = ",\n".join(formatted_rows)
        
        # Construct the final JSON string
        # We assume 'columns' comes first then 'rows'
        
        final_json = "{\n"
        if 'columns' in data:
            final_json += '    "columns": ' + "\n".join(["    " + line for line in columns_str.splitlines()]).strip() + ",\n"
        
        final_json += '    "rows": [\n'
        final_json += rows_str + "\n"
        final_json += "    ]\n"
        final_json += "}\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_json)
            
        print(f"Formatted: {file_path}")

    except Exception as e:
        print(f"Error formatting {file_path}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python linter.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    
    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a directory")
        sys.exit(1)

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                format_json_file(file_path)

if __name__ == "__main__":
    main()
