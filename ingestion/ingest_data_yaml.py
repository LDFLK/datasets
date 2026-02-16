#!/usr/bin/env python3

import asyncio
import argparse
import os
import sys
import uuid
import json
from typing import Dict, List, Any

from ingestion.services.yaml_parser import YamlParser
from ingestion.services.read_service import ReadService
from ingestion.services.ingestion_service import IngestionService
from ingestion.services.entity_resolver import (
    find_ministers_by_name_and_year, 
    find_department_by_name_and_ministers,
    find_government_by_name,
    find_citizen_by_name
)
from ingestion.utils.http_client import http_client
from ingestion.models.schema import Entity, EntityCreate, Relation, Kind, NameValue, AddRelation, AddRelationValue
from ingestion.utils.util_functions import Util
from ingestion.utils.date_utils import calculate_attribute_time_period
from ingestion.utils.logger import logger


# Create either a category or subcategory IF it does not exist yet
async def create_category(
    name: str,
    parent_id: str,
    parent_start_time: str,
    parent_end_time: str,
    read_service: ReadService,
    ingestion_service: IngestionService,
    is_subcategory: bool
) -> str:

    # Determine Kind based on is_subcategory flag
    if is_subcategory:
        kind = Kind(major="Category", minor="childCategory")
    else:
        kind = Kind(major="Category", minor="parentCategory")
    
    # Existence check: Fetch OUTGOING relations from parent_id with name AS_CATEGORY
    relation_filter = Relation(
        name="AS_CATEGORY",
        direction="OUTGOING"
    )
    
    try:
        relations = await read_service.fetch_relations(parent_id, relation_filter)
    except Exception as e:
        logger.warning(f"Failed to fetch relations for existence check: {e}")
        relations = []
    
    # Iterate through ALL returned relations
    for relation in relations:
        related_entity_id = relation.relatedEntityId
        if not related_entity_id:
            continue
        
        # Fetch the entity to check its name
        try:
            search_entity = Entity(id=related_entity_id)
            entities = await read_service.get_entities(search_entity)
            
            if entities and len(entities) > 0:
                entity = entities[0]
                # Check if the entity's name matches
                decoded_name = Util.decode_protobuf_attribute_name(entity.name)
                if decoded_name == name:
                    logger.info(f"Category '{decoded_name}' already exists with ID: {related_entity_id}")
                    return related_entity_id
        except Exception as e:
            # Continue checking other relations if this one fails
            logger.warning(f"Failed to fetch entity {related_entity_id} for existence check: {e}")
            continue
    
    # Category not found - create new one
    logger.info(f"[CREATE] Creating new category '{name}'")
    
    # Generate a unique ID for the entity
    unique_id = str(uuid.uuid4())
    
    # Step 1: Create the category entity WITHOUT relationships
    category_create = EntityCreate(
        id=unique_id,
        name=NameValue(
            startTime=parent_start_time,
            endTime=parent_end_time if parent_end_time else "",
            value=name  # The actual name string
        ),
        kind=kind,
        created=parent_start_time,
        terminated=parent_end_time if parent_end_time else "",
        metadata=[],
        attributes=[],
        relationships=[]  # No relationships when creating
    )
    
    try:
        result = await ingestion_service.create_entity(category_create)
        # Extract entity ID from response
        created_cat_id = result.get('id', unique_id)
        logger.success(f"Created category '{name}' with ID: {created_cat_id}")
    except Exception as e:
        logger.error(f"Failed to create category '{name}': {e}")
        raise
    
    # Step 2: Update the parent entity to add the relationship
    logger.info(f"[UPDATE] Adding relationship from parent {parent_id} to category {created_cat_id}")
    
    try:
        # Create the new relationship in API format
        relation_id = str(uuid.uuid4())
        parent_cat_relation = AddRelation(
            key="AS_CATEGORY",
            value=AddRelationValue(
                id=relation_id,
                name="AS_CATEGORY",
                relatedEntityId=created_cat_id,  # Relationship points TO the category
                startTime=parent_start_time,
                endTime=parent_end_time if parent_end_time else ""
            )
        )
        
        # Add relationship from parent entity to category entity
        parent_cat_rel_update = EntityCreate(
            id=parent_id,
            relationships=[parent_cat_relation]  # Only the new relationship
        )
        
        # Update the parent entity
        await ingestion_service.update_entity(parent_id, parent_cat_rel_update)
        logger.success(f"Added relationship from parent {parent_id} to category {created_cat_id}")
        
    except Exception as e:
        logger.warning(f"Failed to update parent entity with relationship: {e}")
        # Category was created successfully, so we still return the ID
        logger.info(f"Category {created_cat_id} was created but relationship may not have been added")
    
    return created_cat_id

