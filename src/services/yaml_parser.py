import yaml
import os
import re
from typing import Dict, List, Any, Optional


class YamlParser:
    """
    Parser for YAML manifest files that define the structure of datasets
    organized by ministers, departments, categories, and subcategories.
    """
    
    # parse a yaml file and return the parsed content as a dictionary.
    @staticmethod
    def parse_manifest(yaml_path: str) -> Dict[str, Any]:

        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        
        if content is None:
            raise ValueError(f"YAML file is empty or invalid: {yaml_path}")
        
        return content
    
    # Extract the year from a YAML filename.
    # Expected format: manifest_YYYY.yaml or similar patterns containing a 4-digit year.
    @staticmethod
    def extract_year_from_filename(filename: str) -> str:

        # Extract just the filename if a path is provided
        basename = os.path.basename(filename)
        
        # Look for a 4-digit year pattern
        match = re.search(r'\b(19|20)\d{2}\b', basename)
        if match:
            return match.group(0)
        
        raise ValueError(f"Could not extract year from filename: {filename}")
    
    
    # Extract the list of ministers from the parsed manifest.
    @staticmethod
    def get_ministers(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        if 'minister' not in manifest:
            raise ValueError("Manifest does not contain 'minister' key")
        
        ministers = manifest['minister']

        # if there's only one minister, wrap in a list
        if not isinstance(ministers, list):
            return [ministers] if ministers else []
        return ministers
    
    # Check if a minister entry has departments (vs. direct categories).
    @staticmethod
    def has_departments(minister_entry: Dict[str, Any]) -> bool:
        return 'department' in minister_entry and minister_entry['department'] is not None
    
    # Check if an entry has categories.
    @staticmethod
    def has_categories(entry: Dict[str, Any]) -> bool:
        return 'category' in entry and entry['category'] is not None
    
    # Get the list of department dictionaries for a minister entry - department name and categories/datasets below it.
    @staticmethod
    def get_departments(minister_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not YamlParser.has_departments(minister_entry):
            return []
        
        departments = minister_entry['department']

        # if there's only one department, wrap in a list
        if not isinstance(departments, list):
            return [departments] if departments else []
        
        return departments
    
    # Get the list of category dictionaries from an entry.
    @staticmethod
    def get_categories(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        if 'category' not in entry or entry['category'] is None:
            return []
        
        categories = entry['category']

        # if there's only one category, wrap in a list
        if not isinstance(categories, list):
            return [categories] if categories else []
        
        return categories
    
    # Get the list of subcategory dictionaries from a category or subcategory entry.
    @staticmethod
    def get_subcategories(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        if 'subcategory' not in entry or entry['subcategory'] is None:
            return []
        
        subcategories = entry['subcategory']

        # if there's only one subcategory, wrap in a list
        if not isinstance(subcategories, list):
            return [subcategories] if subcategories else []
        
        return subcategories
    
    # Get the list of dataset paths from a category or subcategory entry.
    @staticmethod
    def get_datasets(entry: Dict[str, Any]) -> List[str]:

        if 'datasets' not in entry or entry['datasets'] is None:
            return []
        
        datasets = entry['datasets']

        # if there's only one dataset, wrap in a list
        if not isinstance(datasets, list):
            return [datasets] if datasets else []
        
        return datasets
    
    # Check if an entry has subcategories.
    @staticmethod
    def has_subcategories(entry: Dict[str, Any]) -> bool:
        return 'subcategory' in entry and entry['subcategory'] is not None
    
    # Check if an entry has datasets.
    @staticmethod
    def has_datasets(entry: Dict[str, Any]) -> bool:
        return 'datasets' in entry and entry['datasets'] is not None
