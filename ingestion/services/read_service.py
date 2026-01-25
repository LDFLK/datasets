from ingestion.utils.http_client import http_client
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
from ingestion.models.schema import Entity, Relation
from google.api_core import retry_async
from ingestion.utils.response_handler import handle_api_response
from ingestion.exception.exceptions import (
    BadRequestError, 
    NotFoundError, 
    InternalServerError, 
    ServiceUnavailableError, 
    GatewayTimeoutError
)

load_dotenv()
READ_BASE_URL = os.getenv("READ_BASE_URL")

def custom_retry_predicate(exception: Exception) -> bool:
    """
    Determine if the request should be retried based on the exception type.
    Returns False for BadRequestError to skip retries.
    """
    if isinstance(exception, (BadRequestError, NotFoundError)):
        return False
    
    if isinstance(exception, (InternalServerError, ServiceUnavailableError, GatewayTimeoutError)):
        return True
    
    return False

api_retry_decorator = retry_async.AsyncRetry(
    predicate=custom_retry_predicate,
    initial=1.0,
    maximum=6.0,
    multiplier=2.0,
    timeout=20.0 # retry for 20 seconds
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

        async with self.session.post(url, json=payload, headers=headers) as response:
            res_json = await handle_api_response(response, error_prefix="Failed to get entities")
            response_list = res_json.get("body", [])
            # Return list of Entity objects
            result = [Entity.model_validate(item) for item in response_list]
            return result
    
    @api_retry_decorator
    async def fetch_relations(self, entityId: str, relation: Relation):
        if not entityId or not relation:
            raise BadRequestError("Entity ID and relation are required")
        
        stripped_entity_id = str(entityId).strip()
        if not stripped_entity_id:
            raise BadRequestError("Entity ID cannot be empty")
        
        url = f"{READ_BASE_URL}/v1/entities/{stripped_entity_id}/relations"
        headers = {"Content-Type": "application/json"}
        payload = relation.model_dump()

        async with self.session.post(url, json=payload, headers=headers) as response:
            data = await handle_api_response(response, error_prefix="Failed to get relations")
            result = [Relation.model_validate(item) for item in data]
            return result
    
    @api_retry_decorator
    async def get_entity_metadata(self, entityId: str):
        if not entityId:
            raise BadRequestError("Entity ID is required")
        
        stripped_entity_id = str(entityId).strip()
        if not stripped_entity_id:
            raise BadRequestError("Entity ID cannot be empty")
        
        url = f"{READ_BASE_URL}/v1/entities/{stripped_entity_id}/metadata"
        headers = {"Content-Type": "application/json"}

        async with self.session.get(url, headers=headers) as response:
            data = await handle_api_response(response, error_prefix="Failed to get entity metadata")
            return data
    
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
            raise BadRequestError("Entity ID and attribute name are required")
        
        stripped_entity_id = str(entityId).strip()
        stripped_attribute_name = str(attributeName).strip()
        
        if not stripped_entity_id:
            raise BadRequestError("Entity ID cannot be empty")
        if not stripped_attribute_name:
            raise BadRequestError("Attribute name cannot be empty")
        
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

        async with self.session.get(url, headers=headers, params=params) as response:
            data = await handle_api_response(response, error_prefix="Failed to get entity attribute")
            return data