# Recursively process categories and their subcategories/datasets.
async def process_categories(
    categories: List[Dict[str, Any]],
    parent_id: str,
    parent_type: str,
    yaml_base_path: str,
    year: str,
    parent_start_time: str,
    parent_end_time: str,
    read_service: ReadService,
    ingestion_service: IngestionService
):

    for category in categories:
        category_name = category.get('name', '')
        if not category_name:
            continue
        
        logger.info(f"[CATEGORY] Processing category: {category_name} under {parent_type} {parent_id}")
        
        # Create category entity and relationship to parent
        category_id = await create_category(
            name=category_name,
            parent_id=parent_id,
            parent_start_time=parent_start_time,
            parent_end_time=parent_end_time,
            read_service=read_service,
            ingestion_service=ingestion_service,
            is_subcategory=False
        )
        
        # Check for subcategories
        subcategories = YamlParser.get_subcategories(category)
        if subcategories:
            await process_subcategories_recursive(
                subcategories, 
                category_id,
                yaml_base_path, 
                year,
                parent_start_time=parent_start_time,
                parent_end_time=parent_end_time,
                read_service=read_service,
                ingestion_service=ingestion_service
            )
        
        # Check for datasets directly under category
        datasets = YamlParser.get_datasets(category)
        if datasets:
            await process_datasets(
                datasets,
                category_id,
                yaml_base_path,
                year,
                parent_start_time=parent_start_time,
                parent_end_time=parent_end_time,
                ingestion_service=ingestion_service
            )

# Recursively process subcategories and their nested subcategories/datasets.
async def process_subcategories_recursive(
    subcategories: List[Dict[str, Any]],
    parent_id: str,
    yaml_base_path: str,
    year: str,
    parent_start_time: str,
    parent_end_time: str,
    read_service: ReadService,
    ingestion_service: IngestionService
):

    for subcategory in subcategories:
        subcategory_name = subcategory.get('name', '')
        if not subcategory_name:
            continue
        
        logger.info(f"[SUBCATEGORY] Processing subcategory: {subcategory_name} under parent {parent_id}")
        
        # Create subcategory entity and relationship to parent
        subcategory_id = await create_category(
            name=subcategory_name,
            parent_id=parent_id,
            parent_start_time=parent_start_time,
            parent_end_time=parent_end_time,
            read_service=read_service,
            ingestion_service=ingestion_service,
            is_subcategory=True
        )
        
        # Check for nested subcategories
        nested_subcategories = YamlParser.get_subcategories(subcategory)
        if nested_subcategories:
            await process_subcategories_recursive(
                nested_subcategories,
                subcategory_id,
                yaml_base_path,
                year,
                parent_start_time=parent_start_time,
                parent_end_time=parent_end_time,
                read_service=read_service,
                ingestion_service=ingestion_service
            )
        
        # Check for datasets under subcategory
        datasets = YamlParser.get_datasets(subcategory)
        if datasets:
            await process_datasets(
                datasets,
                subcategory_id,
                yaml_base_path,
                year,
                parent_start_time=parent_start_time,
                parent_end_time=parent_end_time,
                ingestion_service=ingestion_service
            )

