import asyncio
from typing import List, Optional, Dict
from src.services.read_service import ReadService
from src.models.schema import Entity, Relation, Kind
from src.utils.date_utils import is_relationship_active_in_year


async def find_ministers_by_name_and_year(
    name: str, 
    year: str, 
    read_service: ReadService
) -> List[Dict[str, str]]:
    """
    Find all ministers with the given name that were active in the target year.
    
    This function:
    1. Searches for ministers by name using the search API
    2. For each minister found, fetches AS_MINISTER relationships with OUTGOING direction
    3. Filters relationships to only those active in the target year
    4. Returns all ministers that were active in the year with their relationship times
    
    Args:
        name: The name of the minister to search for
        year: The target year as a string (e.g., "2020")
        read_service: An instance of ReadService for API calls
        
    Returns:
        List of dictionaries, each containing:
        - 'minister_id': The minister entity ID
        - 'start_time': The start time of the relationship that was active in the year
        - 'end_time': The end time of the relationship (empty string if ongoing)
        
        Returns empty list if no ministers are found or none are active in the year.
    """
    # Search for ministers by name
    search_entity = Entity(
        name=name,
        kind=Kind(major="Organisation", minor="minister")
    )
    
    try:
        ministers = await read_service.get_entities(search_entity)
    except Exception as e:
        raise Exception(f"Failed to search for ministers: {e}")
    
    if not ministers:
        return []
    
    # For each minister, fetch AS_MINISTER relationships and check if active in year
    active_ministers = []
    
    # Create relation filter for AS_MINISTER OUTGOING
    relation_filter = Relation(
        name="AS_MINISTER",
        direction="INCOMING"
    )
    
    # Fetch relations for all ministers in parallel
    tasks = [
        read_service.fetch_relations(minister.id, relation_filter)
        for minister in ministers
    ]
    
    try:
        all_relations = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        raise Exception(f"Failed to fetch minister relations: {e}")
    
    # Process results - collect ALL active relationships, not just one per minister
    for i, relations in enumerate(all_relations):
        if isinstance(relations, Exception):
            # Skip ministers where relation fetch failed
            continue
        
        minister = ministers[i]
        
        # Check all relationships to find those active in the target year
        for relation in relations:
            start_time = relation.startTime or ""
            end_time = relation.endTime or ""
            
            if is_relationship_active_in_year(start_time, end_time, year):
                # This minister was active in the year with this relationship
                active_ministers.append({
                    'minister_id': minister.id,
                    'start_time': start_time,
                    'end_time': end_time
                })
    
    return active_ministers


async def find_department_by_name_and_ministers(
    name: str,
    active_ministers: List[Dict[str, str]],
    year: str,
    read_service: ReadService
) -> Optional[str]:
    """
    Find a department by name that is connected to any of the given ministers and active in the target year.
    
    This function:
    1. Searches for departments by name using the search API
    2. For each department found, fetches AS_DEPARTMENT relationships
    3. Filters relationships where relatedEntityId matches any of the minister IDs from active_ministers
    4. Filters relationships to only those active in the target year
    5. Returns the department ID with the latest startTime that's still within the year
    
    Args:
        name: The name of the department to search for
        active_ministers: List of dictionaries with 'minister_id', 'start_time', and 'end_time'
        year: The target year as a string (e.g., "2020")
        read_service: An instance of ReadService for API calls
        
    Returns:
        The department ID (string) with the latest startTime that was connected to one of the
        ministers and active in the year. Returns None if no matching department is found.
    """
    if not active_ministers:
        return None
    
    # Extract minister IDs from the active_ministers list
    minister_ids = [m['minister_id'] for m in active_ministers]
    
    # Search for departments by name
    search_entity = Entity(
        name=name,
        kind=Kind(major="Organisation", minor="department")
    )
    
    try:
        departments = await read_service.get_entities(search_entity)
    except Exception as e:
        raise Exception(f"Failed to search for departments: {e}")
    
    if not departments:
        return None
    
    # For each department, fetch AS_DEPARTMENT relations with relatedEntityId set to each minister ID
    # This directly gets us relations connected to any of the ministers
    matching_relations = []
    
    # Create tasks for all department-minister combinations
    tasks = []
    task_department_map = []  # Map task index to department
    
    for department in departments:
        for minister_id in minister_ids:
            relation_filter = Relation(
                name="AS_DEPARTMENT",
                direction="OUTGOING",
                relatedEntityId=minister_id
            )
            tasks.append(read_service.fetch_relations(department.id, relation_filter))
            task_department_map.append(department)
    
    try:
        all_relations = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        raise Exception(f"Failed to fetch department relations: {e}")
    
    # Process results - we now have relations directly connected to the ministers
    for i, relations in enumerate(all_relations):
        if isinstance(relations, Exception):
            # Skip where relation fetch failed
            continue
        
        if not relations:
            # Skip where there's no relation between department and minister
            continue
        
        department = task_department_map[i]
        
        # Check each relation to see if it was active in the target year
        for relation in relations:
            start_time = relation.startTime or ""
            end_time = relation.endTime or ""
            
            if is_relationship_active_in_year(start_time, end_time, year):
                # Store the relation with department info for later sorting
                matching_relations.append({
                    'department_id': department.id,
                    'relation': relation
                })
    
    if not matching_relations:
        return None
    
    # Find the relationship with the latest startTime
    latest_relation = max(
        matching_relations,
        key=lambda x: x['relation'].startTime if x['relation'].startTime else ""
    )
    
    return latest_relation['department_id']
