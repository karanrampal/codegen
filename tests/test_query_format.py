"""Unit tests for the utility functions"""

import pytest

from query_formatter.formatter import QueryFormatter


@pytest.mark.parametrize(
    "ans, query",
    [
        ("", ""),
    ],
)
def test_format_query(ans: str, query: str) -> None:
    """Unit test for fromat query function"""
    assert ans == QueryFormatter.format_query(query)
