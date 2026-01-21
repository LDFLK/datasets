#!/usr/bin/env python3
"""
Main ingestion script for processing YAML manifest files from the flat folder structure.

This script:
1. Parses YAML manifest files
2. Finds the correct minister and department entities in the database
3. Processes categories, subcategories, and datasets from the YAML structure
4. Inserts entities and relationships into the database
"""

import asyncio
import argparse
import os
import sys
from typing import Dict, List, Any, Optional

from ingestion.services.yaml_parser import YamlParser
from ingestion.services.read_service import ReadService
from ingestion.services.ingestion_service import IngestionService
from ingestion.services.entity_resolver import find_ministers_by_name_and_year, find_department_by_name_and_ministers
from ingestion.utils.http_client import http_client


# Recursively process categories and their subcategories/datasets.
async def process_categories(
    categories: List[Dict[str, Any]],
    parent_id: str,
    parent_type: str,
    yaml_base_path: str,
    year: str
):

    for category in categories:
        category_name = category.get('name', '')
        if not category_name:
            continue
        
        print(f"  [CATEGORY] Processing category: {category_name} under {parent_type} {parent_id}")
        
        # TODO: Create category entity and relationship to parent
        # category_id = await create_category_entity(category_name, parent_id, parent_type, year)
        
        # Check for subcategories
        subcategories = YamlParser.get_subcategories(category)
        if subcategories:
            await process_subcategories_recursive(
                subcategories, 
                category_name,  # Using name as placeholder, would use category_id
                yaml_base_path, 
                year
            )
        
        # Check for datasets directly under category
        datasets = YamlParser.get_datasets(category)
        if datasets:
            await process_datasets(
                datasets,
                category_name,  # Using name as placeholder, would use category_id
                yaml_base_path
            )


# Recursively process subcategories and their nested subcategories/datasets.
async def process_subcategories_recursive(
    subcategories: List[Dict[str, Any]],
    parent_id: str,
    yaml_base_path: str,
    year: str
):

    for subcategory in subcategories:
        subcategory_name = subcategory.get('name', '')
        if not subcategory_name:
            continue
        
        print(f"    [SUBCATEGORY] Processing subcategory: {subcategory_name} under parent {parent_id}")
        
        # TODO: Create subcategory entity and relationship to parent
        # subcategory_id = await create_subcategory_entity(subcategory_name, parent_id, year)
        
        # Check for nested subcategories
        nested_subcategories = YamlParser.get_subcategories(subcategory)
        if nested_subcategories:
            await process_subcategories_recursive(
                nested_subcategories,
                subcategory_name,  # Using name as placeholder, would use subcategory_id
                yaml_base_path,
                year
            )
        
        # Check for datasets under subcategory
        datasets = YamlParser.get_datasets(subcategory)
        if datasets:
            await process_datasets(
                datasets,
                subcategory_name,  # Using name as placeholder, would use subcategory_id
                yaml_base_path
            )

# Process dataset files
async def process_datasets(
    datasets: List[str],
    parent_id: str,
    yaml_base_path: str
):

    for dataset_path in datasets:
        # Resolve full path to dataset
        full_dataset_path = os.path.join(yaml_base_path, dataset_path)
        dataset_name = os.path.basename(dataset_path.rstrip('/'))
        
        print(f"      [DATASET] Processing dataset: {dataset_name} under parent {parent_id}")
        print(f"        Path: {full_dataset_path}")
        
        # Check if dataset directory exists
        if os.path.exists(full_dataset_path):
            data_json_path = os.path.join(full_dataset_path, 'data.json')
            metadata_json_path = os.path.join(full_dataset_path, 'metadata.json')
            
            if os.path.exists(data_json_path):
                print(f"        Found data.json")
            if os.path.exists(metadata_json_path):
                print(f"        Found metadata.json")
            
            # TODO: Read data.json and metadata.json
            # TODO: Create dataset entity
            # TODO: Link dataset to parent category/subcategory
        else:
            print(f"        WARNING: Dataset path does not exist: {full_dataset_path}")

# Process a single department entry from the YAML.
async def process_department_entry(
    department_entry: Dict[str, Any],
    department_id: str,
    yaml_base_path: str,
    year: str
):

    department_name = department_entry.get('name', '')
    
    # Process categories under this department
    categories = YamlParser.get_categories(department_entry)
    if categories:
        await process_categories(
            categories,
            department_id,
            "department",
            yaml_base_path,
            year
        )
    else:
        print(f"    [INFO] No categories found under department {department_name}")
    
    # Process datasets directly under department if they exist
    datasets = YamlParser.get_datasets(department_entry)
    if datasets:
        await process_datasets(
            datasets,
            department_id,
            yaml_base_path
        )

