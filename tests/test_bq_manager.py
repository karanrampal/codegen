"""Add unit tests for bigquery manager"""

from unittest.mock import patch

import pandas as pd
import pytest
from typing_extensions import Self  # import from typing if python>=3.11

from bq_manager.query import BQManager
from config_manager.manager import Params


class MockQueryResult:
    """Mock the result method of of clients query"""

    def __init__(self, query: str) -> None:
        self.query = query

    def result(self) -> Self:
        """Mock of result method"""
        return self

    def to_dataframe(self) -> pd.DataFrame:
        """Mock of to_dataframe method"""
        if self.query == "SELECT 1":
            return pd.DataFrame({"a": [1]}).astype(str)
        if self.query == "SELECT 2":
            return pd.DataFrame({"b": [2, 3]})
        return pd.DataFrame()


@pytest.fixture(name="my_bq_manager")
def bq_manager() -> BQManager:
    """Pytest fixture for creating BQManager class object"""
    params = Params({"project_id": "test-project", "filter_columns": ["col1", "col2"]})
    return BQManager(params)


def test_init(my_bq_manager: BQManager) -> None:
    """Test initialization"""
    assert my_bq_manager.bq_client.project == "test-project"
    assert my_bq_manager.filter_cols == ["col1", "col2"]


def test_execute_sql_empty_query(my_bq_manager: BQManager) -> None:
    """Test null query"""
    result = my_bq_manager.execute_sql("")
    assert result.empty


def test_execute_sql_multiple_rows(my_bq_manager: BQManager) -> None:
    """Unit test for executing sql with multple rows"""
    with patch("google.cloud.bigquery.Client.query", return_value=MockQueryResult("SELECT 2")):
        result = my_bq_manager.execute_sql("SELECT 2")
        assert result.equals(pd.DataFrame({"b": [2, 3]}))


def test_execute_sql_single_value(my_bq_manager: BQManager) -> None:
    """Unit test to check single value dataframe return"""
    with patch("google.cloud.bigquery.Client.query", return_value=MockQueryResult("SELECT 1")):
        result = my_bq_manager.execute_sql("SELECT 1")
        assert result.equals(pd.DataFrame({"a": [1]}).astype(str))
        assert result["a"].dtype == "object"


def test_execute_sql_error(my_bq_manager: BQManager) -> None:
    """Unit test to check error condition"""
    with patch("google.cloud.bigquery.Client.query", side_effect=Exception("Test Error")):
        result = my_bq_manager.execute_sql("INVALID QUERY")
        assert str(result.values[0, 0]) == "Test Error"
