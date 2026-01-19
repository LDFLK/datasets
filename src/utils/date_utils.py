from typing import Optional
from src.models.schema import Relation


def get_year_boundaries(year: str) -> tuple[str, str]:
    """
    Get ISO 8601 timestamps for the start and end of a given year.
    
    Args:
        year: The year as a string (e.g., "2020")
        
    Returns:
        A tuple of (year_start, year_end) where:
        - year_start: ISO 8601 timestamp for January 1st at 00:00:00 UTC (e.g., "2020-01-01T00:00:00Z")
        - year_end: ISO 8601 timestamp for December 31st at 23:59:59 UTC (e.g., "2020-12-31T23:59:59Z")
    """
    year_int = int(year)
    year_start = f"{year_int}-01-01T00:00:00Z"
    year_end = f"{year_int}-12-31T23:59:59Z"
    return year_start, year_end


def is_relationship_active_in_year(start_time: str, end_time: str, year: str) -> bool:
    """
    Check if a relationship was active during the target year.
    
    A relationship is considered active in a year if:
    - The relationship started before or during the year (startTime <= year_end)
    - The relationship ended after or during the year start, OR has no end time (endTime == "")
    
    Args:
        start_time: The relationship start time in ISO 8601 format (e.g., "2020-01-01T00:00:00Z")
        end_time: The relationship end time in ISO 8601 format, or empty string if ongoing
        year: The target year as a string (e.g., "2020")
        
    Returns:
        True if the relationship was active during the target year, False otherwise
    """
    year_start, year_end = get_year_boundaries(year)
    
    # Relationship must have started before or during the year
    if start_time > year_end:
        return False
    
    # Relationship must either:
    # 1. Have no end time (ongoing), OR
    # 2. End after or during the year start
    if end_time == "" or end_time == None:
        # No end time means it's ongoing, so it was active if it started before/during the year
        return start_time <= year_end
    else:
        # Must end after or during the year start
        return end_time >= year_start


def get_latest_relationship_in_year(relationships: list[Relation], year: str) -> Optional[Relation]:
    """
    Filter relationships that were active in the target year and return the one with the latest startTime.
    
    Args:
        relationships: List of Relation objects to filter
        year: The target year as a string (e.g., "2020")
        
    Returns:
        The Relation object with the latest startTime that was active in the year, or None if no
        relationships were active in the year
    """
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
