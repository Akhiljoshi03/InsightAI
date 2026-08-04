"""Unit tests for the pandas profiling/cleaning service (no DB/API needed)."""
import pandas as pd
import pytest

from app.services import data_service


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 4],
        "revenue": [100.0, 200.0, None, 400.0, 400.0],
        "region": ["NA", "EU", "NA", "NA", "NA"],
    })


def test_profile_dataframe_counts(sample_df):
    profile = data_service.profile_dataframe(sample_df)
    assert profile["row_count"] == 5
    assert profile["column_count"] == 3
    assert profile["duplicate_rows"] == 1


def test_profile_dataframe_null_pct(sample_df):
    profile = data_service.profile_dataframe(sample_df)
    revenue_col = next(c for c in profile["columns"] if c["name"] == "revenue")
    assert revenue_col["null_count"] == 1


def test_remove_duplicates(sample_df):
    cleaned = data_service.apply_cleaning(sample_df, ["remove_duplicates"])
    assert len(cleaned) == 4


def test_fill_missing_mean(sample_df):
    cleaned = data_service.apply_cleaning(sample_df, ["fill_missing_mean"], columns=["revenue"])
    assert cleaned["revenue"].isna().sum() == 0


def test_unknown_op_is_skipped(sample_df):
    cleaned = data_service.apply_cleaning(sample_df, ["not_a_real_op"])
    pd.testing.assert_frame_equal(cleaned, sample_df)
