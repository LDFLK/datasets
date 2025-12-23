import os
import json
import hashlib
import binascii
import time
import logging
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any, List, Tuple, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from google.protobuf.wrappers_pb2 import StringValue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IngestionClient:
    def __init__(self, config: dict):
        self.config = config
        self.session = self._create_session()
        self.mongo_client = None
        self.db = None
        
        # Base URLs
        self.entity_url = "http://0.0.0.0:8080/entities/"
        self.search_url = "http://0.0.0.0:8081/v1/entities/search"

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "Content-Type": "application/json"
        })
        return session

    def generate_id_for_category(self, parent_of_parent_category_id: str, parent_category_name: str) -> str:
        raw = f"{parent_of_parent_category_id}-{parent_category_name}"
        short_hash = hashlib.sha1(raw.encode()).hexdigest()[:10]
        return f"cat_{short_hash}"

    def create_nodes(self, node_id: str, node_name: str, node_key: str, date: str) -> Dict[str, Any]:
        payload = {
            "id": node_id,
            "kind": {
                "major": "Category",
                "minor": node_key
            },
            "created": date,
            "terminated": "",
            "name": {
                "startTime": date,
                "endTime": "",
                "value": node_name
            },
            "metadata": [],
            "attributes": [],
            "relationships": []
        }
        
        logger.debug(f"Creating node: {node_id}")
        try:
            response = self.session.post(self.entity_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating node {node_id}: {e}")
            return {"error": str(e)}

    @lru_cache(maxsize=1024)
    def validate_node(self, entity_name: str, minor_kind: str, major_kind: str) -> Tuple[bool, str]:
        """Check if a node exists, using caching to avoid repeat lookups."""
        payload = {
            "kind": {
                "major": major_kind,
                "minor": minor_kind
            },
            "name": entity_name
        }
        
        logger.debug(f"Searching for node: {entity_name} ({major_kind}/{minor_kind})")
        
        try:
            response = self.session.post(self.search_url, json=payload)
            response.raise_for_status()
            output = response.json()
            if output and "body" in output and len(output["body"]) > 0:
                return True, output["body"][0]["id"]
            return False, "No data found"
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validating node {entity_name}: {e}")
            return False, "Not found - Error occured"

    @lru_cache(maxsize=1024)
    def get_created_date_of_node(self, entity_name: str, minor_kind: str, major_kind: str) -> Tuple[bool, str]:
        """Get creation date of a node, using caching."""
        payload = {
            "kind": {
                "major": major_kind,
                "minor": minor_kind
            },
            "name": entity_name
        }
        
        try:
            response = self.session.post(self.search_url, json=payload)
            response.raise_for_status()
            output = response.json()
            if output and "body" in output and len(output["body"]) > 0:
                return True, output["body"][0]["created"]
            return False, "No data found"
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting date for {entity_name}: {e}")
            return False, "Not found - Error occured"

    def create_relationships(self, parent_id: str, child_id: str, date: str) -> Dict[str, Any]:
        url = f"{self.entity_url}{parent_id}"
        
        payload = {
            "id": parent_id,
            "kind": {},  # API seems to accept empty kind for partial updates
            "relationships": [
                {
                    "key": "AS_CATEGORY",
                    "value": {
                        "relatedEntityId": child_id,
                        "startTime": date,
                        "endTime": "",
                        "id": f"{parent_id}-to-{child_id}",
                        "name": "AS_CATEGORY"
                    }
                }
            ]
        }
        
        try:
            # Using PUT as per original script, though PATCH might be more appropriate for partial updates if supported
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating relationship {parent_id}->{child_id}: {e}")
            return {"error": str(e)}

    def create_attribute_to_entity(self, date: str, entity_id: str, attribute_table_name: str, values: Any) -> Dict[str, Any]:
        url = f"{self.entity_url}{entity_id}"
        payload = {
            "id": entity_id,
            "attributes": [
                {
                    "key": attribute_table_name,
                    "value": {
                        "values": [
                            {
                                "startTime": date,
                                "endTime": "",
                                "value": values
                            }
                        ]
                    }
                }
            ]
        }
        
        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating attribute for {entity_id}: {e}")
            return {"error": str(e)}

    def create_metadata_to_entity(self, entity_id: str, metadata: List[Dict[str, str]]) -> Dict[str, Any]:
        url = f"{self.entity_url}{entity_id}"
        payload = {
            "id": entity_id,
            "metadata": metadata
        }
        
        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating metadata for {entity_id}: {e}")
            return {"error": str(e)}

    @staticmethod
    def format_attribute_name_for_table_name(name: str, date: str) -> str:
        formatted = name.replace(" ", "_").replace("-", "_")
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            year = date_obj.strftime("%Y")
            formatted = f"{formatted}_{year}"
            hashed = hashlib.md5(formatted.encode()).hexdigest()[:10]
            return hashed
        except ValueError:
            # Fallback if date is invalid
            return hashlib.md5(f"{formatted}_{date}".encode()).hexdigest()[:10]

    @staticmethod
    def format_attribute_name_as_human_readable(name: str) -> str:
        return name.replace("_", " ").replace("-", " ").title()

    def traverse_folder(self, base_path: str) -> List[Dict[str, Any]]:
        result = []
        for root, dirs, files in os.walk(base_path):
            if 'data.json' not in files:
                continue

            data_path = os.path.join(root, 'data.json')
            metadata_path = os.path.join(root, 'metadata.json')
            parent_folder_name = os.path.basename(root)

            # Read data.json
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning(f"Skipping empty data.json in {root}")
                        continue
                    data_content = json.loads(content)
            except Exception as e:
                logger.error(f"Error reading {data_path}: {e}")
                continue

            # Read metadata.json
            metadata_content = {"message": "No metadata found"}
            if 'metadata.json' in files:
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as fm:
                        content_metadata = fm.read().strip()
                        if content_metadata:
                            metadata_content = json.loads(content_metadata)
                except Exception as e:
                    logger.warning(f"Error reading {metadata_path}, using placeholder: {e}")

            # Validate/Format attribute data
            attribute_data = self._validate_attribute_data(data_content, data_path)

            # Determine relationships
            relation_parts, related_entity_name = self._parse_folder_relationships(root, base_path)
            relation = " - ".join(relation_parts)

            result.append({
                "attributeName": parent_folder_name,
                "relatedEntityName": related_entity_name,
                "relation": relation,
                "attributeData": attribute_data,
                "attributeMetadata": metadata_content
            })
        return result

    def _validate_attribute_data(self, data_content: Any, file_path: str) -> Any:
        """Validate if data content matches columns and rows structure."""
        if isinstance(data_content, dict) and 'columns' in data_content and 'rows' in data_content:
            columns = data_content.get('columns')
            rows = data_content.get('rows')
            
            if isinstance(columns, list) and isinstance(rows, list):
                expected_len = len(columns)
                valid_rows = [r for r in rows if isinstance(r, list) and len(r) == expected_len]
                
                if len(valid_rows) != len(rows):
                    logger.warning(f"Filtered {len(rows) - len(valid_rows)} invalid rows in {file_path}")
                
                return {
                    "columns": columns,
                    "rows": valid_rows,
                    "validation": {
                        "total_rows": len(rows),
                        "valid_rows": len(valid_rows),
                        "invalid_rows": len(rows) - len(valid_rows)
                    }
                }
        return data_content

    def _parse_folder_relationships(self, root: str, base_path: str) -> Tuple[List[str], Optional[str]]:
        """Extract relationship hierarchy from folder structure."""
        parent_folder_name = os.path.basename(root)
        relation_parts = [parent_folder_name]
        current_dir = os.path.dirname(root)
        related_entity_name = None

        while current_dir and current_dir != os.path.dirname(base_path):
            folder_name = os.path.basename(current_dir)
            relation_parts.append(folder_name)
            
            if related_entity_name is None and not folder_name.endswith("(AS_CATEGORY)"):
                related_entity_name = folder_name
            
            current_dir = os.path.dirname(current_dir)

        return list(reversed(relation_parts)), related_entity_name

    def pre_process_traverse_result(self, result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich traversal results with entity metadata and structure category data."""
        for item in result:
            relation_set = item["relation"].split(" - ")
            
            # Extract date from year folder (first element)
            try:
                year = int(relation_set[0])
                date = datetime(year, 12, 31)
                item["attributeReleaseDate"] = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, IndexError):
                logger.warning(f"Could not parse year from relation: {item['relation']}")
                item["attributeReleaseDate"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

            category_hop_count = 0
            # Process path components
            for related_item in relation_set:
                name = related_item.split('(')[0]
                if related_item.endswith("(government)"):
                    item["government"] = name
                elif related_item.endswith("(citizen)"):
                    item["president"] = name
                elif related_item.endswith("(minister)"):
                    item["minister"] = name
                elif related_item.endswith("(department)"):
                    item["department"] = name
                elif related_item.endswith("(AS_CATEGORY)"):
                    if "categoryData" not in item:
                        item["categoryData"] = {}
                    
                    if category_hop_count == 0:
                        item["categoryData"]["parentCategory"] = name
                    else:
                        item["categoryData"][f"childCategory_{category_hop_count}"] = name
                    category_hop_count += 1
        return result

    def _resolve_entity_id(self, name: str, minor_kind: str, major_kind: str) -> str:
        """Resolve entity ID, returning the ID if found or the name if not (with logging)."""
        is_valid, entity_id = self.validate_node(name, minor_kind, major_kind)
        if not is_valid:
            logger.warning(f"Entity not found: {name} ({major_kind}/{minor_kind})")
            return entity_id  # Return error msg/placeholder as per original behavior
        return entity_id

    def entity_validator(self, result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and replace entity names with IDs in the dataset."""
        for item in result:
            # Check known entity types
            if "government" in item:
                item["government"] = self._resolve_entity_id(item["government"], "government", "Organisation")
            if "president" in item:
                item["president"] = self._resolve_entity_id(item["president"], "citizen", "Person")
            if "minister" in item:
                item["minister"] = self._resolve_entity_id(item["minister"], "minister", "Organisation")
            if "department" in item:
                item["department"] = self._resolve_entity_id(item["department"], "department", "Organisation")

            # Handle relatedEntityName
            if "relatedEntityName" in item and item["relatedEntityName"]:
                raw_name = item["relatedEntityName"]
                if '(' in raw_name and ')' in raw_name:
                    minor_kind = raw_name.split('(')[1].split(')')[0]
                    clean_name = raw_name.split('(')[0].strip()
                else:
                    minor_kind = "department"
                    clean_name = raw_name
                
                major_kind = "Organisation"
                is_valid, entity_id = self.validate_node(clean_name, minor_kind, major_kind)
                
                item["relatedEntityName"] = entity_id
                
                if is_valid:
                    valid_date, date_val = self.get_created_date_of_node(clean_name, minor_kind, major_kind)
                    item["relatedEntityCreatedDate"] = date_val if valid_date else "Not found date"
                else:
                    item["relatedEntityCreatedDate"] = "Not found date"
                    
        return result

    def _insert_dataset_for_category(self, category_id: str, category_name: str, 
                                   release_date: str, data: Any, table_name: str) -> Optional[str]:
        logger.info(f"Inserting dataset for category: {category_name}")
        res = self.create_attribute_to_entity(release_date, category_id, table_name, data)
        if res.get('id'):
            logger.info(f"✅ inserted dataset for {category_name}")
            return res.get('id')
        else:
            logger.error(f"Failed to insert dataset for {category_name}: {res.get('error')}")
            return None

    def create_categories_and_insert_datasets(self, result: List[Dict[str, Any]]):
        metadata_dict = {}
        logger.info(f"Total items to process: {len(result)}")

        for item in result:
            if "categoryData" not in item:
                continue

            attr_name = item["attributeName"]
            release_date = item["attributeReleaseDate"]
            related_entity_id = item["relatedEntityName"]
            related_created = item["relatedEntityCreatedDate"]
            
            table_name = self.format_attribute_name_for_table_name(attr_name, release_date)
            human_name = self.format_attribute_name_as_human_readable(attr_name)
            
            parent_cat_name = item["categoryData"]["parentCategory"]
            
            # --- Parent Category Processing ---
            is_valid_parent, parent_cat_id = self.validate_node(parent_cat_name, "parentCategory", "Category")
            
            if not is_valid_parent:
                logger.info(f"Creating parent category: {parent_cat_name}")
                parent_cat_id = self.generate_id_for_category(related_entity_id, parent_cat_name)
                res = self.create_nodes(parent_cat_id, parent_cat_name, "parentCategory", related_created)
                
                if res.get('id'):
                    self.create_relationships(related_entity_id, parent_cat_id, related_created)
                else:
                    logger.error(f"Failed to create parent category {parent_cat_name}")
                    continue

            # --- Child Category Processing ---
            category_data = item['categoryData']
            child_cats = []
            for key, val in category_data.items():
                if key.startswith('childCategory'):
                    try:
                        num = int(key.split('_')[1]) if '_' in key else 0
                    except ValueError:
                        num = 0
                    child_cats.append((num, key, val))
            
            child_cats.sort(key=lambda x: x[0])
            
            current_parent_id = parent_cat_id
            current_parent_name = parent_cat_name
            child_cats_found = False

            for num, key, child_name in child_cats:
                child_cats_found = True
                is_valid_child, child_id = self.validate_node(child_name, "childCategory", "Category")
                
                if not is_valid_child:
                    logger.info(f"Creating child category: {child_name}")
                    child_id = self.generate_id_for_category(current_parent_id, child_name)
                    res = self.create_nodes(child_id, child_name, "childCategory", related_created)
                    
                    if res.get('id'):
                        self.create_relationships(current_parent_id, child_id, related_created)
                    else:
                        logger.error(f"Failed to create child category {child_name}")
                        continue
                
                current_parent_id = child_id
                current_parent_name = child_name
                
                # Insert dataset at last child
                if num == child_cats[-1][0]:
                    self._insert_dataset_for_category(child_id, child_name, release_date, item['attributeData'], table_name)
                    metadata = {"key": table_name, "value": human_name}
                    metadata_dict.setdefault(child_id, []).append(metadata)

            # Insert at parent if no children
            if not child_cats_found:
                self._insert_dataset_for_category(parent_cat_id, parent_cat_name, release_date, item['attributeData'], table_name)
                metadata = {"key": table_name, "value": human_name}
                metadata_dict.setdefault(parent_cat_id, []).append(metadata)

        self.create_metadata_to_entities(metadata_dict)
        return result

    def connect_to_mongodb(self) -> Tuple[bool, Optional[Any]]:
        try:
            client = MongoClient(self.config['MONGODB_URI'])
            client.admin.command('ping')
            self.mongo_client = client
            self.db = client.doc_db
            logger.info("✅ Connected to MongoDB successfully!")
            return True, self.db
        except ConnectionFailure as e:
            logger.error(f"❌ Could not connect to MongoDB: {e}")
            return False, None

    def extract_existing_metadata_from_entity(self, entity_id: str) -> Dict:
        url = f"http://0.0.0.0:8081/v1/entities/{entity_id}/metadata"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error extracting metadata for {entity_id}: {e}")
            return {}

    def create_metadata_to_entities(self, metadata_dict: Dict[str, List[Dict[str, str]]]):
        for entity_id, new_metadata in metadata_dict.items():
            existing = self.extract_existing_metadata_from_entity(entity_id)
            
            # Convert existing protobuf-like format if necessary
            cleaned_existing = []
            if existing:
                for key, val in existing.items():
                    decoded = self.decode_protobuf(val) if isinstance(val, str) else val
                    cleaned_existing.append({"key": key, "value": decoded})
            
            merged_metadata = cleaned_existing + new_metadata
            self.create_metadata_to_entity(entity_id, merged_metadata)

    def decode_protobuf(self, name: str) -> str:
        try:
            if not isinstance(name, str): 
                return str(name)
            data = json.loads(name)
            hex_value = data.get("value")
            if not hex_value:
                return ""
            decoded_bytes = binascii.unhexlify(hex_value)
            sv = StringValue()
            try:
                sv.ParseFromString(decoded_bytes)
                return sv.value.strip()
            except Exception:
                decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                return ''.join(ch for ch in decoded_str if ch.isprintable()).strip()
        except Exception:
            return ""

def main():
    config = {
        'MONGODB_URI': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'),
        'BASE_URL_QUERY': 'http://0.0.0.0:8081'
    }
    
    client = IngestionClient(config)
    
    # Example usage based on typical workflow
    # 1. Traverse
    base_path = "data" # Assumed relative path
    if os.path.exists(base_path):
        data = client.traverse_folder(base_path)
        data = client.pre_process_traverse_result(data)
        data = client.entity_validator(data)
        
        # 2. Process
        client.create_categories_and_insert_datasets(data)
    else:
        logger.warning(f"Data directory '{base_path}' not found.")

if __name__ == "__main__":
    main()
