import os
import requests
import argparse
import json
import binascii
from google.protobuf.wrappers_pb2 import StringValue

class Verifier:
    def __init__(self, config):
        self.config = config
        self.base_url = config.get("BASE_URL_QUERY", "http://0.0.0.0:8081")

    def decode_protobuf(self, name_input) -> str:
        val_str = ""
        if isinstance(name_input, dict):
            val_str = name_input.get("value", "")
        elif isinstance(name_input, str):
            try:
                data = json.loads(name_input)
                if isinstance(data, dict):
                     val_str = data.get("value", "")
                else: 
                     val_str = name_input
            except:
                val_str = name_input
        
        if not val_str:
            return ""

        try:
            decoded_bytes = binascii.unhexlify(val_str)
        except (binascii.Error, ValueError):
             return val_str
             
        try:
            return decoded_bytes.decode('utf-8')
        except UnicodeDecodeError:
            pass
            
        sv = StringValue()
        try:
            sv.ParseFromString(decoded_bytes)
            if sv.value:
                return sv.value
        except Exception:
             pass
        
        decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
        cleaned = ''.join(ch for ch in decoded_str if ch.isprintable())
        return cleaned.strip()

    def format_attribute_name_as_human_readable(self, name):
        # User requested to NOT make it human readable, but check for existence.
        #However, keeping this helper in case needed, but logic will change.
        formatted = name.replace("_", " ").replace("-", " ") 
        return formatted.title()

    def get_local_datasets(self, base_path, year_filter=None):
        dataset_counts = {}
        base_path = os.path.abspath(base_path)
        print(f"Traversing {base_path}...")
        for root, dirs, files in os.walk(base_path):
            if year_filter and root == base_path:
                if year_filter in dirs:
                    dirs[:] = [year_filter]
                else:
                    dirs[:] = []
                    continue
            
            if 'data.json' in files:
                # Find nearest parent with (AS_CATEGORY)
                curr = root
                found_cat = False
                while curr.startswith(base_path) and curr != base_path:
                    dirname = os.path.basename(curr)
                    if dirname.endswith("(AS_CATEGORY)"):
                        cat_name = dirname.replace("(AS_CATEGORY)", "")
                        dataset_counts[cat_name] = dataset_counts.get(cat_name, 0) + 1
                        found_cat = True
                        break
                    curr = os.path.dirname(curr)
                
                if not found_cat:
                    # Fallback to direct parent if no AS_CATEGORY found
                    parent = os.path.basename(root)
                    dataset_counts[parent] = dataset_counts.get(parent, 0) + 1

        return dataset_counts

    def get_category_name(self, entity_id):
        url = f"{self.base_url}/v1/entities/search"
        payload = {"id": entity_id}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                body = response.json().get("body", [])
                if body:
                    entity = body[0]
                    kind = entity.get("kind", {})
                    if kind.get("major") == "Category":
                        name_struct = entity.get("name", {})
                        # Return RAW value, do not format
                        return self.decode_protobuf(name_struct)
            return None
        except:
            return None

    def get_parent_category_name(self, dataset_id):
        url = f"{self.base_url}/v1/entities/{dataset_id}/relations"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json={}, headers=headers) 
            response.raise_for_status()
            relations = response.json() 
            
            for rel in relations:
                if rel.get("direction") == "INCOMING":
                    related_id = rel.get("relatedEntityId")
                    cat_name = self.get_category_name(related_id)
                    if cat_name:
                         return cat_name
            return None
        except Exception:
            return None

    def get_remote_datasets(self, major_kind="Dataset", year_filter=None):
        url = f"{self.base_url}/v1/entities/search"
        payload = {
            "kind": {
                "major": major_kind,
                "minor": "" 
            }
        }
        headers = {"Content-Type": "application/json"}
        
        dataset_counts = {}
        
        try:
            print(f"Searching OpenGIN for entities with kind.major='{major_kind}'...")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "body" in data:
                entities = data["body"]
                print(f"Found {len(entities)} raw entities. Tracing parent categories...")
                
                for i, entity in enumerate(entities):
                    entity_id = entity.get("id")
                    
                    # Filter by year if provided
                    if year_filter:
                         created_date = entity.get("created", "")
                         if not created_date or year_filter not in created_date:
                             continue

                    if entity_id:
                        parent_name = self.get_parent_category_name(entity_id)
                        if parent_name:
                            dataset_counts[parent_name] = dataset_counts.get(parent_name, 0) + 1
                            
            return dataset_counts

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to OpenGIN: {e}")
            return None

    def verify(self, base_path, year_filter=None):
        local_counts = self.get_local_datasets(base_path, year_filter)
        total_local = sum(local_counts.values())
        print(f"Found {total_local} local datasets across {len(local_counts)} categories.")
        
        target_kind = "Dataset"
        remote_counts = self.get_remote_datasets(target_kind, year_filter)
        
        if remote_counts is None:
            print("Verification failed due to API error.")
            return

        total_remote = sum(remote_counts.values())
        print(f"Found {total_remote} datasets in OpenGIN across {len(remote_counts)} parent categories.")
        
        print("\n--- Detailed Verification ---")
        
        all_cats = set(local_counts.keys()) | set(remote_counts.keys())
        missing_datasets = 0
        
        for cat in sorted(all_cats):
            l_c = local_counts.get(cat, 0)
            r_c = remote_counts.get(cat, 0)
            status = "✅" if l_c == r_c else "❌"
            if l_c != r_c:
                missing_datasets += abs(l_c - r_c) 
            
            print(f"{status} Category '{cat}': Local={l_c}, Remote={r_c}")

        # Check 1: Category-wise discrepancy
        # Check 2: Total count match
        if missing_datasets == 0 and total_local == total_remote:
             print(f"\n✅ Verification SUCCESS: Exact match found (Local={total_local}, Remote={total_remote}).")
        else:
             print(f"\n❌ Verification FAILED: Found discrepancies.")
             if total_local != total_remote:
                 print(f"   - Total count mismatch: Local={total_local} vs Remote={total_remote}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify data ingestion.")
    parser.add_argument("--dir", type=str, default="data", help="Data directory path")
    parser.add_argument("--year", type=str, help="Specific year to verify (affects local count only)", default=None)
    parser.add_argument("--url", type=str, default="http://0.0.0.0:8081", help="OpenGIN Query API URL")
    
    args = parser.parse_args()
    
    config = {
        "BASE_URL_QUERY": args.url
    }
    
    verifier = Verifier(config)
    
    if os.path.exists(args.dir):
        verifier.verify(args.dir, args.year)
    else:
        print(f"Directory '{args.dir}' not found.")
