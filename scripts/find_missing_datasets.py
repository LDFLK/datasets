#!/usr/bin/env python3
"""
Find empty data.json files and generate a missing datasets report.
Modified for Docusaurus - outputs to website/docs/missing-datasets.md
"""

import os
import argparse
from datetime import datetime
from pathlib import Path


class MissingDatasetFinder:
    def __init__(self, base_path: str):
        self.base_path = os.path.abspath(base_path)
        self.missing_datasets = {}  # {year: [{category: ..., path: ...}]}

    def find_missing(self):
        print(f"Crawling {self.base_path} for missing datasets...")

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
                    is_empty = True

                if is_empty:
                    self._record_missing(root, file_path)

    def _record_missing(self, root: str, file_path: str):
        rel_path = os.path.relpath(root, self.base_path)
        parts = rel_path.split(os.sep)

        year = "Unknown"
        if len(parts) > 0 and parts[0].isdigit() and len(parts[0]) == 4:
            year = parts[0]

        category = "Unknown"
        curr = root
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

    def generate_report(self, output_file: str = None) -> str:
        """Generate the missing datasets report as markdown"""
        report_lines = []

        # Docusaurus front matter
        report_lines.append("---")
        report_lines.append("sidebar_position: 4")
        report_lines.append("title: Missing Datasets Report")
        report_lines.append("---")
        report_lines.append("")

        if not self.missing_datasets:
            report_lines.append("# Missing Datasets Report")
            report_lines.append("")
            report_lines.append("No missing datasets found! All data.json files are populated.")
        else:
            report_lines.append("# Missing Datasets Report")
            report_lines.append("")
            report_lines.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            report_lines.append("This report lists all datasets that have empty `data.json` files and need to be populated.")
            report_lines.append("")

            total_missing = sum(len(items) for items in self.missing_datasets.values())
            report_lines.append(f"**Total missing datasets:** {total_missing}")
            report_lines.append("")

            for year in sorted(self.missing_datasets.keys(), reverse=True):
                items = self.missing_datasets[year]
                count = len(items)

                report_lines.append(f"## Year: {year} (Missing: {count})")
                report_lines.append("")
                report_lines.append("| Category | Relative Path | Status |")
                report_lines.append("| :--- | :--- | :--- |")

                for item in sorted(items, key=lambda x: x['category']):
                    cat = item['category']
                    path = item['path']
                    report_lines.append(f"| **{cat}** | `{path}` | Empty `data.json` |")

                report_lines.append("")

        full_report = "\n".join(report_lines)

        if output_file:
            try:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(full_report)
                print(f"Report written to: {output_file}")
            except Exception as e:
                print(f"Error writing to file: {e}")

        return full_report


def main():
    """Main function"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_path = project_root / "data"
    output_file = project_root / "website" / "docs" / "missing-datasets.md"

    parser = argparse.ArgumentParser(description="Find empty data.json files.")
    parser.add_argument("--dir", type=str, default=str(data_path), help="Data directory path")
    parser.add_argument("--output-file", type=str, default=str(output_file), help="Path to save the markdown report")

    args = parser.parse_args()

    if os.path.exists(args.dir):
        finder = MissingDatasetFinder(args.dir)
        finder.find_missing()
        report = finder.generate_report(args.output_file)

        # Print summary to console
        if finder.missing_datasets:
            total = sum(len(items) for items in finder.missing_datasets.values())
            print(f"Found {total} missing datasets")
        else:
            print("No missing datasets found!")
    else:
        print(f"Error: Directory '{args.dir}' not found.")


if __name__ == "__main__":
    main()
