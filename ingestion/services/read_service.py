from ingestion.utils.http_client import http_client
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
from ingestion.models.schema import Entity, Relation
from google.api_core import retry_async
from ingestion.exception.exceptions import BadRequestError, NotFoundError, InternalServerError

load_dotenv()
READ_BASE_URL = os.getenv("READ_BASE_URL")

def custom_retry_predicate(exception: Exception) -> bool:
    """
    Determine if the request should be retried based on the exception type.
    Returns False for BadRequestError to skip retries.
    """
    if isinstance(exception, (BadRequestError, NotFoundError)):
        return False
    
    if isinstance(exception, (InternalServerError)):
        return True

api_retry_decorator = retry_async.AsyncRetry(
    predicate=custom_retry_predicate,
    initial=1.0,
    maximum=6.0,
    multiplier=2.0,
    timeout=10.0 # retry for 10 seconds
)

class ReadService:
    """
    The OpenGINService directly interfaces with the OpenGIN APIs to retrieve data.
    """

    @property
    def session(self) -> ClientSession:
        return http_client.session

    @api_retry_decorator
    async def get_entities(self, entity: Entity):
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
    
    @api_retry_decorator
    async def fetch_relations(self, entityId: str, relation: Relation):
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
    
    @api_retry_decorator
    async def get_entity_metadata(self, entityId: str):
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
    
    @api_retry_decorator
    async def get_entity_attribute(
        self, 
        entityId: str, 
        attributeName: str, 
        startTime: str = None, 
        endTime: str = None, 
        fields: list = None
    ):

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