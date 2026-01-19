from http_client import http_client
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
from src.models.schema import Entity, Relation

load_dotenv()
READ_BASE_URL = os.getenv("READ_BASE_URL")

class ReadService:
    """
    The OpenGINService directly interfaces with the OpenGIN APIs to retrieve data.
    """
    def __init__(self, config: dict):
        self.config = config

    @property
    def session(self) -> ClientSession:
        return http_client.session

    async def get_entities(self, entity: Entity):
        """
        Search for entities based on the provided entity criteria.
        
        Args:
            entity: Entity object with search criteria
        
        Returns:
            List of Entity objects matching the search criteria
        """
        url = f"{READ_BASE_URL}/v1/entities/search"
        headers = {"Content-Type": "application/json"}
        payload = entity.model_dump()

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                res_json = await response.json()
                response_list = res_json.get("body", [])

                # Return list of Entity objects
                result = [Entity.model_validate(item) for item in response_list]
                return result

        except Exception as e:
            raise Exception(f"Read API Error: {str(e)}")
    
    async def fetch_relations(self, entityId: str, relation: Relation):
        """
        Fetch relations for a given entity based on the provided relation criteria.
        
        Args:
            entityId: The ID of the entity to fetch relations for
            relation: Relation object with search criteria
        
        Returns:
            List of Relation objects matching the search criteria
        
        Raises:
            Exception: If entityId is missing or empty, or if the API call fails
        """
        if not entityId or not relation:
            raise Exception("Entity ID and relation are required")
        
        stripped_entity_id = str(entityId).strip()
        if not stripped_entity_id:
            raise Exception("Entity ID cannot be empty")
        
        url = f"{READ_BASE_URL}/v1/entities/{stripped_entity_id}/relations"
        headers = {"Content-Type": "application/json"}
        payload = relation.model_dump()

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                result = [Relation.model_validate(item) for item in data]
                return result

        except Exception as e:
            raise Exception(f"Read API Error: {str(e)}")
    
    async def get_entity_metadata(self, entityId: str):
        """
        Get metadata of an entity.
        
        Args:
            entityId: The ID of the entity to get metadata for
        
        Returns:
            A dictionary containing entity metadata (structure may vary based on entity type)
        
        Raises:
            Exception: If entityId is missing or empty, or if the API call fails
        """
        if not entityId:
            raise Exception("Entity ID is required")
        
        stripped_entity_id = str(entityId).strip()
        if not stripped_entity_id:
            raise Exception("Entity ID cannot be empty")
        
        url = f"{READ_BASE_URL}/v1/entities/{stripped_entity_id}/metadata"
        headers = {"Content-Type": "application/json"}

        try:
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data

        except Exception as e:
            raise Exception(f"Read API Error: {str(e)}")
    
    async def get_entity_attribute(
        self, 
        entityId: str, 
        attributeName: str, 
        startTime: str = None, 
        endTime: str = None, 
        fields: list = None
    ):
        """
        Get entity attribute value(s).
        
        Args:
            entityId: The ID of the entity
            attributeName: The name of the attribute to retrieve
            startTime: Optional start time filter (date-time format)
            endTime: Optional end time filter (date-time format)
            fields: Optional list of field names to return. Defaults to ['*'] (all fields)
        
        Returns:
            Attribute value(s) - can be a single object, an array of objects, or null.
            Each object has 'start', 'end' (nullable), and 'value' properties.
        
        Raises:
            Exception: If entityId or attributeName is missing or empty, or if the API call fails
        """
        if not entityId or not attributeName:
            raise Exception("Entity ID and attribute name are required")
        
        stripped_entity_id = str(entityId).strip()
        stripped_attribute_name = str(attributeName).strip()
        
        if not stripped_entity_id:
            raise Exception("Entity ID cannot be empty")
        if not stripped_attribute_name:
            raise Exception("Attribute name cannot be empty")
        
        url = f"{READ_BASE_URL}/v1/entities/{stripped_entity_id}/attributes/{stripped_attribute_name}"
        headers = {"Content-Type": "application/json"}
        
        # Build query parameters
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if fields:
            # Handle array query parameter - aiohttp expects it as a list
            params["fields"] = fields

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data

        except Exception as e:
            raise Exception(f"Read API Error: {str(e)}")