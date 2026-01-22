from typing import Optional
from ingestion.models.schema import Relation


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


def calculate_attribute_time_period(
    parent_start_time: str,
    parent_end_time: str,
    year: str
) -> Optional[tuple[str, str]]:
    """
    Calculate the attribute time period as the intersection of parent time period and target year.
    
    The attribute's startTime and endTime must be within both:
    - The parent entity's time period (parent_start_time to parent_end_time)
    - The target year's time period ({year}-01-01T00:00:00Z to {year}-12-31T23:59:59Z)
    
    Args:
        parent_start_time: Start time of the parent entity relationship (ISO 8601 format)
        parent_end_time: End time of the parent entity relationship (ISO 8601 format, empty string if ongoing)
        year: Target year as a string (e.g., "2020")
        
    Returns:
        Tuple of (attribute_start_time, attribute_end_time) if there's an overlap, None otherwise.
        Returns None if the parent time period doesn't overlap with the target year.
    """
    # Get year boundaries
    year_start, year_end = get_year_boundaries(year)
    
    # Calculate intersection start: max of parent_start_time and year_start
    attr_start = max(parent_start_time, year_start)
    
    # If attr_start is after year_end, there's no overlap
    if attr_start > year_end:
        return None
    
    # Calculate intersection end
    if not parent_end_time or parent_end_time == "":
        # Parent has no end time (ongoing), so use year_end
        attr_end = year_end
    else:
        # Parent has an end time, use the minimum of parent_end_time and year_end
        attr_end = min(parent_end_time, year_end)
    
    # Validate: if attr_start > attr_end, there's no overlap
    if attr_start > attr_end:
        return None
    
    return (attr_start, attr_end)
