#!/usr/bin/env python3
"""
Generate ZIP files for datasets.
Modified for Docusaurus - outputs to website/static/downloads/
Note: HTML generation is now handled by React DataBrowser component.
"""

import os
import zipfile
from pathlib import Path


def create_zip_for_section(section_path: str, section_name: str, output_dir: str) -> str:
    """Create a ZIP file for a specific section"""
    os.makedirs(output_dir, exist_ok=True)

    zip_filename = f"{section_name.replace(' ', '_').replace('(', '').replace(')', '')}_Data.zip"
    zip_path = os.path.join(output_dir, zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(section_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    # Create relative path from the section root
                    arcname = os.path.relpath(file_path, section_path)
                    zipf.write(file_path, arcname)

    return zip_filename


def generate_all_zips(data_path: str, output_dir: str) -> dict:
    """Generate ZIP files for all major sections (years)"""
    zip_files = {}

    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found!")
        return zip_files

    os.makedirs(output_dir, exist_ok=True)

    # Generate ZIP for each year
    for year in sorted(os.listdir(data_path)):
        year_path = os.path.join(data_path, year)
        if os.path.isdir(year_path):
            zip_filename = create_zip_for_section(year_path, year, output_dir)
            zip_files[year] = zip_filename
            print(f"  Generated {output_dir}/{zip_filename}")

    return zip_files


def count_datasets(data_path: str) -> int:
    """Count total datasets"""
    count = 0
    for root, dirs, files in os.walk(data_path):
        if "data.json" in files:
            count += 1
    return count


def main():
    """Main function to generate ZIP files"""
    print("Generating ZIP files for downloads...")

    # Determine paths relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_path = project_root / "data"
    output_dir = project_root / "website" / "static" / "downloads"

    zip_files = generate_all_zips(str(data_path), str(output_dir))
    dataset_count = count_datasets(str(data_path))

    print(f"\nGenerated {len(zip_files)} ZIP files")
    print(f"Total datasets: {dataset_count}")


if __name__ == "__main__":
    main()
