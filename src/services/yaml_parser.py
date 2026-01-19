import yaml
import os
import re
from typing import Dict, List, Any, Optional


class YamlParser:
    """
    Parser for YAML manifest files that define the structure of datasets
    organized by ministers, departments, categories, and subcategories.
    """
    
    @staticmethod
    def parse_manifest(yaml_path: str) -> Dict[str, Any]:
        """
        Load and parse a YAML manifest file.
        
        Args:
            yaml_path: Path to the YAML manifest file
            
        Returns:
            Parsed YAML content as a dictionary
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            yaml.YAMLError: If the YAML file is malformed
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        
        if content is None:
            raise ValueError(f"YAML file is empty or invalid: {yaml_path}")
        
        return content
    
    @staticmethod
    def extract_year_from_filename(filename: str) -> str:
        """
        Extract the year from a YAML filename.
        
        Expected format: manifest_YYYY.yaml or similar patterns containing a 4-digit year.
        
        Args:
            filename: The filename (can be just the name or full path)
            
        Returns:
            The year as a string (e.g., "2020")
            
        Raises:
            ValueError: If no valid year is found in the filename
        """
        # Extract just the filename if a path is provided
        basename = os.path.basename(filename)
        
        # Look for a 4-digit year pattern
        match = re.search(r'\b(19|20)\d{2}\b', basename)
        if match:
            return match.group(0)
        
        raise ValueError(f"Could not extract year from filename: {filename}")
    
    @staticmethod
    def get_ministers(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract the list of ministers from the parsed manifest.
        
        Each minister entry contains:
        - name: The minister's name
        - department: (optional) List of departments
        
        Note: While YAML may show categories directly under ministers, in the database
        structure categories are always under departments. If a minister entry has
        categories in the YAML, they should be processed as if under a department.
        
        Args:
            manifest: The parsed YAML content
            
        Returns:
            List of minister dictionaries, each containing name and optionally departments
            
        Raises:
            ValueError: If the manifest doesn't have the expected structure
        """
        if 'minister' not in manifest:
            raise ValueError("Manifest does not contain 'minister' key")
        
        ministers = manifest['minister']
        
        if not isinstance(ministers, list):
            raise ValueError("'minister' key should contain a list")
        
        return ministers
    
    @staticmethod
    def has_departments(minister_entry: Dict[str, Any]) -> bool:
        """
        Check if a minister entry has departments (vs. direct categories).
        
        Args:
            minister_entry: A single minister dictionary from the manifest
            
        Returns:
            True if the minister has departments, False if it has direct categories
        """
        return 'department' in minister_entry and minister_entry['department'] is not None
    
    @staticmethod
    def has_categories(entry: Dict[str, Any]) -> bool:
        """
        Check if an entry has categories.
        
        Categories can ONLY be under:
        - Department entries
        
        Categories cannot be under ministers or nested under other categories.
        Note: While YAML may show categories under ministers, in the database structure
        categories are always under departments.
        
        Args:
            entry: A dictionary that may contain categories (department only)
            
        Returns:
            True if the entry contains categories, False otherwise
        """
        return 'category' in entry and entry['category'] is not None
    
    @staticmethod
    def get_departments(minister_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the list of departments for a minister entry.
        
        Args:
            minister_entry: A single minister dictionary from the manifest
            
        Returns:
            List of department dictionaries, each containing name and category structure
        """
        if not YamlParser.has_departments(minister_entry):
            return []
        
        departments = minister_entry['department']
        if not isinstance(departments, list):
            return [departments] if departments else []
        
        return departments
    
    @staticmethod
    def get_categories(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the list of categories from an entry.
        
        Categories can ONLY be under:
        - Department entries
        
        Categories cannot be under ministers or nested under other categories.
        Note: While YAML may show categories under ministers, in the database structure
        categories are always under departments.
        
        Args:
            entry: A dictionary that may contain categories (department only)
            
        Returns:
            List of category dictionaries
        """
        if 'category' not in entry or entry['category'] is None:
            return []
        
        categories = entry['category']
        if not isinstance(categories, list):
            return [categories] if categories else []
        
        return categories
    
    @staticmethod
    def get_subcategories(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the list of subcategories from a category or subcategory entry.
        
        Subcategories can ONLY be under:
        - Category entries
        - Other subcategory entries (nested subcategories)
        
        Subcategories cannot be directly under ministers or departments.
        
        Args:
            entry: A category or subcategory dictionary
            
        Returns:
            List of subcategory dictionaries
        """
        if 'subcategory' not in entry or entry['subcategory'] is None:
            return []
        
        subcategories = entry['subcategory']
        if not isinstance(subcategories, list):
            return [subcategories] if subcategories else []
        
        return subcategories
    
    @staticmethod
    def get_datasets(entry: Dict[str, Any]) -> List[str]:
        """
        Get the list of dataset paths from a category or subcategory entry.
        
        Datasets can be directly under:
        - Category entries
        - Subcategory entries
        
        Args:
            entry: A category or subcategory dictionary that may contain datasets
            
        Returns:
            List of dataset path strings
        """
        if 'datasets' not in entry or entry['datasets'] is None:
            return []
        
        datasets = entry['datasets']
        if not isinstance(datasets, list):
            return [datasets] if datasets else []
        
        return datasets
    
    @staticmethod
    def has_subcategories(entry: Dict[str, Any]) -> bool:
        """
        Check if an entry (category or subcategory) has subcategories.
        
        Args:
            entry: A category or subcategory dictionary
            
        Returns:
            True if the entry contains subcategories, False otherwise
        """
        return 'subcategory' in entry and entry['subcategory'] is not None
    
    @staticmethod
    def has_datasets(entry: Dict[str, Any]) -> bool:
        """
        Check if an entry (category or subcategory) has datasets.
        
        Args:
            entry: A category or subcategory dictionary
            
        Returns:
            True if the entry contains datasets, False otherwise
        """
        return 'datasets' in entry and entry['datasets'] is not None
