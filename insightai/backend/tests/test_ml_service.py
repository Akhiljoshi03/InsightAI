"""Unit tests for the scikit-learn wrappers."""
import numpy as np
import pandas as pd

from app.services import ml_service


def test_run_regression_linear():
    rng = np.random.default_rng(0)
    x = rng.uniform(0, 10, 200)
    df = pd.DataFrame({"x": x, "y": 3 * x + 5 + rng.normal(0, 0.5, 200)})
    result = ml_service.run_regression(df, target="y", features=["x"], model_type="linear")
    assert result["r2_score"] > 0.9


def test_run_clustering_kmeans():
    rng = np.random.default_rng(1)
    cluster_a = rng.normal(0, 0.5, (50, 2))
    cluster_b = rng.normal(10, 0.5, (50, 2))
    df = pd.DataFrame(np.vstack([cluster_a, cluster_b]), columns=["f1", "f2"])
    result = ml_service.run_clustering(df, features=["f1", "f2"], algorithm="kmeans", n_clusters=2)
    assert result["n_clusters_found"] == 2


def test_run_anomaly_detection_flags_outlier():
    rng = np.random.default_rng(2)
    normal = rng.normal(0, 1, (100, 1))
    outliers = np.array([[50.0], [55.0]])
    df = pd.DataFrame(np.vstack([normal, outliers]), columns=["value"])
    result = ml_service.run_anomaly_detection(df, columns=["value"], contamination=0.05)
    assert result["anomaly_count"] >= 2