# Add a dataset as an attribute to the parent entity.Return True if successful
async def add_dataset_attribute(
    parent_id: str,
    dataset_path: str,
    yaml_base_path: str,
    year: str,
    parent_start_time: str,
    parent_end_time: str,
    ingestion_service: IngestionService
) -> bool:

    # Calculate attribute time period (intersection of parent time and year)
    time_period = calculate_attribute_time_period(
        parent_start_time,
        parent_end_time,
        year
    )
    
    if time_period is None:
        logger.warning(f"No time overlap between parent period and year {year}, skipping dataset")
        return False
    
    attr_start_time, attr_end_time = time_period
    
    # Resolve full path to dataset directory
    full_dataset_path = os.path.join(yaml_base_path, dataset_path)
    data_json_path = os.path.join(full_dataset_path, 'data.json')
    metadata_json_path = os.path.join(full_dataset_path, 'metadata.json')
    
    # Check if dataset directory and data.json exist
    if not os.path.exists(full_dataset_path):
        logger.warning(f"Dataset path does not exist: {full_dataset_path}")
        return False
    
    if not os.path.exists(data_json_path):
        logger.warning(f"data.json not found at: {data_json_path}")
        return False
    
    # Read data.json
    try:
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data_content = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse data.json: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to read data.json: {e}")
        return False
    
    # Validate structure using utility function
    if not Util.validate_tabular_dataset(data_content):
        return False
    
    # TODO: Read metadata.json
    
    # Generate attribute name from dataset path
    dataset_name = os.path.basename(dataset_path.rstrip('/'))
    attribute_name = Util.format_attribute_name(dataset_name) + "-" + year
    
    columns = data_content.get('columns', [])
    rows = data_content.get('rows', [])
    logger.info(f"[ATTRIBUTE] Adding attribute '{attribute_name}' to parent {parent_id}")
    logger.info(f"  Time period: {attr_start_time} to {attr_end_time}")
    logger.info(f"  Columns: {len(columns)}, Rows: {len(rows)}")
    
    # Create attribute structure - use data_content directly
    attribute = {
        "key": attribute_name,
        "value": {
            "values": [
                {
                    "startTime": attr_start_time,
                    "endTime": attr_end_time if attr_end_time else "",
                    "value": data_content
                }
            ]
        }
    }
    
    # Update parent entity with the attribute
    try:
        entity_update = EntityCreate(
            id=parent_id,
            attributes=[attribute]
        )
        
        await ingestion_service.update_entity(parent_id, entity_update)
        logger.success(f"Added attribute '{attribute_name}' to parent {parent_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update parent entity with attribute: {e}")
        return False

# Process dataset files and add them as attributes to the parent entity.
async def process_datasets(
    datasets: List[str],
    parent_id: str,
    yaml_base_path: str,
    year: str,
    parent_start_time: str,
    parent_end_time: str,
    ingestion_service: IngestionService
):

    for dataset_path in datasets:
        dataset_name = os.path.basename(dataset_path.rstrip('/'))
        logger.info(f"[DATASET] Processing dataset: {dataset_name} under parent {parent_id}")
        
        # Add dataset as attribute to parent entity
        success = await add_dataset_attribute(
            parent_id=parent_id,
            dataset_path=dataset_path,
            yaml_base_path=yaml_base_path,
            year=year,
            parent_start_time=parent_start_time,
            parent_end_time=parent_end_time,
            ingestion_service=ingestion_service
        )
        
        if not success:
            logger.warning(f"Failed to add dataset '{dataset_name}' as attribute")

