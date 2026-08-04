"""Pandas-backed dataset loading, profiling, and cleaning operations.

All functions operate on an in-memory DataFrame loaded from the stored file.
Profiling results are cached on Dataset.profile (JSON) so repeated dashboard
loads don't re-scan large files.
"""
from __future__ import annotations

import json
import os
from typing import Any

import numpy as np
import pandas as pd


def load_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
    if file_type == "csv":
        return pd.read_csv(file_path)
    if file_type in ("xlsx", "xls"):
        return pd.read_excel(file_path)
    if file_type == "json":
        return pd.read_json(file_path)
    raise ValueError(f"Unsupported file type: {file_type}")


def _json_safe(value: Any) -> Any:
    """Recursively convert numpy/pandas scalars to native JSON-serializable types."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def profile_dataframe(df: pd.DataFrame) -> dict:
    """Full automatic profile: dtypes, missing values, duplicates, outliers,
    unique counts, correlations, and per-column descriptive statistics."""
    n_rows = len(df)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    columns_info = []
    for col in df.columns:
        series = df[col]
        col_info = {
            "name": col,
            "dtype": str(series.dtype),
            "null_count": int(series.isna().sum()),
            "null_pct": round(float(series.isna().mean()) * 100, 2),
            "unique_count": int(series.nunique()),
        }
        if col in numeric_cols:
            desc = series.describe()
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outliers = series[(series < lower) | (series > upper)]
            col_info.update({
                "mean": desc.get("mean"),
                "median": series.median(),
                "std": desc.get("std"),
                "min": desc.get("min"),
                "max": desc.get("max"),
                "p25": q1, "p75": q3,
                "skewness": series.skew(),
                "kurtosis": series.kurt(),
                "outlier_count": int(len(outliers)),
            })
        else:
            top = series.mode()
            col_info["mode"] = top.iloc[0] if not top.empty else None
        columns_info.append(_json_safe(col_info))

    correlations = None
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True).round(3)
        correlations = _json_safe(corr.to_dict())

    profile = {
        "row_count": n_rows,
        "column_count": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_pct": round(float(df.duplicated().mean()) * 100, 2) if n_rows else 0,
        "columns": columns_info,
        "correlations": correlations,
        "preview": _json_safe(df.head(20).replace({np.nan: None}).to_dict(orient="records")),
    }
    return profile


CLEANING_OPS = {}


def _op(name):
    def wrapper(fn):
        CLEANING_OPS[name] = fn
        return fn
    return wrapper


@_op("remove_duplicates")
def _remove_duplicates(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    return df.drop_duplicates()


@_op("drop_empty_rows")
def _drop_empty_rows(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    return df.dropna(how="all")


@_op("fill_missing_mean")
def _fill_missing_mean(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    df = df.copy()
    for c in cols:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].fillna(df[c].mean())
    return df


@_op("fill_missing_median")
def _fill_missing_median(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    df = df.copy()
    for c in cols:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].fillna(df[c].median())
    return df


@_op("fill_missing_mode")
def _fill_missing_mode(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    cols = columns or df.columns.tolist()
    df = df.copy()
    for c in cols:
        if c in df.columns and not df[c].mode().empty:
            df[c] = df[c].fillna(df[c].mode().iloc[0])
    return df


@_op("strip_whitespace")
def _strip_whitespace(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    df = df.copy()
    cols = columns or df.select_dtypes(include=["object"]).columns.tolist()
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df


@_op("normalize_minmax")
def _normalize_minmax(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    df = df.copy()
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    for c in cols:
        if c in df.columns:
            rng = df[c].max() - df[c].min()
            df[c] = (df[c] - df[c].min()) / rng if rng else 0
    return df


@_op("standardize_zscore")
def _standardize_zscore(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    df = df.copy()
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    for c in cols:
        if c in df.columns:
            std = df[c].std()
            df[c] = (df[c] - df[c].mean()) / std if std else 0
    return df


@_op("encode_categories")
def _encode_categories(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    df = df.copy()
    cols = columns or df.select_dtypes(include=["object"]).columns.tolist()
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype("category").cat.codes
    return df


@_op("parse_dates")
def _parse_dates(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    df = df.copy()
    cols = columns or []
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def apply_cleaning(df: pd.DataFrame, operations: list[str], columns: list[str] | None = None) -> pd.DataFrame:
    """Apply a sequence of named cleaning operations, in order. Unknown ops are skipped."""
    for op_name in operations:
        fn = CLEANING_OPS.get(op_name)
        if fn:
            df = fn(df, columns)
    return df


def save_dataframe(df: pd.DataFrame, file_path: str, file_type: str) -> None:
    if file_type == "csv":
        df.to_csv(file_path, index=False)
    elif file_type in ("xlsx", "xls"):
        df.to_excel(file_path, index=False)
    elif file_type == "json":
        df.to_json(file_path, orient="records")
