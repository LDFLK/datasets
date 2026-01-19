from enum import Enum
from dataclasses import dataclass

class MajorKind(str, Enum):
    ORGANISATION = "Organisation"
    CATEGORY = "Category"

class MinorKind(str, Enum):
    MINISTER = "minister"
    DEPARTMENT = "department"
    PARENT_CATEGORY = "parentCategory"
    CHILD_CATEGORY = "childCategory"

class RelationType(str, Enum):
    AS_MINISTER = "AS_MINISTER"
    AS_DEPARTMENT = "AS_DEPARTMENT"
    AS_CATEGORY = "AS_CATEGORY"
    AS_ATTRIBUTE = "AS_ATTRIBUTE"

@dataclass
class NodeSchema:
    major_kind: MajorKind
    minor_kind: MinorKind

# Mapping of Logical Type to Schema Properties
NODE_DEFINITIONS = {
    "minister": NodeSchema(MajorKind.ORGANISATION, MinorKind.MINISTER),
    "department": NodeSchema(MajorKind.ORGANISATION, MinorKind.DEPARTMENT),
    "category": NodeSchema(MajorKind.CATEGORY, MinorKind.PARENT_CATEGORY),
    "subcategory": NodeSchema(MajorKind.CATEGORY, MinorKind.CHILD_CATEGORY),
}
