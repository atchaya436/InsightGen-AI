"""
InsightGen AI — Reusable logic functions.

These functions contain NO Streamlit calls (no st.anything). This is
deliberate: keeping business logic separate from UI code means we can
test it with plain pytest, without needing a running Streamlit app.
This separation is a standard software engineering practice called
"separation of concerns."
"""

import pandas as pd


def is_id_like_column(df: pd.DataFrame, col: str) -> bool:
    """
    Determine whether a column is likely an identifier (e.g., CustomerID)
    rather than a meaningful measure.

    A column is considered ID-like if:
    - its name contains "id" (case-insensitive), OR
    - more than 95% of its values are unique.

    Args:
        df: The DataFrame containing the column.
        col: The column name to check.

    Returns:
        True if the column looks like an identifier, False otherwise.
    """
    if "id" in col.lower():
        return True
    if len(df) == 0:
        return False
    uniqueness_ratio = df[col].nunique() / len(df)
    return uniqueness_ratio > 0.95


def find_column(df: pd.DataFrame, keywords: list) -> str | None:
    """
    Find the first column whose name contains any of the given keywords
    (case-insensitive substring match).

    Args:
        df: The DataFrame to search.
        keywords: List of keywords to look for in column names.

    Returns:
        The matching column name, or None if no column matches.
    """
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in keywords):
            return col
    return None


def detect_dataset_type(columns: list) -> tuple[str, dict]:
    """
    Detect the likely business dataset type (Retail, HR, Finance,
    Customer, or Generic) based on keyword matches in column names.

    This is a rule-based classifier: it counts how many keywords for
    each type appear in the combined column names, and picks the type
    with the highest score, as long as it scores at least 2.

    Args:
        columns: List of column names from the dataset.

    Returns:
        A tuple of (detected_type, scores_dict) where scores_dict shows
        the keyword match count for every candidate type.
    """
    columns_lower = " ".join(columns).lower()

    type_keywords = {
        "Retail": ["product", "price", "quantity", "sales", "revenue", "category", "order"],
        "HR": ["employee", "salary", "department", "hire", "attrition", "performance", "tenure"],
        "Finance": ["revenue", "expense", "profit", "budget", "cost", "transaction", "invoice"],
        "Customer": ["customer", "spending", "income", "age", "gender", "genre", "membership"],
    }

    scores = {}
    for dataset_type, keywords in type_keywords.items():
        score = sum(1 for keyword in keywords if keyword in columns_lower)
        scores[dataset_type] = score

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    detected_type = best_type if best_score >= 2 else "Generic"

    return detected_type, scores


def calculate_iqr_bounds(series: pd.Series) -> tuple[float, float]:
    """
    Calculate the lower and upper outlier bounds for a numeric series
    using the standard IQR (Interquartile Range) method.

    Args:
        series: A pandas Series of numeric values.

    Returns:
        A tuple of (lower_bound, upper_bound).
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return lower_bound, upper_bound


def standardize_column_name(col: str) -> str:
    """
    Convert a column name to a standardized format: lowercase, with
    spaces replaced by underscores, and special characters removed.

    Example: "Annual Income (k$)" -> "annual_income_k"

    Args:
        col: The original column name.

    Returns:
        The standardized column name.
    """
    new_col = col.strip().lower()
    new_col = new_col.replace(" ", "_")
    new_col = "".join(ch for ch in new_col if ch.isalnum() or ch == "_")
    while "__" in new_col:
        new_col = new_col.replace("__", "_")
    new_col = new_col.strip("_")
    return new_col


def escape_dollar_signs(text: str) -> str:
    """
    Escape '$' characters so Streamlit's markdown renderer doesn't
    misinterpret them as the start of LaTeX math notation.

    Example: "Income ($)" -> "Income (\\$)"

    Args:
        text: The text that may contain '$' characters.

    Returns:
        The text with all '$' escaped.
    """
    return str(text).replace("$", "\\$")