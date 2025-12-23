import os
import json
import argparse
from datetime import datetime
import requests
import hashlib
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import binascii
from google.protobuf.wrappers_pb2 import StringValue
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class WriteAttributes:
    def __init__(self, config : dict):
        self.config = config
        self.session = self._create_session()

    def _create_session(self):
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
        return session
    
    def generate_id_for_category(self, parent_of_parent_category_id, parent_category_name):
        raw = f"{parent_of_parent_category_id}-{parent_category_name}"
        short_hash = hashlib.sha1(raw.encode()).hexdigest()[:10]
        node_id = f"cat_{short_hash}"
        return node_id

    def create_nodes(self, node_id, node_name, node_key, date):
        
        url = "http://0.0.0.0:8080/entities/"
           
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
        headers = {
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {token}"  
                }
        
        print(f"    [DEBUG] Create payload: {payload}")
        print(f"    [DEBUG] Create URL: {url}")
        
        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()  
            output = response.json()
            return output
        except Exception as e:
            print("error : " +  str(e))
            return {
                "error": str(e)
            }

    def validate_node(self, entity_name, minorKind, majorKind) -> tuple[bool, str]:
        url = "http://0.0.0.0:8081/v1/entities/search"
        
        payload = {
            "kind": {
                "major": majorKind,
                "minor": minorKind
            },
            "name": entity_name
            }
        
        headers = {
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {token}"  
                }
        

        print(f"    [DEBUG] Search payload: {payload}")
        print(f"    [DEBUG] Search URL: {url}")
        
        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()  
            output = response.json()
            if output and "body" in output and len(output["body"]) > 0:
                entity_id = output["body"][0]["id"]
                return True, entity_id
            else:
                return False, "No data found"
        except Exception as e:
            print("error : " +  str(e))
            return False , "Not found - Error occured"
        
    def get_created_date_of_node(self, entity_name, minorKind, majorKind) -> tuple[bool, str]:
        url = "http://0.0.0.0:8081/v1/entities/search"
        
        payload = {
            "kind": {
                "major": majorKind,
                "minor": minorKind
            },
            "name": entity_name
            }
        
        headers = {
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {token}"  
                }
                
        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()  
            output = response.json()
            if output and "body" in output and len(output["body"]) > 0:
                return True, output["body"][0]["created"]
            else:
                return False, "No data found"
        except Exception as e:
            print("error : " +  str(e))
            return False , "Not found - Error occured"
        
    def create_relationships(self, parent_id, child_id, date):
        url = f"http://0.0.0.0:8080/entities/{parent_id}"
        
        payload = {
                "id": parent_id,
                "kind": {},
                "created": "",
                "terminated": "",
                "name": {
                },
                "metadata": [],
                "attributes": [],
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
        headers = {
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {token}"  
                }
        
        
        try:
            response = self.session.put(url, json=payload, headers=headers)
            response.raise_for_status()  
            output = response.json()
            return output
        except Exception as e:
            print("error : " +  str(e))
            return {
                "error": str(e)
            }
   
    def create_attribute_to_entity(self, date, entity_id, attribute_name_for_table_name, values): 
        url = f"http://0.0.0.0:8080/entities/{entity_id}"
        payload = {
            "id": entity_id,
            "attributes": [
                {
                    "key": attribute_name_for_table_name,
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
        
        headers = {
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {token}"  
                }
        
        try:
            response = self.session.put(url, json=payload, headers=headers)
            response.raise_for_status()  
            output = response.json()
            return output
        except Exception as e:
            print(f"error : " +  str(e))
            return {
                "error" : str(e)
            }
            
    def create_metadata_to_entity(self, entity_id, metadata): 
        url = f"http://0.0.0.0:8080/entities/{entity_id}"
        payload = {
            "id": entity_id,
             "metadata": metadata
        }
        
        headers = {
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {token}"  
                }
        
        try:
            response = self.session.put(url, json=payload, headers=headers)
            response.raise_for_status()  
            output = response.json()
            return output
        except Exception as e:
            print(f"error : " +  str(e))
            return {
                "error" : str(e)
            }

    def format_attribute_name_for_table_name(self, name, date):
        formatted = name.replace(" ", "_").replace("-", "_")
        date_for_id_u = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        year_u = date_for_id_u.strftime("%Y")
        formatted = f"{formatted}_{year_u}"
        hashed = hashlib.md5(formatted.encode()).hexdigest()[:10] 
        return hashed
    
    def format_attribute_name_as_human_readable(self, name):
        formatted = name.replace("_", " ").replace("-", " ") 
        return formatted.title()
            
    def traverse_folder(self, base_path, year_filter=None):
        result = []
        
        # Use absolute path for reliable comparison
        base_path = os.path.abspath(base_path)

        for root, dirs, files in os.walk(base_path):
            if year_filter and root == base_path:
                if year_filter in dirs:
                    dirs[:] = [year_filter]
                else:
                    dirs[:] = []
                    continue
            # data.json is mandatory, metadata.json optional
            if 'data.json' in files:
                data_path = os.path.join(root, 'data.json')
                metadata_path = os.path.join(root, 'metadata.json')
                parent_folder_name = os.path.basename(root)

                # Read data.json (required)
                try:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            print(f"Skipping empty data.json in {root} \n")
                            continue
                        data_content = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON in {root} (data.json): {e} \n")
                    continue
                except Exception as e:
                    print(f"Error reading {data_path}: {e}\n")
                    continue

                # Read metadata.json (optional)
                if 'metadata.json' in files:
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as fm:
                            content_metadata = fm.read().strip()
                            if not content_metadata:
                                print(f"metadata.json empty in {root} — using placeholder\n")
                                metadata_content = {"message": "No metadata found"}
                            else:
                                try:
                                    metadata_content = json.loads(content_metadata)
                                except json.JSONDecodeError as e:
                                    print(f"Invalid metadata.json in {root}: {e} — using placeholder\n")
                                    metadata_content = {"message": "Invalid metadata JSON"}
                    except Exception as e:
                        print(f"Error reading {metadata_path}: {e}\n")
                        metadata_content = {"message": "No metadata found"}
                else:
                    # metadata missing -> use placeholder
                    metadata_content = {"message": "No metadata found"}

                # If data_content has columns & rows, validate rows lengths match columns count
                attribute_data = None
                if isinstance(data_content, dict) and 'columns' in data_content and 'rows' in data_content:
                    columns = data_content.get('columns')
                    rows = data_content.get('rows')

                    if not isinstance(columns, list) or not isinstance(rows, list):
                        print(f"[WARN] columns/rows in {data_path} are not lists — storing raw data\n")
                        attribute_data = data_content
                    else:
                        expected_len = len(columns)
                        valid_rows = []
                        invalid_count = 0
                        for i, row in enumerate(rows):
                            if isinstance(row, list) and len(row) == expected_len:
                                valid_rows.append(row)
                            else:
                                invalid_count += 1
                                print(f"[WARN] Row #{i} in {data_path} has length {len(row) if isinstance(row, list) else 'N/A'}; expected {expected_len}")

                        attribute_data = {
                            "columns": columns,
                            "rows": valid_rows,
                            "validation": {
                                "total_rows": len(rows),
                                "valid_rows": len(valid_rows),
                                "invalid_rows": invalid_count
                            }
                        }
                else:
                    # Not a tabular structure — keep as-is
                    attribute_data = data_content

                # Collect relation parts from parent folder back to base_path
                relation_parts = [parent_folder_name]  # folder before data.json
                current_dir = os.path.dirname(root)   # go one level up

                relatedEntityName = None

                # Stop when we reach the base_path
                while current_dir and current_dir != base_path and current_dir != os.path.dirname(current_dir):
                    folder_name = os.path.basename(current_dir)
                    relation_parts.append(folder_name)

                    # Pick the first non-(AS_CATEGORY) folder as relatedEntityName
                    if relatedEntityName is None and not folder_name.endswith("(AS_CATEGORY)"):
                        relatedEntityName = folder_name

                    current_dir = os.path.dirname(current_dir)

                # Reverse so relation starts from base_path children down to parent folder
                relation_parts = list(reversed(relation_parts))
                relation = " - ".join(relation_parts)

                result.append({
                    "attributeName": parent_folder_name,
                    "relatedEntityName": relatedEntityName,
                    "relation": relation,
                    "attributeData": attribute_data,
                    "attributeMetadata": metadata_content
                })

        return result
    
    def pre_process_traverse_result(self, result):    
        for item in result:
            category_hop_count = 0
            relation_set = item["relation"].split(" - ")
            year = relation_set[0]
            date = datetime(int(year), 12, 31) 
            iso_date_str = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            item["attributeReleaseDate"] = str(iso_date_str)
            for related_item in relation_set:
                if related_item.endswith("(government)"):
                    item["government"] = str(related_item.split('(')[0])
                elif related_item.endswith("(citizen)"):
                    item["president"] = str(related_item.split('(')[0])
                elif related_item.endswith("(minister)"):
                    item["minister"] = str(related_item.split('(')[0])
                elif related_item.endswith("(department)"):
                    item["department"] = str(related_item.split('(')[0])
                elif related_item.endswith("(AS_CATEGORY)"):
                    if "categoryData" not in item:
                        item["categoryData"] = {}
                    if category_hop_count == 0:
                        item["categoryData"]["parentCategory"] = str(related_item.split('(')[0])
                    elif category_hop_count >= 1:
                        item["categoryData"]["childCategory_" + str(category_hop_count)] = str(related_item.split('(')[0])
                    category_hop_count += 1
        return result
    
    def entity_validator(self, result):
        for item in result:
            for data in list(item.keys()):
                if data == "government":
                    minorKind = "government"
                    majorKind = "Organisation"
                    is_valid, entity_id = self.validate_node(item[data], minorKind, majorKind)
                    if is_valid:
                        item[data] = entity_id
                    else:
                        item[data] = entity_id
                elif data == "president":
                    minorKind = "citizen"
                    majorKind = "Person"
                    is_valid, entity_id   = self.validate_node(item[data], minorKind, majorKind)
                    if is_valid:
                        item[data] = entity_id
                    else:
                        item[data] = entity_id
                elif data == "minister":
                    minorKind = "minister"
                    majorKind = "Organisation"
                    is_valid, entity_id = self.validate_node(item[data], minorKind, majorKind)
                    if is_valid:
                        item[data] = entity_id
                    else:
                        item[data] = entity_id
                elif data == "department":
                    minorKind = "department"
                    majorKind = "Organisation"
                    is_valid, entity_id = self.validate_node(item[data], minorKind, majorKind)
                    if is_valid:
                        item[data] = entity_id
                    else:
                        item[data] = entity_id
                elif data == "relatedEntityName":
                    related_entity_name = item[data]
                    if '(' in related_entity_name and ')' in related_entity_name:
                        minorKind = related_entity_name.split('(')[1].split(')')[0]
                        clean_name = related_entity_name.split('(')[0].strip()
                    else:
                        # Default to department if no parentheses found
                        minorKind = "department"
                        clean_name = related_entity_name
                    
                    majorKind = "Organisation"
                    
                    is_valid, entity_id = self.validate_node(clean_name, minorKind, majorKind)
                    if is_valid:
                        item[data] = entity_id
                        is_valid_related_entity_created_date, related_entity_created_date = self.get_created_date_of_node(clean_name, minorKind, majorKind)
                        if is_valid_related_entity_created_date:
                            item["relatedEntityCreatedDate"] = related_entity_created_date
                        else:
                            item["relatedEntityCreatedDate"] = related_entity_created_date
                    else:
                        item[data] = entity_id
                        item["relatedEntityCreatedDate"] = "Not found date"
        return result
     
    def _insert_dataset_for_category(self, category_id, category_name, attributeReleaseDate, attributeData, attribute_name_for_table_name):
        """Helper function to insert dataset for a category (parent or child)"""
        print(f"  --Inserting dataset for category ---> {category_name}")
        print(f"  --Formatted dataset name for table name - {attribute_name_for_table_name}")
        # date_for_id_u = datetime.strptime(attributeReleaseDate, "%Y-%m-%dT%H:%M:%SZ")
        # year_u = date_for_id_u.strftime("%Y")
        # attribute_name_for_table_name = f"{attribute_name_for_table_name}_{year_u}_{category_id}"
        res = self.create_attribute_to_entity(attributeReleaseDate, category_id, attribute_name_for_table_name, attributeData)
        if res.get('id'):
            print(f"  --✅ Inserted dataset for {category_name} with attribute id {res['id']}")
        else:
            print(f"  --Inserting dataset for {category_name} was unsuccessfull")
            print(f"  --Error ---> {res['error']}")

    def create_categories_and_insert_datasets(self, result):   
        metadata_dict = {}         

        print(f"Total items to process: {len(result)}")
        
        print("=" * 200)
        
        for item in result:
            attributeReleaseDate = item["attributeReleaseDate"]
            attributeName = item["attributeName"]
            relatedEntityName = item["relatedEntityName"]
            relatedEntityCreatedDate = item["relatedEntityCreatedDate"]
            attribute_name_for_table_name = self.format_attribute_name_for_table_name(attributeName, attributeReleaseDate)
            attribute_name_as_human_readable = self.format_attribute_name_as_human_readable(attributeName)
    
            print(f"🔄 Processing item ---> {attributeName}")
            print(f"  --Dataset name: {attributeName}")
            print(f"  --Dataset name (Human readable) - {attribute_name_as_human_readable}")
            print(f"  --Formatted dataset name for table name - {attribute_name_for_table_name}")
            print(f"  --Dataset release date: {attributeReleaseDate}")
            print(f"  --Related entity Id: {relatedEntityName}")
            print(f"  --Related entity created date: {relatedEntityCreatedDate}")
            parent_category_name = item["categoryData"]["parentCategory"]
            print(f"  --Parent category name: {parent_category_name}")
            print(f"  --Checking if parent category exists ---> {parent_category_name}")
            is_valid_parent_category, parent_category_id = self.validate_node(parent_category_name, "parentCategory", "Category")
            if is_valid_parent_category:
                print(f"  --Parent category found ---> {parent_category_name} with id: {parent_category_id}")
            else:
                print(f"  --Parent category not found")
                print(f"  --Start creating parent category ---> {parent_category_name}")
                parent_category_id = self.generate_id_for_category(relatedEntityName, parent_category_name) 
                res = self.create_nodes(parent_category_id, parent_category_name, "parentCategory", relatedEntityCreatedDate)
                if res.get('id'):
                    print(f"  --Parent category created ---> {parent_category_name} with id: {parent_category_id}")
                    print(f"  --Creating relationship from {relatedEntityName} ---> {parent_category_id}")
                    res = self.create_relationships(relatedEntityName, parent_category_id, relatedEntityCreatedDate)
                    if res.get('id'):
                        print(f"  --Relationship created ---> {relatedEntityName} ---> {parent_category_id}")
                    else:
                        print(f"  --Relationship creation failed ---> {relatedEntityName} ---> {parent_category_id}")
                        print(f"  --Error ---> {res['error']}")
                else:
                    print(f"  --Parent category creation failed ---> {parent_category_name}")
                    print(f"  --Error ---> {res['error']}")
                    continue  # Skip child category creation if parent failed
            
            print("\n")
            
            # Create child categories in hierarchical order (only if parent category was successfully created)
            category_data = item['categoryData']
            child_categories_found = False
            
            # Collect and sort child categories by their numeric suffix
            child_categories_list = []
            for key, child_category_name in category_data.items():
                if key.startswith('childCategory'):
                    child_categories_found = True
                    # Extract the number from childCategory_N
                    try:
                        num = int(key.split('_')[1]) if '_' in key else 0
                        child_categories_list.append((num, key, child_category_name))
                    except (ValueError, IndexError):
                        child_categories_list.append((0, key, child_category_name))
            
            # Sort by numeric suffix to maintain hierarchy
            child_categories_list.sort(key=lambda x: x[0])
            
            # Track the current parent for the hierarchy chain
            current_parent_id = parent_category_id
            current_parent_name = parent_category_name
            
            # Process child categories in order, creating hierarchical relationships
            for num, key, child_category_name in child_categories_list:
                print(f"  --Child category name: {child_category_name} (Level {num})")
                print(f"  --Checking if child category exists ---> {child_category_name}")
                is_valid_child_category, child_category_id = self.validate_node(child_category_name, "childCategory", "Category")
                if is_valid_child_category:
                    print(f"  --Child category found ---> {child_category_name} with id: {child_category_id}")
                else:
                    print(f"  --Child category not found")
                    print(f"  --Creating child category ---> {child_category_name}")
                    child_category_id = self.generate_id_for_category(current_parent_id, child_category_name)
                    res = self.create_nodes(child_category_id, child_category_name, "childCategory", relatedEntityCreatedDate)
                    if res.get('id'):
                        print(f"  --Child category created ---> {child_category_name} with id: {child_category_id}")
                        print(f"  --Creating relationship from {current_parent_name} ({current_parent_id}) ---> {child_category_name} ({child_category_id})")
                        res = self.create_relationships(current_parent_id, child_category_id, relatedEntityCreatedDate)
                        if res.get('id'):
                            print(f"  --Child relationship created ---> {current_parent_id} ---> {child_category_id}")
                        else:
                            print(f"  --Child relationship creation failed ---> {current_parent_id} ---> {child_category_id}")
                            print(f"  --Error ---> {res['error']}")
                            continue
                    else:
                        print(f"  --Child category creation failed ---> {child_category_name}")
                        print(f"  --Error ---> {res['error']}")
                        continue
                
                # Update current parent for next iteration (to create chain: parent -> child1 -> child2)
                current_parent_id = child_category_id
                current_parent_name = child_category_name
                
                # Only insert dataset to the last child category in the chain
                if num == child_categories_list[-1][0]:  # Last child category
                    print(f"  --This is the last child category in the chain, inserting dataset here")
                    self._insert_dataset_for_category(child_category_id, child_category_name, attributeReleaseDate, item['attributeData'], attribute_name_for_table_name)
                    print(f"  --Storing metadata for {child_category_name}")
                    metadata = {
                        "key" : attribute_name_for_table_name,
                        "value": attribute_name_as_human_readable
                    }
                    if child_category_id in metadata_dict:
                        metadata_dict[child_category_id].append(metadata)
                    else:
                        metadata_dict[child_category_id] = [metadata]
            
            # Check if no child categories were found
            if not child_categories_found:
                print(f"  --No child categories found for parent category: {parent_category_name}")
                print(f"  --Parent category ID: {parent_category_id}")
                # Insert dataset into parent category when no child categories exist
                self._insert_dataset_for_category(parent_category_id, parent_category_name, attributeReleaseDate, item['attributeData'], attribute_name_for_table_name)
                print(f"  --Storing metadata for {parent_category_name}")
                metadata = {
                    "key" : attribute_name_for_table_name,
                    "value": attribute_name_as_human_readable
                }
                if parent_category_id in metadata_dict:
                    metadata_dict[parent_category_id].append(metadata)
                else:
                    metadata_dict[parent_category_id] = [metadata]
        
            print("=" * 200)
            
        print(f"Metadata dictionary: {metadata_dict}")
        self.create_metadata_to_entities(metadata_dict)
        
        return result

    def create_parent_categories_and_children_categories(self, result):
        count = 0
        node_ids = {}  
        metadata_dict = {}
        
        print(f"Total items to process: {len(result)}")
        
        print("=" * 200)
    
        for item in result:
            
            date = item["attributeReleaseDate"]
            if 'categoryData' in item:
                pass
                category_data = item['categoryData']

                # --- Create parent node ---
                parent_name = category_data['parentCategory']
                
                if 'minister' and 'department' in item:
                    parent_of_parent_category_id = item["department"]
                elif 'minister' in item:
                    parent_of_parent_category_id = item["minister"]
                
                attribute_name = item['attributeName']  
                attribute_data = item['attributeData']
                
                if parent_name not in node_ids:
                    node_id = self.generate_id_for_category(date, parent_of_parent_category_id, parent_name)
                    print(f"id >>>>>>>>>>>>>> {node_id}")
                    print(f"🔄 Creating parent category node for ---> '{parent_name}'")
                    date_for_id_u = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                    year_u = date_for_id_u.strftime("%Y")
                    month_day_u = date_for_id_u.strftime("%m-%d")
                    parent_name_unique = f"{parent_name}_{year_u}_{month_day_u}"
                    res = self.create_nodes(node_id.lower(), parent_name_unique, 'parentCategory', date)
                    if res.get('id'):
                        count += 1
                        node_id = res['id']
                        node_ids[parent_name] = node_id
                        print(f"✅ Created parent category node for ---> '{parent_name}' with id: {node_id}")
                        parent_id = node_ids[parent_name]
                        print(f"🔄 Creating relationship from {parent_of_parent_category_id} ---> {parent_id}")
                        res = self.create_relationships(parent_of_parent_category_id, parent_id, date)
                        if res.get('id'):
                            print(f"✅ Created relationship from {parent_of_parent_category_id} ---> {parent_id}")
                        else:
                            print(f"❌ Creating relationship from {parent_of_parent_category_id} ---> {parent_id} was unsuccessfull")
                            print(f"With error ---> {res['error']}")
                    else:
                        print(f"❌ Creating parent category for {parent_name} was unsuccessfull")
                        print(f"With error ---> {res['error']}") 
                        
                else:
                    print(f"❗️ Parent category node for ---> '{parent_name}' is already exists with the id: {node_ids[parent_name]}") 
                
                print("\n")
                   
                # --- Create child nodes ---
                for key, child_name in category_data.items():
                    if key.startswith('childCategory'):
                        child_key = (parent_name, child_name)  # unique per parent
                        if child_key not in node_ids:
                            name_for_id = f"{parent_name}_{child_name}"
                            node_id = self.generate_id_for_category(date, parent_of_parent_category_id, name_for_id)
                            print(f"id >>>>>>>>>>>>>> {node_id}")
                            print(f"🔄 Creating child node '{child_name}' for parent '{parent_name}'")
                            date_for_id_u = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                            year_u = date_for_id_u.strftime("%Y")
                            month_day_u = date_for_id_u.strftime("%m-%d")
                            child_name_unique = f"{child_name}_{year_u}_{month_day_u}"
                            res = self.create_nodes(node_id, child_name_unique, key, date)
                            if res.get("id"):
                                count += 1
                                node_id = res['id']
                                node_ids[child_key] = node_id
                                print(f"✅ Created child node '{child_name}' with id: {node_id} for parent '{parent_name}'")   
                                child_id = node_ids[child_key]
                                parent_id = node_ids[parent_name]
                                # --- Create relationship ---
                                print(f"🔄 Creating relationship from {parent_name} ---> {child_name}")
                                res = self.create_relationships(parent_id, child_id, date)
                                if res['relationships'][0]:
                                    print(f"✅ Created relationship from {parent_name} ---> {child_name}")
                                    print(f"🔄 Creating attribute for {child_name} ---> {attribute_name}")
                                    attribute_name_for_table_name = self.format_attribute_name_for_table_name(attribute_name)
                                    attribute_name_as_human_readable = self.format_attribute_name_as_human_readable(attribute_name)
                                    print(f"  --Attribute name (Human readable) - {attribute_name_as_human_readable}")
                                    print(f"  --Formatted attribute name for table name - {attribute_name_for_table_name}")
                                    attribute_name_for_table_name = f"{attribute_name_for_table_name}_{year_u}_{node_id}"
                                    res = self.create_attribute_to_entity(date, child_id, attribute_name_for_table_name, attribute_data)
                                    if res.get('id'):
                                        print(f"✅ Created attribute for {child_name} with attribute id {res['id']}")
                                        print(f"🔄 Storing metadata for {child_name}")
                                        metadata = {
                                            "key" : attribute_name_for_table_name,
                                            "value": attribute_name_as_human_readable
                                        }
                                        if child_id in metadata_dict:
                                            metadata_dict[child_id].append(metadata)
                                        else:
                                            metadata_dict[child_id] = [metadata]
                                        
                                        print(f"✅ Storing metadata for {child_name} successfull")
                                        
                                    else:
                                        print(f"❌ Creating attribute for {child_name} was unsuccessfull")
                                        print(f"With error ---> {res['error']}")     
                                else:
                                    print(f"❌ Creating relationship from {parent_name} ---> {child_name} was unsuccessfull")
                                    print(f"With error ---> {res['error']}")
                            else:
                                print(f"❌ Creating child node {child_name} was unsuccessfull")
                                print(f"With error ---> {res['error']}")  
                        else:
                            print(f"❗️ Child node '{child_name}' for parent '{parent_name}' already exists with id: {node_ids[child_key]}")    
                            
                print("=" * 200)   
                
            else:
                if 'minister' and 'department' in item:
                    parent_of_attribute = item["department"]
                    print("❗️ Attribute directly connects to a Department") 
                elif 'minister' in item:
                    parent_of_attribute = item["minister"]
                    print("❗️ Attribute directly connected to a Ministry")
                     
                attribute_name = item['attributeName']
                attribute_data = item['attributeData']
                attribute_name_for_table_name = self.format_attribute_name_for_table_name(attribute_name)
                attribute_name_as_human_readable = self.format_attribute_name_as_human_readable(attribute_name)
                print(f"  --Attribute name (Human readable) - {attribute_name_as_human_readable}")
                print(f"  --Formatted attribute name for table name - {attribute_name_for_table_name}")
                print(f"🔄 Creating attribute for {parent_of_attribute} ---> {attribute_name}")
                date_for_id_u = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                year_u = date_for_id_u.strftime("%Y")
                month_day_u = date_for_id_u.strftime("%m-%d")
                attribute_name_for_table_name = f"{attribute_name_for_table_name}_{year_u}_{parent_of_attribute}"
                res = self.create_attribute_to_entity(date, parent_of_attribute, attribute_name_for_table_name, attribute_data)
                if res.get('id'):
                    print(f"✅ Created attribute for {parent_of_attribute} with attribute id {res['id']}")
                    print(f"🔄 Storing metadata for {parent_of_attribute}")
                    metadata = {
                         "key": attribute_name_for_table_name,
                         "value": attribute_name_as_human_readable
                    }
                    # If entity already exists, append; else create a new list
                    if parent_of_attribute in metadata_dict:
                        metadata_dict[parent_of_attribute].append(metadata)
                    else:
                        metadata_dict[parent_of_attribute] = [metadata]
                        
                    print(f"✅ Storing metadata for {parent_of_attribute} successfull")
                    
                else:
                    print(f"❌ Creating attribute for {parent_of_attribute} was unsuccessfull")
                    print(f"With error ---> {res['error']}")
                    
                print("=" * 200) 
            
        self.create_metadata_to_entities(metadata_dict)
                 
        return
    
    def extract_existing_metadata_from_entity(self, entity_id):
        url = f"http://0.0.0.0:8081/v1/entities/{entity_id}/metadata"
        
        headers = {
            "Content-Type": "application/json",
            # "Authorization": f"Bearer {token}"  
        }
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()  
            metadata = response.json()
            return metadata
        
        except Exception as e:
            print(f"Error extracting existing metadata from entity {entity_id}")
            print(f"Error: {e}")
            return {}
    
    def create_metadata_to_entities(self, metadata_dict):
        for entity_id, metadata in metadata_dict.items():
            print(f"🔄 Creating metadata for entity {entity_id}")
            print(f"Extracting existing metadata from entity {entity_id}")
            existing_metadata = self.extract_existing_metadata_from_entity(entity_id)
            print(f"Existing metadata: {existing_metadata}")
            
            # Handle case where existing_metadata is empty
            if existing_metadata:
                for key, value in existing_metadata.items():
                    decoded_value = self.decode_protobuf(value)
                    existing_metadata[key] = decoded_value
                existing_metadata_list = [{'key': key, 'value': value} for key, value in existing_metadata.items()]
            else:
                print("No existing metadata found - using empty list")
                existing_metadata_list = []

            print(f"Metadata to be added: {metadata}")
            metadata = existing_metadata_list + metadata
            print(f"Concatenated Metadata: {metadata}")
            res = self.create_metadata_to_entity(entity_id, metadata)
            if res.get('id'):
                print(f"✅ Created metadata for entity {entity_id} successfully")
            else:
                print(f"❌ Creating metadata for entity {entity_id} was unsuccessfull")
                print(f"With error ---> {res['error']}")
        return
    
    def create_parent_categories_and_children_categories_v2(self, result):
        count = 0
        node_ids = {}  
        metadata_dict = {}
        
        print(f"Total items to process: {len(result)}")
        
        print("=" * 200)
    
        for item in result:
            
            date = item["attributeReleaseDate"]
            if 'categoryData' in item:
                category_data = item['categoryData']

                # --- Create parent node ---
                parent_name = category_data['parentCategory']
                
                # Fix: Properly check for both minister and department
                if 'minister' in item and 'department' in item:
                    parent_of_parent_category_id = item["department"]
                    print(f"🔄 Using department as parent: {parent_of_parent_category_id}")
                elif 'minister' in item:
                    parent_of_parent_category_id = item["minister"]
                    print(f"🔄 Using minister as parent: {parent_of_parent_category_id}")
                else:
                    print(f"❌ No minister or department found in item")
                    continue
                
                attribute_name = item['attributeName']  
                attribute_data = item['attributeData']
                
                if parent_name not in node_ids:
                    parent_node_id = self.generate_id_for_category(date, parent_of_parent_category_id, parent_name)
                    print(f"id >>>>>>>>>>>>>> {parent_node_id}")
                    print(f"🔄 Creating parent category node for ---> '{parent_name}'")
                    date_for_id_u = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                    year_u = date_for_id_u.strftime("%Y")
                    month_day_u = date_for_id_u.strftime("%m-%d")
                    parent_name_unique = f"{parent_name}_{year_u}_{month_day_u}"
                    res = self.create_nodes(parent_node_id, parent_name_unique, 'parentCategory', date)
                    if res.get('id'):
                        count += 1
                        created_parent_id = res['id']
                        node_ids[parent_name] = created_parent_id
                        print(f"✅ Created parent category node for ---> '{parent_name}' with id: {created_parent_id}")
                        print(f"🔄 Creating relationship from {parent_of_parent_category_id} ---> {created_parent_id}")
                        res = self.create_relationships(parent_of_parent_category_id, created_parent_id, date)
                        if res.get('id'):
                            print(f"✅ Created relationship from {parent_of_parent_category_id} ---> {created_parent_id}")
                        else:
                            print(f"❌ Creating relationship from {parent_of_parent_category_id} ---> {created_parent_id} was unsuccessfull")
                            print(f"With error ---> {res['error']}")
                    else:
                        print(f"❌ Creating parent category for {parent_name} was unsuccessfull")
                        print(f"With error ---> {res['error']}") 
                        
                else:
                    print(f"❗️ Parent category node for ---> '{parent_name}' already exists with the id: {node_ids[parent_name]}") 
                
                print("\n")
                   
                # --- Create child nodes ---
                for key, child_name in category_data.items():
                    if key.startswith('childCategory'):
                        child_key = (parent_name, child_name)  # unique per parent
                        if child_key not in node_ids:
                            name_for_id = f"{parent_name}_{child_name}"
                            child_node_id = self.generate_id_for_category(date, parent_of_parent_category_id, name_for_id)
                            print(f"id >>>>>>>>>>>>>> {child_node_id}")
                            print(f"🔄 Creating child node '{child_name}' for parent '{parent_name}'")
                            date_for_id_u = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                            year_u = date_for_id_u.strftime("%Y")
                            month_day_u = date_for_id_u.strftime("%m-%d")
                            child_name_unique = f"{child_name}_{year_u}_{month_day_u}"
                            res = self.create_nodes(child_node_id, child_name_unique, key, date)
                            if res.get("id"):
                                count += 1
                                created_child_id = res['id']
                                node_ids[child_key] = created_child_id
                                print(f"✅ Created child node '{child_name}' with id: {created_child_id} for parent '{parent_name}'")   
                                parent_id = node_ids[parent_name]
                                # --- Create relationship ---
                                print(f"🔄 Creating relationship from {parent_name} ---> {child_name}")
                                res = self.create_relationships(parent_id, created_child_id, date)
                                # Fix: Check if relationships exist and are valid
                                if res.get('id') and res.get('relationships') and len(res['relationships']) > 0:
                                    print(f"✅ Created relationship from {parent_name} ---> {child_name}")
                                    print(f"🔄 Creating attribute for {child_name} ---> {attribute_name}")
                                    attribute_name_for_table_name = self.format_attribute_name_for_table_name(attribute_name)
                                    attribute_name_as_human_readable = self.format_attribute_name_as_human_readable(attribute_name)
                                    print(f"  --Attribute name (Human readable) - {attribute_name_as_human_readable}")
                                    print(f"  --Formatted attribute name for table name - {attribute_name_for_table_name}")
                                    attribute_name_for_table_name = f"{attribute_name_for_table_name}_{year_u}_{created_child_id}"
                                    res = self.create_attribute_to_entity(date, created_child_id, attribute_name_for_table_name, attribute_data)
                                    if res.get('id'):
                                        print(f"✅ Created attribute for {child_name} with attribute id {res['id']}")
                                        print(f"🔄 Storing metadata for {child_name}")
                                        
                                        metadata = {
                                            "key" : attribute_name_for_table_name,
                                            "value": attribute_name_as_human_readable
                                        }
                                        parent_cat = {
                                            "key": "parent_of_parent_category_id",
                                            "value": parent_of_parent_category_id
                                        }
                                        if created_child_id in metadata_dict:
                                            metadata_dict[created_child_id].append(metadata)
                                        else:
                                            metadata_dict[created_child_id] = [metadata, parent_cat]
                                            
                                    
                                        print(f"✅ Storing metadata for {child_name} successfull")
                                        
                                    else:
                                        print(f"❌ Creating attribute for {child_name} was unsuccessfull")
                                        print(f"With error ---> {res['error']}")     
                                else:
                                    print(f"❌ Creating relationship from {parent_name} ---> {child_name} was unsuccessfull")
                                    print(f"With error ---> {res.get('error', 'Unknown error')}")
                            else:
                                print(f"❌ Creating child node {child_name} was unsuccessfull")
                                print(f"With error ---> {res['error']}")  
                        else:
                            print(f"❗️ Child node '{child_name}' for parent '{parent_name}' already exists with id: {node_ids[child_key]}")    
                            
                print("=" * 200)   
                
            else:
                # Handle items without categoryData (existing logic)
                if 'minister' in item and 'department' in item:
                    parent_of_attribute = item["department"]
                    print("❗️ Attribute directly connects to a Department") 
                elif 'minister' in item:
                    parent_of_attribute = item["minister"]
                    print("❗️ Attribute directly connected to a Ministry")
                else:
                    print("❌ No minister or department found in item")
                    continue
                     
                attribute_name = item['attributeName']
                attribute_data = item['attributeData']
                attribute_name_for_table_name = self.format_attribute_name_for_table_name(attribute_name)
                attribute_name_as_human_readable = self.format_attribute_name_as_human_readable(attribute_name)
                print(f"  --Attribute name (Human readable) - {attribute_name_as_human_readable}")
                print(f"  --Formatted attribute name for table name - {attribute_name_for_table_name}")
                print(f"🔄 Creating attribute for {parent_of_attribute} ---> {attribute_name}")
                date_for_id_u = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                year_u = date_for_id_u.strftime("%Y")
                month_day_u = date_for_id_u.strftime("%m-%d")
                attribute_name_for_table_name = f"{attribute_name_for_table_name}_{year_u}_{parent_of_attribute}"
                res = self.create_attribute_to_entity(date, parent_of_attribute, attribute_name_for_table_name, attribute_data)
                if res.get('id'):
                    print(f"✅ Created attribute for {parent_of_attribute} with attribute id {res['id']}")
                    print(f"🔄 Storing metadata for {parent_of_attribute}")
                    metadata = {
                         "key": attribute_name_for_table_name,
                         "value": attribute_name_as_human_readable
                    }
                    parent_cat = {
                        "key": "parent_of_parent_category_id",
                        "value": parent_of_attribute
                    }
                    # If entity already exists, append; else create a new list
                    if parent_of_attribute in metadata_dict:
                        metadata_dict[parent_of_attribute].append(metadata)
                    else:
                        metadata_dict[parent_of_attribute] = [metadata, parent_cat]
                        
                    print(f"✅ Storing metadata for {parent_of_attribute} successfull")
                    
                else:
                    print(f"❌ Creating attribute for {parent_of_attribute} was unsuccessfull")
                    print(f"With error ---> {res['error']}")
                    
                print("=" * 200) 
            
        self.create_metadata_to_entities(metadata_dict)
                 
        return
    
    def connect_to_mongodb(self):
        try:
            # Create a MongoDB client
            client = MongoClient(self.config['MONGODB_URI'])

            client.admin.command('ping')
            db = client.doc_db
            collection_names = db.list_collection_names()
            
            print("✅ Connected to MongoDB successfully!")
            return True , collection_names , db
        except ConnectionFailure as e:
            print(f"❌ Could not connect to MongoDB: {e}")
            return False
    
    def get_all_documents_from_nexoan(self):
        url = f"{self.config['BASE_URL_QUERY']}/v1/entities/search"
        
        payload = {
            "kind": {
                "major": "Document",
                "minor": ""
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            # "Authorization": f"Bearer {token}"  
        }
        
        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()  
            documents = response.json()
            return documents['body']
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []
        return documents['body']
    
    def categorise_documents_by_year(self, documents):
        grouped_by_year = {}
        for document in documents:
            year = document['created'].split('-')[0]
            grouped_by_year.setdefault(year, []).append(document)
        return grouped_by_year
    
    def add_metadata_to_the_document(self, categorised_documents, db):
        
        for year, documents in categorised_documents.items():
            
            collection_name = f"gazettes_{year}"
            collection = db[collection_name]
            
            print(f"\nChecking collection: {collection_name}")
            
            for doc in documents:
                doc_id = doc.get("id")
                print(f"Document id: {doc_id}")
                
                document_no = doc.get("name")
                decoded_document_no = self.decode_protobuf(document_no)
                print(decoded_document_no)
                
                print(f"Extracted document id: {decoded_document_no}")
                existing_doc = collection.find_one({"document_id": decoded_document_no})
                metadata_list = []
                if existing_doc:
                    print(f"Document exists in collection: {collection_name} with id: {decoded_document_no}")
                    
                    for key, value in existing_doc.items():
                        if key == "_id" or key == "document_id" or key == "document_date":
                            continue
                        metadata_list.append({"key": key, "value": value})
                    
                    print(metadata_list)
                    
                    print(f"Creating metadata for document: {doc_id}")
                    res = self.create_metadata_to_entity(doc_id, metadata_list)
                    if res.get('metadata') and len(res.get('metadata')) == len(metadata_list):
                        print(f"✅ Created metadata for document: {doc_id}")
                    else:
                        print(f"❌ Creating metadata for document: {doc_id} was unsuccessfull")
                else:
                    print(f"Document does not exist in collection: {collection_name}")
                
                print("=" * 200)
            
            print("=" * 200)
            
        return
    
    def decode_protobuf(self, name : str) -> str:
        try:
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
                cleaned = ''.join(ch for ch in decoded_str if ch.isprintable())
                return cleaned.strip()
        except Exception as e:
            print(f"[DEBUG decode] outer exception: {e}")
            return ""

if __name__ == "__main__":
    config = {
        'MONGODB_URI': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'),
        'BASE_URL_QUERY': 'http://0.0.0.0:8081'
    }
    
    client = WriteAttributes(config)
    
    parser = argparse.ArgumentParser(description="Ingest attributes from data folder.")
    parser.add_argument("--year", type=str, help="Specific year to process (e.g., 2023)", default=None)
    args = parser.parse_args()
    
    # Example usage
    base_path = "data" 
    if os.path.exists(base_path):
        print(f"Traversing {base_path}..." + (f" for year {args.year}" if args.year else ""))
        data = client.traverse_folder(base_path, year_filter=args.year)
        print("Preprocessing data...")
        data = client.pre_process_traverse_result(data)
        print("Validating entities...")
        data = client.entity_validator(data)
        
        print("Creating categories and inserting data...")
        client.create_categories_and_insert_datasets(data)
    else:
        print(f"Data directory '{base_path}' not found.")
