from typing import Optional
from src.models.schema import Relation


# Get ISO 8601 timestamps for the start and end of a given year.
def get_year_boundaries(year: str) -> tuple[str, str]:
    year_int = int(year)
    year_start = f"{year_int}-01-01T00:00:00Z"
    year_end = f"{year_int}-12-31T23:59:59Z"
    return year_start, year_end


# Check if a relationship was active during the target year.
def is_relationship_active_in_year(start_time: str, end_time: str, year: str) -> bool:
    year_start, year_end = get_year_boundaries(year)
    
    # Relationship must have started before or during the year
    if start_time > year_end:
        return False

    if end_time == "" or end_time == None:
        return start_time <= year_end
    else:
        # Must end after or during the year start
        return end_time >= year_start


# Filter relationships that were active in the target year and return the one with the latest startTime.
def get_latest_relationship_in_year(relationships: list[Relation], year: str) -> Optional[Relation]:

    active_relationships = []
    
    for relation in relationships:
        start_time = relation.startTime or ""
        end_time = relation.endTime or ""
        
        if is_relationship_active_in_year(start_time, end_time, year):
            active_relationships.append(relation)
    
    if not active_relationships:
        return None
    
    # Sort by startTime descending (latest first) and return the first one
    # Handle empty startTime by treating it as earliest possible
    active_relationships.sort(
        key=lambda r: r.startTime if r.startTime else "",
        reverse=True
    )
    
    return active_relationships[0]
