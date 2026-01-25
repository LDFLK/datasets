from ingestion.utils.http_client import http_client
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
from ingestion.models.schema import EntityCreate
from google.api_core import retry_async
from ingestion.utils.response_handler import handle_api_response
from ingestion.exception.exceptions import (
    BadRequestError, 
    NotFoundError, 
    InternalServerError, 
    ServiceUnavailableError, 
    GatewayTimeoutError
)

from ingestion.utils.logger import logger

load_dotenv()
INGESTION_BASE_URL = os.getenv("INGESTION_BASE_URL")

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

class IngestionService:

    @property
    def session(self) -> ClientSession:
        return http_client.session

    @api_retry_decorator
    async def create_entity(self, entity: EntityCreate):
        url = f"{INGESTION_BASE_URL}/entities"
        headers = {"Content-Type":"application/json"}      
        payload = entity.model_dump()


        async with self.session.post(url, headers=headers, json=payload) as response:
            return await handle_api_response(response, error_prefix="Failed to create entity")

    @api_retry_decorator
    async def update_entity(self, entity_id: str, entity: EntityCreate):
        url = f"{INGESTION_BASE_URL}/entities/{entity_id}"
        headers = {"Content-Type": "application/json"}
        payload = entity.model_dump()
        # Include the id in the payload as required by the API
        payload["id"] = entity_id

        async with self.session.put(url, headers=headers, json=payload) as response:
            return await handle_api_response(response, error_prefix="Failed to update entity")