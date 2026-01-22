from pydantic import BaseModel

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
    """Relation refers to the relation between two entities in the OpenGIN Specification"""
    name: str = ""
    activeAt: str = ""
    relatedEntityId: str = ""
    startTime: str = ""
    endTime: str = ""
    id: str = ""
    direction: str = ""

class EntityCreate(BaseModel):
    """EntityCreate refers to the object in the OpenGIN Specification"""
    id: str = ""
    name: str = ""
    kind: Kind = Kind()
    created: str = ""
    terminated: str = ""
    metadata: dict = {}
    attributes: dict = {}
    relationships: list[Relation] = []

class Date(BaseModel):
    date: str