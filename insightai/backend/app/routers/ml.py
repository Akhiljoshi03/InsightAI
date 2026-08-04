"""Regression, clustering, and anomaly detection endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.routers.datasets import _get_owned_dataset
from app.services import data_service, ml_service

router = APIRouter(prefix="/api/ml", tags=["machine-learning"])


def _load_df(db: Session, dataset_id: str, user: models.User):
    dataset = _get_owned_dataset(db, dataset_id, user)
    return data_service.load_dataframe(dataset.file_path, dataset.file_type)


@router.post("/regression")
def regression(payload: schemas.RegressionRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    df = _load_df(db, payload.dataset_id, user)
    try:
        return ml_service.run_regression(df, payload.target_column, payload.feature_columns, payload.model_type)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/clustering")
def clustering(payload: schemas.ClusteringRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    df = _load_df(db, payload.dataset_id, user)
    try:
        return ml_service.run_clustering(df, payload.feature_columns, payload.algorithm, payload.n_clusters)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/anomaly-detection")
def anomaly_detection(payload: schemas.AnomalyRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    df = _load_df(db, payload.dataset_id, user)
    try:
        return ml_service.run_anomaly_detection(df, payload.columns, payload.contamination)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
