import asyncio
import logging
from typing import List, Optional, Dict, Any
from ingestion.services.read_service import ReadService
from ingestion.models.schema import Entity, Relation, Kind
from ingestion.utils.date_utils import is_relationship_active_in_year

logger = logging.getLogger(__name__)

# Find all ministers with the given name that were active in the target year.
# returns a list of dictionaries with id, starttime, endtime
async def find_ministers_by_name_and_year(name: str, year: str, read_service: ReadService) -> List[Dict[str, str]]:
    
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
    
    # Create relation filter for AS_MINISTER INCOMING
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
    
    # Process results - collect ALL active relationships for each minister
    for i, relations in enumerate(all_relations):
        if isinstance(relations, Exception):
            # Skip ministers where relation fetch failed
            minister = ministers[i]
            logger.warning(
                f"Failed to fetch relations for minister {minister.id} ({minister.name}): {relations}",
                exc_info=relations
            )
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

# Find all governments with the given name
async def find_government_by_name(name: str, read_service: ReadService) -> Optional[Entity]:
    
    # Search for government by name
    search_entity = Entity(
        name=name,
        kind=Kind(major="Organisation", minor="government")
    )
    
    try:
        governments = await read_service.get_entities(search_entity)
    except Exception as e:
        raise Exception(f"Failed to search for governments: {e}")
    
    if not governments:
        return None
           
    return governments[0]

#Find a department by name that is connected to any of the given ministers and active in the target year.
# Returns department id
async def find_department_by_name_and_ministers(name: str, active_ministers: List[Dict[str, str]], year: str, read_service: ReadService) -> Optional[Dict[str, Any]]:

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
                direction="INCOMING",
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
            department = task_department_map[i]
            logger.warning(
                f"Failed to fetch relations for department {department.id} ({department.name}): {relations}",
                exc_info=relations
            )
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
    
    return {
        'department_id': latest_relation['department_id'],
        'relation': latest_relation['relation']
    }

# Find a citizen entity by exact name match.
# Returns the full Entity object if found, None otherwise.
async def find_citizen_by_name(name: str, read_service: ReadService) -> Optional[Entity]:
    
    # Search for citizen by name
    search_entity = Entity(
        name=name,
        kind=Kind(major="Person", minor="citizen")
    )
    
    try:
        citizens = await read_service.get_entities(search_entity)
    except Exception as e:
        raise Exception(f"Failed to search for citizens: {e}")
    
    if not citizens:
        return None
    
    # Warn if multiple citizens found with the same name
    if len(citizens) > 1:
        citizen_ids = [citizen.id for citizen in citizens]
        logger.warning(
            f"Found {len(citizens)} citizens with name '{name}'. "
            f"IDs: {', '.join(citizen_ids)}. Using the first one: {citizen_ids[0]}"
        )
    
    return citizens[0]
