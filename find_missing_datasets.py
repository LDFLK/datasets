import os
import argparse
from datetime import datetime

class MissingDatasetFinder:
    def __init__(self, base_path):
        self.base_path = os.path.abspath(base_path)
        self.missing_datasets = {} # {year: [{category: ..., path: ...}]}

    def find_missing(self):
        print(f"Crawling {self.base_path} for missing datasets...\n")
        
        for root, dirs, files in os.walk(self.base_path):
            if 'data.json' in files:
                file_path = os.path.join(root, 'data.json')
                
                is_empty = False
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            is_empty = True
                except Exception:
                    # Treat read errors as empty/missing for safety
                    is_empty = True
                
                if is_empty:
                    self._record_missing(root, file_path)

    def _record_missing(self, root, file_path):
        # Extract Year (first folder under base_path)
        rel_path = os.path.relpath(root, self.base_path)
        parts = rel_path.split(os.sep)
        
        year = "Unknown"
        if len(parts) > 0:
            # Check if first part looks like a year
            if parts[0].isdigit() and len(parts[0]) == 4:
                year = parts[0]

        # Extract Category
        category = "Unknown"
        curr = root
        # Try to find nearest AS_CATEGORY
        while curr.startswith(self.base_path) and curr != self.base_path:
            dirname = os.path.basename(curr)
            if dirname.endswith("(AS_CATEGORY)"):
                category = dirname.replace("(AS_CATEGORY)", "")
                break
            curr = os.path.dirname(curr)
        
        if category == "Unknown":
            category = os.path.basename(root)

        if year not in self.missing_datasets:
            self.missing_datasets[year] = []
        
        self.missing_datasets[year].append({
            "category": category,
            "path": rel_path
        })

    def print_report(self, output_file=None):
        # Build the Markdown report as a string first
        report_lines = []
        
        if not self.missing_datasets:
            report_lines.append("✅ No missing datasets found! All data.json files are populated.")
        else:
            report_lines.append("# 🚨 Missing Datasets Report")
            report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")

            # Sort years descending
            for year in sorted(self.missing_datasets.keys(), reverse=True):
                items = self.missing_datasets[year]
                count = len(items)
                
                report_lines.append(f"## 📅 Year: {year} (Missing: {count})")
                report_lines.append("")
                report_lines.append("| Category | Relative Path | Status |")
                report_lines.append("| :--- | :--- | :--- |")
                
                for item in sorted(items, key=lambda x: x['category']):
                    cat = item['category']
                    path = item['path']
                    report_lines.append(f"| **{cat}** | `{path}` | 🔴 Empty `data.json` |")
                
                report_lines.append("\n")

        full_report = "\n".join(report_lines)

        if output_file:
            try:
                # Add Jekyll Front Matter
                front_matter = "---\nlayout: default\ntitle: Missing Datasets Report\n---\n\n"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(front_matter + full_report)
                print(f"Report written to: {output_file}")
            except Exception as e:
                print(f"Error writing to file: {e}")

        # Try to use rich for pretty printing (always print to console too)
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            console = Console()
            md = Markdown(full_report)
            console.print(md)
        except ImportError:
            # Fallback to standard print
            print("To see a prettier output, install 'rich': pip install rich\n")
            print(full_report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find empty data.json files.")
    parser.add_argument("--dir", type=str, default="data", help="Data directory path")
    parser.add_argument("--output-file", type=str, help="Path to save the markdown report (e.g. docs/missing_datasets.md)", default=None)
    
    args = parser.parse_args()
    
    if os.path.exists(args.dir):
        finder = MissingDatasetFinder(args.dir)
        finder.find_missing()
        finder.print_report(args.output_file)
    else:
        print(f"Error: Directory '{args.dir}' not found.")