# Process a single citizen entry from the YAML.
async def process_citizen_entry(
    citizen_entry: Dict[str, Any],
    yaml_base_path: str,
    read_service: ReadService,
    ingestion_service: IngestionService
):

    citizen_name = citizen_entry.get('name', '')
    if not citizen_name:
        logger.warning(f"Skipping citizen entry with no name")
        return
    
    logger.info(f"[CITIZEN] Processing: {citizen_name}")
    
    # Find citizen entity by name
    citizen_entity = await find_citizen_by_name(citizen_name, read_service)
    
    if not citizen_entity:
        logger.error(f"Citizen entity not found for '{citizen_name}'. Skipping.")
        return
    
    citizen_id = citizen_entity.id
    logger.info(f"[SELECTED] Using citizen ID: {citizen_id}")
    
    # Extract time period from the citizen entity
    citizen_start_time = citizen_entity.created
    citizen_end_time = citizen_entity.terminated if citizen_entity.terminated else ""
    
    # Process profiles for this citizen
    profiles = YamlParser.get_profiles(citizen_entry)
    if profiles:
        await process_profiles(
            profiles,
            citizen_id,
            yaml_base_path,
            citizen_start_time=citizen_start_time,
            citizen_end_time=citizen_end_time,
            ingestion_service=ingestion_service
        )
    else:
        logger.info(f"No profiles found for citizen {citizen_name}")

# Process profile datasets and add them as attributes to the citizen entity.
async def process_profiles(
    profiles: List[str],
    citizen_id: str,
    yaml_base_path: str,
    citizen_start_time: str,
    citizen_end_time: str,
    ingestion_service: IngestionService
):

    for profile_path in profiles:
        profile_name = os.path.basename(profile_path.rstrip('/'))
        logger.info(f"[PROFILE] Processing profile: {profile_name} for citizen {citizen_id}")
        
        # Add profile as attribute
        success = await add_profile_attribute(
            citizen_id=citizen_id,
            profile_path=profile_path,
            yaml_base_path=yaml_base_path,
            citizen_start_time=citizen_start_time,
            citizen_end_time=citizen_end_time,
            ingestion_service=ingestion_service
        )
        
        if not success:
            logger.warning(f"Failed to add profile '{profile_name}' as attribute")

# Add a profile dataset as an attribute to a citizen entity. Return True if successful
async def add_profile_attribute(
    citizen_id: str,
    profile_path: str,
    yaml_base_path: str,
    citizen_start_time: str,
    citizen_end_time: str,
    ingestion_service: IngestionService
) -> bool:

    # Resolve full path to profile directory
    full_profile_path = os.path.join(yaml_base_path, profile_path)
    data_json_path = os.path.join(full_profile_path, 'data.json')
    
    # Check if profile directory and data.json exist
    if not os.path.exists(full_profile_path):
        logger.warning(f"Profile path does not exist: {full_profile_path}")
        return False
    
    if not os.path.exists(data_json_path):
        logger.warning(f"data.json not found at: {data_json_path}")
        return False
    
    # Read data.json
    try:
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data_content = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse data.json: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to read data.json: {e}")
        return False
    
    # Validate structure
    if not Util.validate_tabular_dataset(data_content):
        return False
    
    # Generate attribute name from profile path
    profile_name = os.path.basename(profile_path.rstrip('/'))
    attribute_name = Util.format_attribute_name(profile_name) + " Profile"
    
    columns = data_content.get('columns', [])
    rows = data_content.get('rows', [])
    logger.info(f"[ATTRIBUTE] Adding profile attribute '{attribute_name}' to citizen {citizen_id}")
    logger.info(f"  Columns: {len(columns)}, Rows: {len(rows)}")
    
    # Create attribute structure
    attribute = {
        "key": attribute_name,
        "value": {
            "values": [
                {
                    "startTime": citizen_start_time,
                    "endTime": citizen_end_time if citizen_end_time else "",
                    "value": data_content
                }
            ]
        }
    }
    
    # Update citizen entity with the attribute
    try:
        entity_update = EntityCreate(
            id=citizen_id,
            attributes=[attribute]
        )
        
        await ingestion_service.update_entity(citizen_id, entity_update)
        logger.success(f"Added profile attribute '{attribute_name}' to citizen {citizen_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update citizen entity with profile attribute: {e}")
        return False

