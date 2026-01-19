from http_client import http_client
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
from src.models.schema import EntityCreate

load_dotenv()
READ_BASE_URL = os.getenv("READ_BASE_URL")

class IngestionService:
    """
    The OpenGINService directly interfaces with the OpenGIN APIs to insert data.
    """
    def __init__(self, config: dict):
        self.config = config

    @property
    def session(self) -> ClientSession:
        return http_client.session

    async def create_entity(self, entity: EntityCreate):
        url = f"{READ_BASE_URL}/v1/entities"
        headers = {"Content-Type":"application/json"}      
        payload = entity.model_dump()

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create entity: {response.status}")
        except Exception as e:
            raise Exception(f"Failed to create entity: {e}")

    async def update_entity(self, entity_id: str, entity: EntityCreate):
        """
        Update an existing entity by its ID.
        
        This method allows you to update an existing entity by:
        - Updating its core attributes (name, created, terminated)
        - Adding its metadata
        - Adding its attributes
        - Adding or Updating its relationships
        
        Args:
            entity_id: The ID of the entity to update (required in path and body)
            entity: The entity data to update (EntityCreate object)
        
        Returns:
            The updated entity as a dictionary
        
        Raises:
            Exception: If the update fails
        """
        url = f"{READ_BASE_URL}/v1/entities/{entity_id}"
        headers = {"Content-Type": "application/json"}
        payload = entity.model_dump()
        # Include the id in the payload as required by the API
        payload["id"] = entity_id

        try:
            async with self.session.put(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update entity: {response.status} - {error_text}")
        except Exception as e:
            raise Exception(f"Failed to update entity: {e}")
        