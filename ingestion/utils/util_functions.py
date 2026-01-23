import binascii
import json
import re
from datetime import datetime
from google.protobuf.wrappers_pb2 import StringValue

class Util:
    # helper: decode protobuf attribute name 
    @staticmethod      
    def decode_protobuf_attribute_name(name : str) -> str: 
            try:
                data = json.loads(name)
                hex_value = data.get("value")
                if not hex_value:
                    return "Unknown"

                decoded_bytes = binascii.unhexlify(hex_value)
                
                sv = StringValue()
                try:
                    sv.ParseFromString(decoded_bytes)
                    if(sv.value.strip() == ""):
                        return decoded_bytes.decode("utf-8", errors="ignore").strip()
                    return sv.value.strip()
                except Exception:
                    decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                    cleaned = ''.join(ch for ch in decoded_str if ch.isprintable())
                    return cleaned.strip()
            except Exception as e:
                print(f"[DEBUG decode] outer exception: {e}")
                return "Unknown"

    @staticmethod
    def validate_tabular_dataset(data_content: dict) -> bool:
        """
        Validate the structure of a dataset JSON content.
        
        Validates:
        - data_content is a dictionary
        - Has 'columns' key that is a non-empty list
        - Has 'rows' key that is a list
        - Each row is a list
        - All rows have the same number of columns (matching columns length)
        
        Args:
            data_content: Dictionary containing dataset data with 'columns' and 'rows' keys
            
        Returns:
            True if validation passes, False otherwise
        """
        # Validate structure: must have columns and rows
        if not isinstance(data_content, dict):
            print(f"        [ERROR] data.json is not a dictionary")
            return False
        
        columns = data_content.get('columns')
        rows = data_content.get('rows')
        
        if not isinstance(columns, list):
            print(f"        [ERROR] 'columns' in data.json is not a list")
            return False
        
        if not isinstance(rows, list):
            print(f"        [ERROR] 'rows' in data.json is not a list")
            return False
        
        if not columns:
            print(f"        [ERROR] 'columns' list is empty")
            return False
        
        if not rows:
            print(f"        [ERROR] 'rows' list is empty")
            return False
        
        expected_column_count = len(columns)
        
        # Validate rows structure (each row must be a list with same number of columns)
        for i, row in enumerate(rows):
            if not isinstance(row, list):
                print(f"        [ERROR] Row {i} is not a list")
                return False
            if len(row) != expected_column_count:
                print(f"        [ERROR] Row {i} has {len(row)} values but expected {expected_column_count}")
                return False
        
        return True

    # Format name to human readable title case
    @staticmethod
    def format_attribute_name(name: str) -> str:
        # Replace underscores and hyphens with spaces
        formatted = name.replace('_', ' ').replace('-', ' ')
        # Remove extra whitespace and convert to title case
        formatted = ' '.join(formatted.split())
        formatted = formatted.title()
        return formatted

    