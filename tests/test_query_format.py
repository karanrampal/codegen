"""Unit tests for the utility functions"""

import pytest

from query_formatter.formatter import QueryFormatter


@pytest.mark.parametrize(
    "query, expected",
    [
        ("```SELECT * FROM users;```", "SELECT * FROM users;"),
        ("```\nSELECT * FROM users;\n```", "\nSELECT * FROM users;\n"),
        ("```sql\nSELECT * FROM users;\n```", "\nSELECT * FROM users;\n"),
        ("```googlesql\nSELECT * FROM users;\n```", "\nSELECT * FROM users;\n"),
        ("```  SELECT * FROM users;  ```", "  SELECT * FROM users;  "),
        ("SELECT * FROM users;", "SELECT * FROM users;"),
        ("```SELECT * FROM users;``` and more text", "SELECT * FROM users;"),
        ("Text before ```SELECT * FROM users;```", "SELECT * FROM users;"),
    ],
)
def test_extract_sql(query: str, expected: str) -> None:
    """Test for extract sql method"""
    assert QueryFormatter.extract_sql(query) == expected


@pytest.mark.parametrize(
    "query",
    [
        "```SELECT * FROM users;",
        "SELECT * FROM users;```",
        "No backticks here",
        "",
    ],
)
def test_extract_sql_return_empty(query: str) -> None:
    """Test extract_sql empty case"""
    assert QueryFormatter.extract_sql(query, return_empty=True) == ""


@pytest.mark.parametrize(
    "query, expected_output",
    [
        ("", ""),
        ("SELECT * FROM table", "SELECT * FROM table"),
        (
            "SELECT customer_brand_id, countr_rk FROM table",
            "SELECT customer_brand_id, countr_rk FROM table",
        ),
        (
            "SELECT customer_brand_id, countr_rk FROM\n `customersegment.table` AS cs",
            "SELECT cs.customer_brand_id, cs.countr_rk FROM\n `customersegment.table` AS cs",
        ),
        (
            "SELECT customer_brand_id, countr_rk FROM\n customersegment- AS cseg",
            "SELECT cseg.customer_brand_id, cseg.countr_rk FROM\n customersegment- AS cseg",
        ),
    ],
)
def test_format_ambiguous(query: str, expected_output: str) -> None:
    """Test format_ambiguous"""
    assert QueryFormatter.format_ambiguous(query) == expected_output


@pytest.mark.parametrize(
    "input_query, expected_output",
    [
        ("", ""),
        ("customersegment-", "`customersegment-`"),
        ("`customersegment`", "`customersegment`"),
        ("onlinebehaviour.something", "`onlinebehaviour.something`"),
        ("customersegment.one.two", "`customersegment.one.two`"),
        ("This is my `customersegment` query", "This is my `customersegment` query"),
        ("`customersegment.` and onlinebehaviours", "`customersegment.` and `onlinebehaviours`"),
        (
            "customersegment.one and onlinebehaviour.two",
            "`customersegment.one` and `onlinebehaviour.two`",
        ),
        ("``customersegment``", "`customersegment`"),
    ],
)
def test_format_backtick(input_query: str, expected_output: str) -> None:
    """Test backtick method"""
    assert QueryFormatter.format_backtick(input_query) == expected_output


@pytest.mark.parametrize(
    "query, expected_output",
    [
        ("customersegment_p_1d26", "customersegment-p-1d26"),
        ("onlinebehaviour_p_e4a2", "onlinebehaviour-p-e4a2"),
        (
            "customersegment_p_1d26_onlinebehaviour_p_e4a2",
            "customersegment-p-1d26_onlinebehaviour-p-e4a2",
        ),
        ("some_other_string", "some_other_string"),
        ("", ""),
        (None, ""),
    ],
)
def test_format_underscore(query: str, expected_output: str) -> None:
    """Test for underscore error"""
    assert QueryFormatter.format_underscore(query) == expected_output


@pytest.mark.parametrize(
    "ans, query",
    [("", ""), ("abc", "abc")],
)
def test_format_query(ans: str, query: str) -> None:
    """Unit test for format query function"""
    assert ans == QueryFormatter.format_query(query)
