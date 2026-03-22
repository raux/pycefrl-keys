"""
Tests for the Streamlit web interface helper functions in :mod:`app`.

These tests validate the non-UI helper functions (categorisation, DataFrame
conversion, GitHub URL validation) without launching a Streamlit server.
"""

import os
import tempfile

import pandas as pd
import pytest

# Import only the pure helper functions — no Streamlit UI side-effects are
# triggered because these functions do not call st.* at module level when
# imported individually.
from app import categorize_class, results_to_dataframe


# ---------------------------------------------------------------------------
# categorize_class
# ---------------------------------------------------------------------------

class TestCategorizeClass:
    """Verify the high-level category assigned to each pattern class name."""

    @pytest.mark.parametrize(
        "class_name, expected",
        [
            ("Print", "I/O"),
            ("File open() call", "I/O"),
            ("File I/O method call", "I/O"),
            ("Simple List", "Data Structures"),
            ("Simple Tuple", "Data Structures"),
            ("Simple Dictionary", "Data Structures"),
            ("Nested List", "Data Structures"),
            ("Nested Dictionary", "Data Structures"),
            ("Simple If Statement", "Control Flow"),
            ("Simple For Loop", "Control Flow"),
            ("While Loop", "Control Flow"),
            ("Break", "Control Flow"),
            ("Continue", "Control Flow"),
            ("Pass", "Control Flow"),
            ("Try Block", "Control Flow"),
            ("Except Clause", "Control Flow"),
            ("Lambda Expression", "OOP & Functions"),
            ("Simple Function Definition", "OOP & Functions"),
            ("Function with Arguments", "OOP & Functions"),
            ("Simple Class Definition", "OOP & Functions"),
            ("__init__ Method", "OOP & Functions"),
            ("Property Decorator", "OOP & Functions"),
            ("Generator Function (yield)", "OOP & Functions"),
            ("Import", "Modules"),
            ("From Import", "Modules"),
            ("From Relative Import", "Modules"),
            ("Standard Library Module Import", "Modules"),
            ("Augmented Assignment", "Operations"),
            ("Simple Assignment", "Operations"),
            ("Simple Return", "OOP & Functions"),
            ("range() call", "Other"),
        ],
    )
    def test_known_categories(self, class_name, expected):
        assert categorize_class(class_name) == expected

    def test_unknown_returns_other(self):
        assert categorize_class("SomeCompletelyUnknownThing") == "Other"


# ---------------------------------------------------------------------------
# results_to_dataframe
# ---------------------------------------------------------------------------

class TestResultsToDataFrame:
    """Verify conversion from analyser result dicts to a pandas DataFrame."""

    SAMPLE_RESULTS = [
        {
            "repo": "my_repo",
            "file": "main.py",
            "class": "Print",
            "start_line": 1,
            "end_line": 1,
            "displacement": 0,
            "level": "A1",
        },
        {
            "repo": "my_repo",
            "file": "main.py",
            "class": "Simple Assignment",
            "start_line": 2,
            "end_line": 2,
            "displacement": 0,
            "level": "A1",
        },
        {
            "repo": "my_repo",
            "file": "utils.py",
            "class": "Lambda Expression",
            "start_line": 5,
            "end_line": 5,
            "displacement": 4,
            "level": "B1",
        },
    ]

    def test_column_names(self):
        df = results_to_dataframe(self.SAMPLE_RESULTS)
        for col in ("Repo", "File", "Class", "Start Line", "End Line", "Level", "Category"):
            assert col in df.columns, f"Missing column: {col}"

    def test_row_count(self):
        df = results_to_dataframe(self.SAMPLE_RESULTS)
        assert len(df) == len(self.SAMPLE_RESULTS)

    def test_category_column_populated(self):
        df = results_to_dataframe(self.SAMPLE_RESULTS)
        assert df["Category"].notna().all()

    def test_empty_results(self):
        df = results_to_dataframe([])
        assert df.empty

    def test_level_values_preserved(self):
        df = results_to_dataframe(self.SAMPLE_RESULTS)
        assert set(df["Level"]) == {"A1", "B1"}
