"""Unit tests for the SchemaManager class"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config_manager.manager import Params
from schema_manager.schema import SchemaManager


@pytest.fixture(name="my_schema_manager")
def schema_manager() -> SchemaManager:
    """Pytest fixture to create schema manager"""
    params = Params(
        {
            "project_id": "test-project",
            "filter_columns": ["col1", "col2"],
            "num_rows": 10,
            "tables": ["table1", "table2"],
            "metadata": "test/path",
        }
    )
    return SchemaManager(params)


def test_init(my_schema_manager: SchemaManager) -> None:
    """Test initialization"""
    assert my_schema_manager.client is not None
    assert my_schema_manager.table_names == ["table1", "table2"]
    assert my_schema_manager.meta_loc == "test/path"
    assert my_schema_manager.filter_cols == ["col1", "col2"]
    assert my_schema_manager.num_rows == 10
    assert my_schema_manager.schemas == ""


@patch("os.path.join")
@patch("builtins.open", new_callable=MagicMock)
def test_read_schema_success(
    mock_open: MagicMock, mock_join: MagicMock, my_schema_manager: SchemaManager
) -> None:
    """Test read_schema function"""
    mock_join.return_value = "test/path/schemas.txt"
    mock_open.return_value.__enter__.return_value.read.return_value = "Test Schema"
    my_schema_manager.read_schema()
    assert my_schema_manager.schemas == "Test Schema"


@patch("os.path.join")
def test_read_schema_file_not_found(mock_join: MagicMock, my_schema_manager: SchemaManager) -> None:
    """Test read_schema exception"""
    mock_join.return_value = "nonexistent/path.txt"
    with pytest.raises(FileNotFoundError):
        my_schema_manager.read_schema()


def test_write_schemas(my_schema_manager: SchemaManager, tmp_path: Path) -> None:
    """Test write_schema method"""
    my_schema_manager.schemas = "test_schema"

    my_schema_manager.meta_loc = str(tmp_path)
    my_schema_manager.write_schemas()

    schema_file = os.path.join(my_schema_manager.meta_loc, "schemas.txt")
    assert os.path.exists(schema_file)

    with open(schema_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert content == "test_schema"


@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join", return_value="test_metadata/dataset_info.md")
def test_get_dataset_info(
    mock_join: MagicMock, mock_open: MagicMock, my_schema_manager: SchemaManager
) -> None:
    """Test get_dataset_info function"""
    mock_open.return_value.__enter__.return_value.read.return_value = "Test dataset information"

    result = my_schema_manager.get_dataset_info()

    assert result == "Test dataset information"
    mock_join.assert_called_once_with("test/path", "dataset_info.md")
    mock_open.assert_called_once_with("test_metadata/dataset_info.md", "r", encoding="UTF-8")
