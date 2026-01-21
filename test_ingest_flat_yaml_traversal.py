"""
Tests for traversal functionality in ingest_flat_yaml.py

These tests focus on verifying that the traversal functions correctly
navigate through the YAML structure (categories, subcategories, datasets).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

# Import the functions to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingest_flat_yaml import (
    process_categories,
    process_subcategories_recursive,
    process_datasets,
    process_department_entry,
    process_minister_entry
)
import ingest_flat_yaml


class TestProcessCategories:
    """Tests for process_categories function"""
    
    @pytest.mark.asyncio
    async def test_process_categories_with_subcategories(self, tmp_path):
        """Test processing categories that contain subcategories"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "parent-123"
        parent_type = "department"
        
        categories = [
            {
                "name": "category1",
                "subcategory": [
                    {
                        "name": "subcat1",
                        "datasets": ["dataset1"]
                    }
                ]
            }
        ]
        
        # Mock both subcategory and dataset processing
        # Use wraps to call the real process_subcategories_recursive
        # so it will actually process and call process_datasets (which we'll mock)
        with patch('ingest_flat_yaml.process_subcategories_recursive', wraps=process_subcategories_recursive) as mock_subcat, \
             patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            
            await process_categories(categories, parent_id, parent_type, yaml_base_path, year)
            
            # Verify subcategory processing was called
            mock_subcat.assert_called_once()
            call_args = mock_subcat.call_args
            assert len(call_args[0][0]) == 1  # One subcategory
            assert call_args[0][0][0]["name"] == "subcat1"
            assert call_args[0][1] == "category1"  # parent_id is category name
            
            # Verify process_datasets was called since subcategory contains a dataset
            mock_datasets.assert_called_once()
            dataset_call_args = mock_datasets.call_args
            assert dataset_call_args[0][0] == ["dataset1"]  # The dataset list
            assert dataset_call_args[0][1] == "subcat1"  # parent_id is subcategory name
    
    @pytest.mark.asyncio
    async def test_process_categories_with_datasets(self, tmp_path):
        """Test processing categories that contain datasets directly"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "parent-123"
        parent_type = "department"
        
        categories = [
            {
                "name": "category1",
                "datasets": ["dataset1", "dataset2"]
            }
        ]
        
        # Mock the dataset processing
        with patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            mock_datasets.return_value = None
            await process_categories(categories, parent_id, parent_type, yaml_base_path, year)
            
            # Verify dataset processing was called
            mock_datasets.assert_called_once()
            call_args = mock_datasets.call_args
            assert call_args[0][0] == ["dataset1", "dataset2"]
            assert call_args[0][1] == "category1"  # parent_id is category name
    
    @pytest.mark.asyncio
    async def test_process_categories_empty_name(self, tmp_path):
        """Test that categories with empty names are skipped"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "parent-123"
        parent_type = "department"
        
        categories = [
            {"name": ""},  # Empty name
            {"name": "valid_category"}
        ]
        
        with patch('ingest_flat_yaml.process_subcategories_recursive') as mock_subcat, \
             patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            await process_categories(categories, parent_id, parent_type, yaml_base_path, year)
            
            # Should only process the valid category
            # Since it has no subcategories or datasets, nothing should be called
            mock_subcat.assert_not_called()
            mock_datasets.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_categories_multiple_categories(self, tmp_path):
        """Test processing multiple categories"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "parent-123"
        parent_type = "department"
        
        categories = [
            {"name": "category1", "datasets": ["dataset1"]},
            {"name": "category2", "subcategory": [{"name": "subcat1"}]},
            {"name": "category3"}
        ]
        
        with patch('ingest_flat_yaml.process_subcategories_recursive') as mock_subcat, \
             patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            await process_categories(categories, parent_id, parent_type, yaml_base_path, year)
            
            # Should process datasets for category1
            assert mock_datasets.call_count == 1
            # Should process subcategories for category2
            assert mock_subcat.call_count == 1


class TestProcessSubcategoriesRecursive:
    """Tests for process_subcategories_recursive function"""
    
    @pytest.mark.asyncio
    async def test_process_subcategories_nested(self, tmp_path):
        """Test processing nested subcategories"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "parent-123"
        
        subcategories = [
            {
                "name": "subcat1",
                "subcategory": [
                    {
                        "name": "nested_subcat1",
                        "datasets": ["dataset1"]
                    }
                ]
            }
        ]
        
        # Track calls to verify recursion
        call_count = {"count": 0}
        
        async def mock_recursive(subcats, parent, base_path, yr):
            call_count["count"] += 1
            if call_count["count"] == 1:
                # First call with subcat1
                assert subcats[0]["name"] == "nested_subcat1"
                assert parent == "subcat1"
        
        with patch('ingest_flat_yaml.process_subcategories_recursive', side_effect=mock_recursive), \
             patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            await process_subcategories_recursive(subcategories, parent_id, yaml_base_path, year)
            
            # Should recursively call for nested subcategory
            assert call_count["count"] == 1
    
    @pytest.mark.asyncio
    async def test_process_subcategories_with_datasets(self, tmp_path):
        """Test processing subcategories that contain datasets"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "parent-123"
        
        subcategories = [
            {
                "name": "subcat1",
                "datasets": ["dataset1", "dataset2"]
            }
        ]
        
        with patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            await process_subcategories_recursive(subcategories, parent_id, yaml_base_path, year)
            
            mock_datasets.assert_called_once()
            call_args = mock_datasets.call_args
            assert call_args[0][0] == ["dataset1", "dataset2"]
            assert call_args[0][1] == "subcat1"
    
    @pytest.mark.asyncio
    async def test_process_subcategories_empty_name(self, tmp_path):
        """Test that subcategories with empty names are skipped"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "parent-123"
        
        subcategories = [
            {"name": ""},  # Empty name
            {"name": "valid_subcat", "datasets": ["dataset1"]}
        ]
        
        with patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            await process_subcategories_recursive(subcategories, parent_id, yaml_base_path, year)
            
            # Should only process the valid subcategory
            mock_datasets.assert_called_once()
            assert mock_datasets.call_args[0][1] == "valid_subcat"
    
    @pytest.mark.asyncio
    async def test_process_subcategories_deeply_nested(self, tmp_path):
        """Test processing deeply nested subcategories"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        parent_id = "level0"
        
        subcategories = [
            {
                "name": "level1",
                "subcategory": [
                    {
                        "name": "level2",
                        "subcategory": [
                            {
                                "name": "level3",
                                "datasets": ["final_dataset"]
                            }
                        ]
                    }
                ]
            }
        ]
        
        call_trace = []
        
        async def mock_recursive(subcats, parent, base_path, yr):
            # Mirror the real implementation: loop through all subcategories
            for subcat in subcats:
                subcat_name = subcat.get('name', '')
                if not subcat_name:
                    continue
                
                # Track this call
                call_trace.append((parent, subcat_name))
                
                # Check for nested subcategories and recurse
                if "subcategory" in subcat:
                    await ingest_flat_yaml.process_subcategories_recursive(
                        subcat["subcategory"],
                        subcat_name,
                        base_path,
                        yr
                    )
        
        with patch('ingest_flat_yaml.process_subcategories_recursive', side_effect=mock_recursive), \
             patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            await process_subcategories_recursive(subcategories, parent_id, yaml_base_path, year)
            
            # Verify the nesting was processed
            # Expected: level0->level1, level1->level2, level2->level3
            assert len(call_trace) >= 2  # At least level1 -> level2 -> level3


class TestProcessDatasets:
    """Tests for process_datasets function"""
    
    @pytest.mark.asyncio
    async def test_process_datasets_single(self, tmp_path):
        """Test processing a single dataset"""
        yaml_base_path = str(tmp_path)
        parent_id = "parent-123"
        
        # Create a test dataset directory
        dataset_dir = tmp_path / "datasets" / "Test Dataset"
        dataset_dir.mkdir(parents=True)
        (dataset_dir / "data.json").write_text("{}")
        (dataset_dir / "metadata.json").write_text("{}")
        
        datasets = ["datasets/Test Dataset"]
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            await process_datasets(datasets, parent_id, str(tmp_path))
            
            # Verify it found the dataset files
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Found data.json" in str(call) for call in print_calls)
            assert any("Found metadata.json" in str(call) for call in print_calls)
    
    @pytest.mark.asyncio
    async def test_process_datasets_multiple(self, tmp_path):
        """Test processing multiple datasets"""
        yaml_base_path = str(tmp_path)
        parent_id = "parent-123"
        
        # Create test dataset directories
        (tmp_path / "datasets" / "Dataset1").mkdir(parents=True)
        (tmp_path / "datasets" / "Dataset2").mkdir(parents=True)
        
        datasets = ["datasets/Dataset1", "datasets/Dataset2"]
        
        with patch('builtins.print') as mock_print:
            await process_datasets(datasets, parent_id, str(tmp_path))
            
            # Should process both datasets
            print_calls = [str(call) for call in mock_print.call_args_list]
            dataset_names = [call for call in print_calls if "[DATASET]" in str(call)]
            assert len([c for c in dataset_names if "Dataset1" in str(c)]) > 0
            assert len([c for c in dataset_names if "Dataset2" in str(c)]) > 0
    
    @pytest.mark.asyncio
    async def test_process_datasets_missing_path(self, tmp_path):
        """Test handling of missing dataset paths"""
        yaml_base_path = str(tmp_path)
        parent_id = "parent-123"
        
        datasets = ["datasets/NonExistent Dataset"]
        
        with patch('builtins.print') as mock_print:
            await process_datasets(datasets, parent_id, str(tmp_path))
            
            # Should print a warning
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("WARNING" in str(call) and "does not exist" in str(call) for call in print_calls)


class TestProcessDepartmentEntry:
    """Tests for process_department_entry function"""
    
    @pytest.mark.asyncio
    async def test_process_department_with_categories(self, tmp_path):
        """Test processing department entry with categories"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        department_id = "dept-123"
        
        department_entry = {
            "name": "Test Department",
            "category": [
                {"name": "category1", "datasets": ["dataset1"]}
            ]
        }
        
        with patch('ingest_flat_yaml.process_categories') as mock_categories:
            await process_department_entry(department_entry, department_id, yaml_base_path, year)
            
            mock_categories.assert_called_once()
            call_args = mock_categories.call_args
            assert call_args[0][1] == department_id
            assert call_args[0][2] == "department"
    
    @pytest.mark.asyncio
    async def test_process_department_with_datasets(self, tmp_path):
        """Test processing department entry with direct datasets"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        department_id = "dept-123"
        
        department_entry = {
            "name": "Test Department",
            "datasets": ["dataset1", "dataset2"]
        }
        
        with patch('ingest_flat_yaml.process_datasets') as mock_datasets:
            await process_department_entry(department_entry, department_id, yaml_base_path, year)
            
            mock_datasets.assert_called_once()
            call_args = mock_datasets.call_args
            assert call_args[0][0] == ["dataset1", "dataset2"]
            assert call_args[0][1] == department_id
    
    @pytest.mark.asyncio
    async def test_process_department_no_categories_or_datasets(self, tmp_path):
        """Test processing department entry with no categories or datasets"""
        yaml_base_path = str(tmp_path)
        year = "2020"
        department_id = "dept-123"
        
        department_entry = {
            "name": "Test Department"
        }
        
        with patch('ingest_flat_yaml.process_categories') as mock_categories, \
             patch('ingest_flat_yaml.process_datasets') as mock_datasets, \
             patch('builtins.print') as mock_print:
            await process_department_entry(department_entry, department_id, yaml_base_path, year)
            
            # Should not process anything, but may print info
            mock_categories.assert_not_called()
            mock_datasets.assert_not_called()


class TestProcessMinisterEntry:
    """Tests for process_minister_entry function"""
    
    @pytest.mark.asyncio
    async def test_process_minister_with_departments(self, tmp_path):
        """Test processing minister entry with departments"""
        year = "2020"
        yaml_base_path = str(tmp_path)
        
        minister_entry = {
            "name": "Test Minister",
            "department": [
                {
                    "name": "Test Department",
                    "category": [{"name": "category1"}]
                }
            ]
        }
        
        # Mock the entity resolver and services
        mock_read_service = MagicMock()
        mock_ingestion_service = MagicMock()
        
        # Mock finding ministers
        async def mock_find_ministers(name, yr, read_svc):
            return [{"minister_id": "minister-123", "start_time": "2020-01-01", "end_time": ""}]
        
        # Mock finding department
        async def mock_find_department(name, ministers, yr, read_svc):
            return "dept-123"
        
        with patch('ingest_flat_yaml.find_ministers_by_name_and_year', side_effect=mock_find_ministers), \
             patch('ingest_flat_yaml.find_department_by_name_and_ministers', side_effect=mock_find_department), \
             patch('ingest_flat_yaml.process_department_entry') as mock_dept:
            await process_minister_entry(
                minister_entry,
                year,
                yaml_base_path,
                mock_read_service,
                mock_ingestion_service
            )
            
            # Should process the department
            mock_dept.assert_called_once()
            call_args = mock_dept.call_args
            assert call_args[0][1] == "dept-123"
    
    @pytest.mark.asyncio
    async def test_process_minister_no_active_ministers(self, tmp_path):
        """Test processing minister entry when no active ministers found"""
        year = "2020"
        yaml_base_path = str(tmp_path)
        
        minister_entry = {
            "name": "Test Minister"
        }
        
        mock_read_service = MagicMock()
        mock_ingestion_service = MagicMock()
        
        # Mock finding no ministers
        async def mock_find_ministers(name, yr, read_svc):
            return []
        
        with patch('ingest_flat_yaml.find_ministers_by_name_and_year', side_effect=mock_find_ministers), \
             patch('builtins.print') as mock_print:
            await process_minister_entry(
                minister_entry,
                year,
                yaml_base_path,
                mock_read_service,
                mock_ingestion_service
            )
            
            # Should print a warning
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("WARNING" in str(call) and "No ministers found" in str(call) for call in print_calls)
    
    @pytest.mark.asyncio
    async def test_process_minister_with_direct_categories(self, tmp_path):
        """Test processing minister entry with direct categories"""
        year = "2020"
        yaml_base_path = str(tmp_path)
        
        minister_entry = {
            "name": "Test Minister",
            "category": [
                {"name": "category1", "datasets": ["dataset1"]}
            ]
        }
        
        mock_read_service = MagicMock()
        mock_ingestion_service = MagicMock()
        
        async def mock_find_ministers(name, yr, read_svc):
            return [{"minister_id": "minister-123", "start_time": "2020-01-01", "end_time": ""}]
        
        with patch('ingest_flat_yaml.find_ministers_by_name_and_year', side_effect=mock_find_ministers), \
             patch('ingest_flat_yaml.process_categories') as mock_categories:
            await process_minister_entry(
                minister_entry,
                year,
                yaml_base_path,
                mock_read_service,
                mock_ingestion_service
            )
            
            # Should process categories
            mock_categories.assert_called_once()
            call_args = mock_categories.call_args
            assert call_args[0][1] == "minister-123"
            assert call_args[0][2] == "minister"
    
    @pytest.mark.asyncio
    async def test_process_minister_empty_name(self, tmp_path):
        """Test processing minister entry with empty name"""
        year = "2020"
        yaml_base_path = str(tmp_path)
        
        minister_entry = {
            "name": ""
        }
        
        mock_read_service = MagicMock()
        mock_ingestion_service = MagicMock()
        
        with patch('builtins.print') as mock_print:
            await process_minister_entry(
                minister_entry,
                year,
                yaml_base_path,
                mock_read_service,
                mock_ingestion_service
            )
            
            # Should print a warning and return early
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("WARNING" in str(call) and "no name" in str(call) for call in print_calls)


class TestTraversalIntegration:
    """Integration tests for full traversal scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_traversal_path(self, tmp_path):
        """Test complete traversal: minister -> department -> category -> subcategory -> dataset"""
        year = "2020"
        yaml_base_path = str(tmp_path)
        
        # Create a test dataset
        (tmp_path / "datasets" / "Test Dataset").mkdir(parents=True)
        (tmp_path / "datasets" / "Test Dataset" / "data.json").write_text("{}")
        
        # Track traversal order
        traversal_order = []
        
        async def track_categories(cats, parent_id, parent_type, base_path, yr):
            traversal_order.append(f"category:{parent_id}")
            # Process subcategories if any
            for cat in cats:
                if "subcategory" in cat:
                    # Call the patched version from the module
                    await ingest_flat_yaml.process_subcategories_recursive(
                        cat["subcategory"],
                        cat["name"],
                        base_path,
                        yr
                    )
        
        async def track_subcategories(subcats, parent_id, base_path, yr):
            traversal_order.append(f"subcategory:{parent_id}")
            # Process nested subcategories or datasets
            for subcat in subcats:
                if "subcategory" in subcat:
                    # Call the patched version from the module
                    await ingest_flat_yaml.process_subcategories_recursive(
                        subcat["subcategory"],
                        subcat["name"],
                        base_path,
                        yr
                    )
                elif "datasets" in subcat:
                    await ingest_flat_yaml.process_datasets(subcat["datasets"], subcat["name"], base_path)
        
        async def track_datasets(datasets, parent_id, base_path):
            traversal_order.append(f"dataset:{parent_id}")
        
        with patch('ingest_flat_yaml.process_categories', side_effect=track_categories), \
             patch('ingest_flat_yaml.process_subcategories_recursive', side_effect=track_subcategories), \
             patch('ingest_flat_yaml.process_datasets', side_effect=track_datasets):
            
            department_entry = {
                "name": "Test Department",
                "category": [
                    {
                        "name": "category1",
                        "subcategory": [
                            {
                                "name": "subcat1",
                                "datasets": ["datasets/Test Dataset"]
                            }
                        ]
                    }
                ]
            }
            
            await process_department_entry(
                department_entry,
                "dept-123",
                yaml_base_path,
                year
            )
            
            # Verify traversal order
            assert "category:dept-123" in traversal_order
            assert "subcategory:category1" in traversal_order
            assert "dataset:subcat1" in traversal_order
