from pydantic import BaseModel
from typing import Dict, Any, Optional

class Kind(BaseModel):
    """Kind refers to the type of entity in the OpenGIN Specification"""
    major: str = ""
    minor: str = ""
    
class Entity(BaseModel):
    """Entity refers to the object in the OpenGIN Specification"""
    id: str = ""
    name: str = ""
    kind: Kind = Kind()
    created: str = ""
    terminated: str = ""

class Relation(BaseModel):
    """Relation refers to the relation between two entities in the OpenGIN Specification (for reading/filtering)"""
    name: str = ""
    activeAt: str = ""
    relatedEntityId: str = ""
    startTime: str = ""
    endTime: str = ""
    id: str = ""
    direction: str = ""

class NameValue(BaseModel):
    """Name value structure for EntityCreate API format"""
    startTime: str = ""
    endTime: str = ""
    value: str = ""

class AddRelationValue(BaseModel):
    """Value part of AddRelation for API format"""
    relatedEntityId: str = ""
    startTime: str = ""
    endTime: str = ""
    id: str = ""
    name: str = ""

class AddRelation(BaseModel):
    """Relation format for EntityCreate API (with key-value structure)"""
    key: str = ""
    value: AddRelationValue = AddRelationValue()

class EntityCreate(BaseModel):
    """EntityCreate refers to the object in the OpenGIN Specification for API creation"""
    id: str = ""
    kind: Kind = Kind()
    created: str = ""
    terminated: str = ""
    name: NameValue = NameValue()
    metadata: list[Dict[str, Any]] = []
    attributes: list[Dict[str, Any]] = []
    relationships: list[AddRelation] = []

class Date(BaseModel):
    date: str