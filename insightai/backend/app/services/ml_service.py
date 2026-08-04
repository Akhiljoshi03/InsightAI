"""Machine learning routines used by the ML and forecasting endpoints.

Kept dependency-light (scikit-learn + numpy/pandas only) so it runs without
GPU or heavyweight forecasting libraries. Swap in statsmodels/prophet for
more advanced seasonality handling if needed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor, IsolationForest
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    r2_score, mean_absolute_error, accuracy_score, roc_auc_score, roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


def _prep_xy(df: pd.DataFrame, target: str, features: list[str]):
    data = df[features + [target]].dropna()
    X = pd.get_dummies(data[features], drop_first=True)
    y = data[target]
    return X, y


def run_regression(df: pd.DataFrame, target: str, features: list[str], model_type: str) -> dict:
    X, y = _prep_xy(df, target, features)
    is_classification = model_type == "logistic" or y.dtype == object or y.nunique() <= 10 and y.dtype != float

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    if model_type == "linear":
        model = LinearRegression()
    elif model_type == "logistic":
        model = LogisticRegression(max_iter=1000)
    elif model_type == "decision_tree":
        model = DecisionTreeClassifier(random_state=42) if is_classification else DecisionTreeRegressor(random_state=42)
    elif model_type == "random_forest":
        model = RandomForestClassifier(random_state=42) if is_classification else RandomForestRegressor(random_state=42)
    elif model_type == "gradient_boosting":
        model = GradientBoostingRegressor(random_state=42)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    result: dict = {"model_type": model_type, "n_train": len(X_train), "n_test": len(X_test)}

    if model_type == "logistic" or (is_classification and hasattr(model, "predict_proba")):
        result["accuracy"] = round(float(accuracy_score(y_test, preds)), 4)
        try:
            proba = model.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, proba)
            result["roc_auc"] = round(float(roc_auc_score(y_test, proba)), 4)
            result["roc_curve"] = {"fpr": fpr.round(4).tolist(), "tpr": tpr.round(4).tolist()}
        except Exception:  # noqa: BLE001 - not all targets are binary
            pass
    else:
        result["r2_score"] = round(float(r2_score(y_test, preds)), 4)
        result["mae"] = round(float(mean_absolute_error(y_test, preds)), 4)

    if hasattr(model, "feature_importances_"):
        importances = dict(zip(X.columns, model.feature_importances_.round(4).tolist()))
        result["feature_importance"] = dict(sorted(importances.items(), key=lambda kv: -kv[1]))
    elif hasattr(model, "coef_"):
        coefs = np.ravel(model.coef_)
        result["feature_importance"] = dict(zip(X.columns, np.round(coefs, 4).tolist()))

    return result


def run_clustering(df: pd.DataFrame, features: list[str], algorithm: str, n_clusters: int) -> dict:
    data = df[features].dropna()
    X = StandardScaler().fit_transform(pd.get_dummies(data, drop_first=True))

    if algorithm == "kmeans":
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(X)
    elif algorithm == "dbscan":
        model = DBSCAN(eps=0.7, min_samples=5)
        labels = model.fit_predict(X)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    data = data.copy()
    data["cluster"] = labels
    sizes = data["cluster"].value_counts().to_dict()
    return {
        "algorithm": algorithm,
        "n_clusters_found": int(len(set(labels)) - (1 if -1 in labels else 0)),
        "cluster_sizes": {str(k): int(v) for k, v in sizes.items()},
        "assignments": data.reset_index(drop=True).to_dict(orient="records")[:500],
    }


def run_anomaly_detection(df: pd.DataFrame, columns: list[str], contamination: float) -> dict:
    data = df[columns].dropna()
    X = StandardScaler().fit_transform(pd.get_dummies(data, drop_first=True))

    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(X)  # -1 = anomaly, 1 = normal
    scores = model.decision_function(X)

    out = data.copy()
    out["is_anomaly"] = preds == -1
    out["anomaly_score"] = scores.round(4)
    anomalies = out[out["is_anomaly"]].sort_values("anomaly_score").head(100)

    return {
        "total_rows": len(data),
        "anomaly_count": int(out["is_anomaly"].sum()),
        "anomaly_pct": round(float(out["is_anomaly"].mean()) * 100, 2),
        "anomalies": anomalies.reset_index(drop=True).to_dict(orient="records"),
    }


def run_forecast(df: pd.DataFrame, date_col: str, value_col: str, periods: int) -> dict:
    """Simple, dependency-light forecast: linear trend + monthly seasonality
    index applied on top, with a bootstrap-based confidence interval."""
    data = df[[date_col, value_col]].dropna().copy()
    data[date_col] = pd.to_datetime(data[date_col])
    data = data.sort_values(date_col)
    data = data.set_index(date_col).resample("MS")[value_col].mean().dropna()

    if len(data) < 4:
        raise ValueError("Need at least 4 periods of history to forecast")

    t = np.arange(len(data))
    y = data.values
    coeffs = np.polyfit(t, y, 1)
    trend = np.poly1d(coeffs)

    residuals = y - trend(t)
    resid_std = float(np.std(residuals)) if len(residuals) > 1 else 0.0

    seasonal_index = (
        pd.Series(y, index=data.index).groupby(data.index.month).mean()
        / pd.Series(y, index=data.index).mean()
    ).to_dict()

    future_t = np.arange(len(data), len(data) + periods)
    future_dates = pd.date_range(data.index[-1] + pd.offsets.MonthBegin(), periods=periods, freq="MS")

    forecasts = []
    for i, (ft, fd) in enumerate(zip(future_t, future_dates)):
        base = trend(ft)
        seasonal_mult = seasonal_index.get(fd.month, 1.0)
        point = base * seasonal_mult
        ci = 1.645 * resid_std * (1 + i * 0.15)  # widen interval further out
        forecasts.append({
            "date": fd.strftime("%Y-%m-%d"),
            "forecast": round(float(point), 2),
            "lower": round(float(point - ci), 2),
            "upper": round(float(point + ci), 2),
        })

    return {
        "history": [{"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)} for d, v in data.items()],
        "forecast": forecasts,
        "trend_slope": round(float(coeffs[0]), 4),
    }
