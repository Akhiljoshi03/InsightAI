"""Aggregation endpoint that shapes a dataset column into chart-ready series
(bar/line/pie/scatter/heatmap) with grouping, sorting, filtering, aggregation."""
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.deps import get_current_user
from app.routers.datasets import _get_owned_dataset
from app.services import data_service

router = APIRouter(prefix="/api/charts", tags=["charts"])

AggFunc = Literal["sum", "mean", "count", "min", "max", "median"]


@router.get("/{dataset_id}/aggregate")
def aggregate(
    dataset_id: str,
    x: str = Query(..., description="Column to group by"),
    y: Optional[str] = Query(None, description="Numeric column to aggregate; omit for count"),
    agg: AggFunc = Query("sum"),
    sort_desc: bool = Query(True),
    limit: int = Query(50, le=1000),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    dataset = _get_owned_dataset(db, dataset_id, user)
    df = data_service.load_dataframe(dataset.file_path, dataset.file_type)

    if x not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{x}' not found")

    if y and y not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{y}' not found")

    if y:
        grouped = getattr(df.groupby(x)[y], agg)().reset_index()
        grouped = grouped.rename(columns={y: "value"})
    else:
        grouped = df.groupby(x).size().reset_index(name="value")

    grouped = grouped.sort_values("value", ascending=not sort_desc).head(limit)
    grouped = grouped.rename(columns={x: "label"})
    return {"x": x, "y": y, "agg": agg, "data": grouped.to_dict(orient="records")}


@router.get("/{dataset_id}/correlation-matrix")
def correlation_matrix(dataset_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, dataset_id, user)
    if not dataset.profile or not dataset.profile.get("correlations"):
        raise HTTPException(status_code=400, detail="No numeric correlations available for this dataset")
    return dataset.profile["correlations"]
