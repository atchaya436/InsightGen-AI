"""
Unit tests for src/utils.py

Run with: pytest
(from the project root, with the virtual environment activated)
"""

import sys
import os
import pandas as pd

# Add the src folder to Python's import path so we can import utils.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils import (
    is_id_like_column,
    find_column,
    detect_dataset_type,
    calculate_iqr_bounds,
    standardize_column_name,
    escape_dollar_signs,
)


# -----------------------------------------------------------------------
# TESTS FOR is_id_like_column
# -----------------------------------------------------------------------

def test_is_id_like_column_detects_id_in_name():
    df = pd.DataFrame({"CustomerID": [1, 2, 3], "Age": [25, 30, 35]})
    assert is_id_like_column(df, "CustomerID") is True


def test_is_id_like_column_detects_high_uniqueness():
    # Every value is unique, and the name doesn't contain "id"
    df = pd.DataFrame({"Code": ["A1", "B2", "C3", "D4"], "Category": ["X", "X", "Y", "Y"]})
    assert is_id_like_column(df, "Code") is True


def test_is_id_like_column_returns_false_for_normal_column():
    df = pd.DataFrame({"Age": [25, 30, 25, 30, 25]})
    assert is_id_like_column(df, "Age") is False


# -----------------------------------------------------------------------
# TESTS FOR find_column
# -----------------------------------------------------------------------

def test_find_column_finds_matching_column():
    df = pd.DataFrame({"Annual Income (k$)": [50, 60], "Age": [25, 30]})
    result = find_column(df, ["income"])
    assert result == "Annual Income (k$)"


def test_find_column_returns_none_when_no_match():
    df = pd.DataFrame({"Age": [25, 30], "Gender": ["M", "F"]})
    result = find_column(df, ["salary", "revenue"])
    assert result is None


def test_find_column_is_case_insensitive():
    df = pd.DataFrame({"SALARY": [50000, 60000]})
    result = find_column(df, ["salary"])
    assert result == "SALARY"


# -----------------------------------------------------------------------
# TESTS FOR detect_dataset_type
# -----------------------------------------------------------------------

def test_detect_dataset_type_customer():
    columns = ["CustomerID", "Gender", "Age", "Annual Income", "Spending Score"]
    detected_type, scores = detect_dataset_type(columns)
    assert detected_type == "Customer"


def test_detect_dataset_type_retail():
    columns = ["OrderID", "Product", "Category", "Price", "Quantity"]
    detected_type, scores = detect_dataset_type(columns)
    assert detected_type == "Retail"


def test_detect_dataset_type_falls_back_to_generic():
    columns = ["StudentID", "Subject", "Score", "Hours_Studied"]
    detected_type, scores = detect_dataset_type(columns)
    assert detected_type == "Generic"


# -----------------------------------------------------------------------
# TESTS FOR calculate_iqr_bounds
# -----------------------------------------------------------------------

def test_calculate_iqr_bounds_normal_data():
    series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    lower, upper = calculate_iqr_bounds(series)
    # For this evenly spread data, bounds should comfortably contain
    # the full range of values (no extreme outliers expected)
    assert lower < series.min()
    assert upper > series.max()


def test_calculate_iqr_bounds_flags_extreme_outlier():
    series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 1000])
    lower, upper = calculate_iqr_bounds(series)
    # 1000 should fall OUTSIDE the calculated upper bound
    assert 1000 > upper


# -----------------------------------------------------------------------
# TESTS FOR standardize_column_name
# -----------------------------------------------------------------------

def test_standardize_column_name_basic():
    assert standardize_column_name("Annual Income (k$)") == "annual_income_k"


def test_standardize_column_name_removes_extra_spaces():
    assert standardize_column_name("  Customer   Name  ") == "customer_name"


def test_standardize_column_name_already_clean():
    assert standardize_column_name("age") == "age"


# -----------------------------------------------------------------------
# TESTS FOR escape_dollar_signs
# -----------------------------------------------------------------------

def test_escape_dollar_signs_escapes_dollar():
    assert escape_dollar_signs("Income ($)") == "Income (\\$)"


def test_escape_dollar_signs_no_dollar_unchanged():
    assert escape_dollar_signs("Age") == "Age"