# Process a single department entry from the YAML.
async def process_department_entry(
    department_entry: Dict[str, Any],
    department_id: str,
    yaml_base_path: str,
    year: str,
    dept_start_time: str,
    dept_end_time: str,
    read_service: ReadService,
    ingestion_service: IngestionService
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
            year,
            parent_start_time=dept_start_time,
            parent_end_time=dept_end_time,
            read_service=read_service,
            ingestion_service=ingestion_service
        )
    else:
        logger.info(f"No categories found under department {department_name}")
    
    # Process datasets directly under department if they exist
    datasets = YamlParser.get_datasets(department_entry)
    if datasets:
        await process_datasets(
            datasets,
            department_id,
            yaml_base_path,
            year,
            parent_start_time=dept_start_time,
            parent_end_time=dept_end_time,
            ingestion_service=ingestion_service
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
        logger.warning(f"Skipping minister entry with no name")
        return
    
    logger.info(f"[MINISTER] Processing: {minister_name}")
    
    # Find all ministers with this name active in the target year
    active_ministers = await find_ministers_by_name_and_year(
        minister_name,
        year,
        read_service
    )
    
    if not active_ministers:
        logger.warning(f"No ministers found with name '{minister_name}' active in year {year}")
        return
    
    logger.info(f"Found {len(active_ministers)} active minister relationship(s) in {year}")
    
    # Select the minister with latest startTime for direct categories
    minister_id = None
    if active_ministers:
        latest_minister = max(
            active_ministers,
            key=lambda m: m['start_time'] if m['start_time'] else ""
        )
        minister_id = latest_minister['minister_id']
        logger.info(f"[SELECTED] Using minister ID: {minister_id} (latest startTime: {latest_minister['start_time']})")
    
    # Process departments if they exist
    if YamlParser.has_departments(minister_entry):
        departments = YamlParser.get_departments(minister_entry)
        logger.info(f"[DEPARTMENTS] Found {len(departments)} department(s)")
        
        for department_entry in departments:
            department_name = department_entry.get('name', '')
            if not department_name:
                continue
            
            logger.info(f"[DEPARTMENT] Processing: {department_name}")
            
            # Find department connected to any of the active ministers
            department_info = await find_department_by_name_and_ministers(
                department_name,
                active_ministers,
                year,
                read_service
            )
            
            if not department_info:
                logger.warning(f"Department '{department_name}' not found or not connected to active ministers")
                continue
            
            department_id = department_info['department_id']
            department_relation = department_info['relation']
            logger.info(f"Found department ID: {department_id}")
            
            # Process the department entry
            await process_department_entry(
                department_entry,
                department_id,
                yaml_base_path,
                year,
                dept_start_time=department_relation.startTime or "",
                dept_end_time=department_relation.endTime or "",
                read_service=read_service,
                ingestion_service=ingestion_service
            )
    
    # Process direct categories under minister if they exist
    if YamlParser.has_categories(minister_entry):
        if not minister_id:
            logger.warning(f"Cannot process categories: No active minister selected")
        else:
            categories = YamlParser.get_categories(minister_entry)
            if categories:
                await process_categories(
                    categories,
                    minister_id,
                    "minister",
                    yaml_base_path,
                    year,
                    parent_start_time=latest_minister['start_time'],
                    parent_end_time=latest_minister['end_time'],
                    read_service=read_service,
                    ingestion_service=ingestion_service
                )
            else:
                logger.info(f"No categories found under minister {minister_name}")
    
    # Process direct datasets under minister if they exist
    datasets = YamlParser.get_datasets(minister_entry)
    if datasets:
        if not minister_id:
            logger.warning(f"Cannot process datasets: No active minister selected")
        else:
            await process_datasets(
                datasets,
                minister_id,
                yaml_base_path,
                year,
                parent_start_time=latest_minister['start_time'],
                parent_end_time=latest_minister['end_time'],
                ingestion_service=ingestion_service
            )

# Process a single government entry from the YAML.
async def process_government_entry(
    government_entry: Dict[str, Any],
    yaml_base_path: str,
    year: str,
    read_service: ReadService,
    ingestion_service: IngestionService
):
    government_name = government_entry.get('name', '')
    if not government_name:
        logger.warning(f"Skipping government entry with no name")
        return

    logger.info(f"[GOVERNMENT] Processing: {government_name}")

    # Find government with this name
    active_government = await find_government_by_name(
        government_name,
        read_service
    )

    if not active_government or not active_government.id:
        logger.warning(f"No governments found with name '{government_name}'")
        return

    government_id = active_government.id
    logger.info(f"[SELECTED] Using government ID: {government_id}")

    # Define government relationship start/end times
    gov_start_time = "1948-02-04"
    gov_end_time = ""

    # Process categories under government
    if YamlParser.has_categories(government_entry):
        categories = YamlParser.get_categories(government_entry)
        if categories:
            await process_categories(
                categories,
                government_id,
                "government",
                yaml_base_path,
                year,
                parent_start_time=gov_start_time,
                parent_end_time=gov_end_time,
                read_service=read_service,
                ingestion_service=ingestion_service
            )

async def main():
    """Main entry point for the ingestion script."""
    # Check required environment variables first
    read_base_url = os.getenv("READ_BASE_URL")
    ingestion_base_url = os.getenv("INGESTION_BASE_URL")
    
    if not read_base_url:
        logger.error("READ_BASE_URL environment variable is not set")
        logger.error("Please set it before running the ingestion script.")
        sys.exit(1)
    
    if not ingestion_base_url:
        logger.error("INGESTION_BASE_URL environment variable is not set")
        logger.error("Please set it before running the ingestion script.")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description='Ingest datasets from YAML manifest files using flat folder structure'
    )
    parser.add_argument(
        'yaml_file',
        type=str,
        help='Path to the YAML manifest file (e.g., data/2020/data_hierarchy_2020.yaml)'
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
        logger.error(f"YAML file not found: {yaml_path}")
        sys.exit(1)
    
    # Extract year from filename or use override
    if args.year:
        year = args.year
    else:
        try:
            year = YamlParser.extract_year_from_filename(yaml_path)
        except ValueError as e:
            logger.error(f"{e}")
            sys.exit(1)
    
    logger.info(f"Processing YAML file: {yaml_path}")
    logger.info(f"Target year: {year}")
    
    # Get base path for resolving dataset paths
    yaml_base_path = os.path.dirname(os.path.abspath(yaml_path))
    logger.info(f"Base path: {yaml_base_path}")
    
    # Parse YAML
    try:
        manifest = YamlParser.parse_manifest(yaml_path)
    except Exception as e:
        logger.error(f"Error parsing YAML: {e}")
        sys.exit(1)
    
    # Get list of ministers
    try:
        ministers = YamlParser.get_ministers(manifest)
    except Exception as e:
        logger.error(f"Error extracting ministers from YAML: {e}")
        ministers = []
    
    logger.info(f"Found {len(ministers)} minister(s) in YAML")

    # Get list of governments
    try:
        governments = YamlParser.get_governments(manifest)
    except Exception as e:
        logger.error(f"Error extracting governments from YAML: {e}")
        governments = []
    
    logger.info(f"Found {len(governments)} government(s) in YAML")
    
    # Initialize HTTP client
    await http_client.start()
    
    try:
        # Initialize services
        read_service = ReadService()
        ingestion_service = IngestionService()

        # Process each government entry
        for government_entry in governments:
            await process_government_entry(
                government_entry,
                yaml_base_path,
                year,
                read_service,
                ingestion_service
            )
        
        # Process each minister entry sequentially - change to parallel later
        for minister_entry in ministers:
            await process_minister_entry(
                minister_entry,
                year,
                yaml_base_path,
                read_service,
                ingestion_service
            )
          
        logger.success("[COMPLETE] Ingestion process finished")
    finally:
        # Clean up HTTP client
        await http_client.close()


if __name__ == "__main__":
    asyncio.run(main())
