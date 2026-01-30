#!/usr/bin/env python3
"""
Generate JSON index of all datasets for the React DataBrowser component.
Outputs to website/src/data/datasetIndex.json
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def clean_name(name: str) -> str:
    """Clean folder names for display"""
    name = name.replace('(AS_CATEGORY)', '')
    name = name.replace('(government)', '')
    name = name.replace('(citizen)', '')
    name = name.replace('(minister)', '')
    name = name.replace('(department)', '')
    name = name.replace('_', ' ')
    return name.strip().title()


def categorize_dataset(dataset_name: str) -> str:
    """Categorize a dataset based on its name"""
    name_lower = dataset_name.lower()

    # Tourism datasets
    tourism_keywords = [
        'tourist', 'tourism', 'accommodation', 'occupancy',
        'top 10 source', 'location vs revenue', 'tourist attraction'
    ]
    if any(keyword in name_lower for keyword in tourism_keywords):
        return 'Tourism'

    # Foreign Employment datasets
    employment_keywords = [
        'slbfe', 'remittance', 'foreign exchange', 'local arrival',
        'local departure', 'legal division', 'complaints', 'raids'
    ]
    if any(keyword in name_lower for keyword in employment_keywords):
        return 'Foreign Employment'

    # Immigration datasets
    immigration_keywords = [
        'asylum', 'deportation', 'refugee', 'refused entry',
        'fake passport', 'fraudulent visa'
    ]
    if any(keyword in name_lower for keyword in immigration_keywords):
        return 'Immigration'

    # Budget datasets
    budget_keywords = [
        'capital expenditure', 'recurrent expenditure', 'budget'
    ]
    if any(keyword in name_lower for keyword in budget_keywords):
        return 'Budget'

    # Foreign Affairs datasets
    foreign_affairs_keywords = [
        'ministry news', 'mission news', 'staff of mission',
        'staff of the ministry', 'special notice', 'news from other',
        'cadre management'
    ]
    if any(keyword in name_lower for keyword in foreign_affairs_keywords):
        return 'Foreign Affairs'

    return 'Other'


def get_category_from_path(path_parts: List[str]) -> str:
    """Extract category from path parts, looking for AS_CATEGORY markers"""
    for part in path_parts:
        if '(AS_CATEGORY)' in part:
            return clean_name(part)
    return ''


def scan_data_folder(data_path: str = "data") -> Dict[str, Any]:
    """
    Scan the data folder and generate a structured index.

    Returns a dictionary with:
    - datasets: List of all datasets with metadata
    - years: List of available years
    - ministries: List of unique ministries
    - statistics: Summary statistics
    """
    if not os.path.exists(data_path):
        print(f"Error: {data_path} folder not found!")
        return {"datasets": [], "years": [], "ministries": [], "statistics": {}}

    datasets = []
    years_set = set()
    ministries_set = set()
    departments_set = set()
    categories_set = set()

    for root, dirs, files in os.walk(data_path):
        if "data.json" in files:
            # Get relative path from data folder
            rel_path = os.path.relpath(root, data_path)
            path_parts = rel_path.split(os.sep)

            # Extract hierarchical information
            year = path_parts[0] if len(path_parts) > 0 and path_parts[0].isdigit() else ""

            # Find government, president, ministry, department
            government = ""
            president = ""
            ministry = ""
            department = ""
            category = ""
            dataset_name = path_parts[-1] if path_parts else ""

            for i, part in enumerate(path_parts):
                if '(government)' in part:
                    government = clean_name(part)
                elif '(citizen)' in part:
                    president = clean_name(part)
                elif '(minister)' in part:
                    ministry = clean_name(part)
                elif '(department)' in part:
                    department = clean_name(part)
                elif '(AS_CATEGORY)' in part:
                    category = clean_name(part)

            # Clean dataset name
            dataset_name_clean = clean_name(dataset_name)

            # Categorize dataset based on name (for flat statistics structure)
            if not category:
                category = categorize_dataset(dataset_name_clean)

            # Build path for data access (served via staticDirectories from ../data)
            # Prefix with 'statistics/' since we scan data/statistics but serve from data/
            data_path_rel = f"statistics/{rel_path}/data.json".replace('\\', '/')

            # Check for metadata.json
            metadata_path = os.path.join(root, "metadata.json")
            has_metadata = os.path.exists(metadata_path)
            metadata_path_rel = f"statistics/{rel_path}/metadata.json".replace('\\', '/') if has_metadata else None

            # Check if data.json is empty
            data_json_path = os.path.join(root, "data.json")
            is_empty = False
            try:
                with open(data_json_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    is_empty = not content
            except Exception:
                is_empty = True

            # Build search text (for client-side search)
            search_parts = [
                year, government, president, ministry, department,
                category, dataset_name_clean
            ]
            search_text = " ".join(filter(None, search_parts)).lower()

            dataset_entry = {
                "id": rel_path.replace(os.sep, '_').replace(' ', '_'),
                "name": dataset_name_clean,
                "year": year,
                "government": government,
                "president": president,
                "ministry": ministry,
                "department": department,
                "category": category,
                "path": data_path_rel,
                "metadataPath": metadata_path_rel,
                "hasMetadata": has_metadata,
                "isEmpty": is_empty,
                "searchText": search_text,
                "hierarchy": path_parts,
            }

            datasets.append(dataset_entry)

            if year:
                years_set.add(year)
            if ministry:
                ministries_set.add(ministry)
            if department:
                departments_set.add(department)
            if category:
                categories_set.add(category)

    # Sort datasets by year (descending) then by name
    datasets.sort(key=lambda x: (x['year'], x['ministry'], x['department'], x['name']), reverse=False)

    # Build hierarchical tree structure
    tree = build_tree_structure(datasets)

    return {
        "datasets": datasets,
        "years": sorted(list(years_set), reverse=True),
        "ministries": sorted(list(ministries_set)),
        "departments": sorted(list(departments_set)),
        "categories": sorted(list(categories_set)),
        "tree": tree,
        "statistics": {
            "totalDatasets": len(datasets),
            "totalYears": len(years_set),
            "totalMinistries": len(ministries_set),
            "totalDepartments": len(departments_set),
            "totalCategories": len(categories_set),
        }
    }


def build_tree_structure(datasets: List[Dict]) -> Dict:
    """Build a hierarchical tree structure from flat dataset list"""
    tree = {}

    for dataset in datasets:
        hierarchy = dataset['hierarchy']
        current = tree

        for i, part in enumerate(hierarchy[:-1]):  # Exclude the dataset folder itself
            clean_part = clean_name(part)
            if clean_part not in current:
                current[clean_part] = {
                    "_meta": {
                        "name": clean_part,
                        "originalName": part,
                        "level": i,
                    },
                    "_children": {},
                    "_datasets": []
                }
            current = current[clean_part]["_children"]

        # Add the dataset to the deepest level
        # TODO: Optimize tree traversal logic (Issue #96: https://github.com/LDFLK/datasets/issues/96)
        parent_key = clean_name(hierarchy[-2]) if len(hierarchy) > 1 else ""
        if parent_key:
            # Navigate to parent
            current_nav = tree # See Issue #96
            for part in hierarchy[:-2]:
                clean_part = clean_name(part)
                if clean_part in current_nav:
                    current_nav = current_nav[clean_part]["_children"]

            parent_clean = clean_name(hierarchy[-2])
            if parent_clean in current_nav:
                current_nav[parent_clean]["_datasets"].append(dataset)

    return tree


def main():
    """Main function to generate the dataset index"""
    print("Generating dataset index for React DataBrowser...")

    # Determine paths relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    # Only scan the statistics folder (published data)
    data_path = project_root / "data" / "statistics"
    output_path = project_root / "website" / "src" / "data" / "datasetIndex.json"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Scan and generate index
    index_data = scan_data_folder(str(data_path))

    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print(f"Generated {output_path}")
    print(f"  - Total datasets: {index_data['statistics']['totalDatasets']}")
    print(f"  - Years: {', '.join(index_data['years'])}")
    print(f"  - Categories: {', '.join(index_data['categories'])}")


if __name__ == "__main__":
    main()