# Process a single minister entry from the YAML.
async def process_minister_entry(
    minister_entry: Dict[str, Any],
    year: str,
    yaml_base_path: str,
    read_service: ReadService,
    ingestion_service: IngestionService
):

    minister_name = minister_entry.get('name', '')
    if not minister_name:
        print(f"[WARNING] Skipping minister entry with no name")
        return
    
    print(f"\n[MINISTER] Processing: {minister_name}")
    
    # Find all ministers with this name active in the target year
    active_ministers = await find_ministers_by_name_and_year(
        minister_name,
        year,
        read_service
    )
    
    if not active_ministers:
        print(f"  [WARNING] No ministers found with name '{minister_name}' active in year {year}")
        return
    
    print(f"  Found {len(active_ministers)} active minister relationship(s) in {year}")
    
    # Select the minister with latest startTime for direct categories/datasets
    minister_id = None
    if active_ministers:
        latest_minister = max(
            active_ministers,
            key=lambda m: m['start_time'] if m['start_time'] else ""
        )
        minister_id = latest_minister['minister_id']
        print(f"  [SELECTED] Using minister ID: {minister_id} (latest startTime: {latest_minister['start_time']})")
    
    # Process departments if they exist
    if YamlParser.has_departments(minister_entry):
        departments = YamlParser.get_departments(minister_entry)
        print(f"  [DEPARTMENTS] Found {len(departments)} department(s)")
        
        for department_entry in departments:
            department_name = department_entry.get('name', '')
            if not department_name:
                continue
            
            print(f"\n  [DEPARTMENT] Processing: {department_name}")
            
            # Find department connected to any of the active ministers
            department_id = await find_department_by_name_and_ministers(
                department_name,
                active_ministers,
                year,
                read_service
            )
            
            if not department_id:
                print(f"    [WARNING] Department '{department_name}' not found or not connected to active ministers")
                continue
            
            print(f"    Found department ID: {department_id}")
            
            # Process the department entry
            await process_department_entry(
                department_entry,
                department_id,
                yaml_base_path,
                year
            )
    
    # Process direct categories under minister if they exist
    if YamlParser.has_categories(minister_entry):
        if not minister_id:
            print(f"  [WARNING] Cannot process categories: No active minister selected")
        else:
            categories = YamlParser.get_categories(minister_entry)
            if categories:
                await process_categories(
                    categories,
                    minister_id,
                    "minister",
                    yaml_base_path,
                    year
                )
            else:
                print(f"  [INFO] No categories found under minister {minister_name}")
    
    # Process direct datasets under minister if they exist
    datasets = YamlParser.get_datasets(minister_entry)
    if datasets:
        if not minister_id:
            print(f"  [WARNING] Cannot process datasets: No active minister selected")
        else:
            await process_datasets(
                datasets,
                minister_id,
                yaml_base_path
            )


async def main():
    """Main entry point for the ingestion script."""
    parser = argparse.ArgumentParser(
        description='Ingest datasets from YAML manifest files using flat folder structure'
    )
    parser.add_argument(
        'yaml_file',
        type=str,
        help='Path to the YAML manifest file (e.g., data/2020_flat/manifest_2020.yaml)'
    )
    parser.add_argument(
        '--year',
        type=str,
        default=None,
        help='Override year extracted from filename (optional)'
    )
    
    args = parser.parse_args()
    
    yaml_path = args.yaml_file
    if not os.path.exists(yaml_path):
        print(f"Error: YAML file not found: {yaml_path}")
        sys.exit(1)
    
    # Extract year from filename or use override
    if args.year:
        year = args.year
    else:
        try:
            year = YamlParser.extract_year_from_filename(yaml_path)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    print(f"Processing YAML file: {yaml_path}")
    print(f"Target year: {year}")
    
    # Get base path for resolving dataset paths
    yaml_base_path = os.path.dirname(os.path.abspath(yaml_path))
    print(f"Base path: {yaml_base_path}")
    
    # Parse YAML
    try:
        manifest = YamlParser.parse_manifest(yaml_path)
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)
    
    # Get list of ministers
    try:
        ministers = YamlParser.get_ministers(manifest)
    except Exception as e:
        print(f"Error extracting ministers from YAML: {e}")
        sys.exit(1)
    
    print(f"\nFound {len(ministers)} minister(s) in YAML")
    
    # Initialize HTTP client
    await http_client.start()
    
    try:
        # Initialize services
        read_service = ReadService()
        ingestion_service = IngestionService()
        
        # Process each minister entry sequentially - change to parallel later
        for minister_entry in ministers:
            await process_minister_entry(
                minister_entry,
                year,
                yaml_base_path,
                read_service,
                ingestion_service
            )
        
        print("\n[COMPLETE] Ingestion process finished")
    finally:
        # Clean up HTTP client
        await http_client.close()


if __name__ == "__main__":
    asyncio.run(main())
