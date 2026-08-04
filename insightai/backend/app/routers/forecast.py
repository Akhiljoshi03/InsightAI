"""Time-series forecasting endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.routers.datasets import _get_owned_dataset
from app.services import data_service, ml_service

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


@router.post("")
def forecast(payload: schemas.ForecastRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, payload.dataset_id, user)
    df = data_service.load_dataframe(dataset.file_path, dataset.file_type)
    try:
        return ml_service.run_forecast(df, payload.date_column, payload.value_column, payload.periods)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
