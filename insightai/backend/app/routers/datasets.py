"""Dataset upload, profiling, preview, cleaning, and deletion endpoints."""
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user
from app.services import data_service

router = APIRouter(prefix="/api/datasets", tags=["datasets"])
settings = get_settings()

ALLOWED_EXT = {"csv", "xlsx", "xls", "json"}


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _project_owned(db: Session, project_id: str, user: models.User) -> models.Project:
    project = db.query(models.Project).filter(
        models.Project.id == project_id, models.Project.owner_id == user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/upload", response_model=schemas.DatasetOut)
async def upload_dataset(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    _project_owned(db, project_id, user)
    ext = _ext(file.filename)
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}")

    os.makedirs(settings.upload_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4()}.{ext}"
    dest_path = os.path.join(settings.upload_dir, stored_name)
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    size_mb = os.path.getsize(dest_path) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        os.remove(dest_path)
        raise HTTPException(status_code=413, detail="File exceeds max upload size")

    dataset = models.Dataset(
        project_id=project_id,
        filename=file.filename,
        file_path=dest_path,
        file_type="xlsx" if ext == "xls" else ext,
        status=models.DatasetStatus.analyzing,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Synchronous profiling for simplicity; move to a background worker/queue for large files.
    try:
        df = data_service.load_dataframe(dataset.file_path, dataset.file_type)
        profile = data_service.profile_dataframe(df)
        dataset.row_count = profile["row_count"]
        dataset.column_count = profile["column_count"]
        dataset.profile = profile
        dataset.status = models.DatasetStatus.ready
    except Exception as exc:  # noqa: BLE001
        dataset.status = models.DatasetStatus.error
        dataset.profile = {"error": str(exc)}
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("/project/{project_id}", response_model=list[schemas.DatasetOut])
def list_datasets(project_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    _project_owned(db, project_id, user)
    return db.query(models.Dataset).filter(models.Dataset.project_id == project_id).all()


@router.get("/{dataset_id}", response_model=schemas.DatasetOut)
def get_dataset(dataset_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, dataset_id, user)
    return dataset


def _get_owned_dataset(db: Session, dataset_id: str, user: models.User) -> models.Dataset:
    dataset = (
        db.query(models.Dataset)
        .join(models.Project)
        .filter(models.Dataset.id == dataset_id, models.Project.owner_id == user.id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.post("/{dataset_id}/clean", response_model=schemas.DatasetOut)
def clean_dataset(
    dataset_id: str,
    payload: schemas.CleaningRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Apply one-click cleaning operations and re-profile. Original file is
    backed up to <path>.bak on first clean so 'Undo' can restore it."""
    dataset = _get_owned_dataset(db, dataset_id, user)
    df = data_service.load_dataframe(dataset.file_path, dataset.file_type)

    backup_path = dataset.file_path + ".bak"
    if not os.path.exists(backup_path):
        shutil.copyfile(dataset.file_path, backup_path)

    cleaned = data_service.apply_cleaning(df, payload.operations, payload.columns)
    data_service.save_dataframe(cleaned, dataset.file_path, dataset.file_type)

    profile = data_service.profile_dataframe(cleaned)
    dataset.row_count = profile["row_count"]
    dataset.column_count = profile["column_count"]
    dataset.profile = profile
    db.commit()
    db.refresh(dataset)
    return dataset


@router.post("/{dataset_id}/undo-clean", response_model=schemas.DatasetOut)
def undo_clean(dataset_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, dataset_id, user)
    backup_path = dataset.file_path + ".bak"
    if not os.path.exists(backup_path):
        raise HTTPException(status_code=400, detail="No cleaning operation to undo")
    shutil.copyfile(backup_path, dataset.file_path)
    df = data_service.load_dataframe(dataset.file_path, dataset.file_type)
    profile = data_service.profile_dataframe(df)
    dataset.profile = profile
    dataset.row_count = profile["row_count"]
    dataset.column_count = profile["column_count"]
    db.commit()
    db.refresh(dataset)
    return dataset


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, dataset_id, user)
    for path in (dataset.file_path, dataset.file_path + ".bak"):
        if os.path.exists(path):
            os.remove(path)
    db.delete(dataset)
    db.commit()
