"""Generate and export executive reports (PDF / XLSX / CSV)."""
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user
from app.routers.datasets import _get_owned_dataset
from app.services import data_service, report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])
settings = get_settings()


@router.post("/generate")
def generate_report(payload: schemas.ReportGenerateRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, payload.dataset_id, user)
    if not dataset.profile:
        raise HTTPException(status_code=400, detail="Dataset has not finished analyzing yet")

    try:
        content = report_service.generate_report_content(dataset.profile, payload.title)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc

    report = models.Report(
        project_id=dataset.project_id, dataset_id=dataset.id, title=payload.title, content=content,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"id": report.id, "title": report.title, "content": content}


@router.get("/{report_id}/export/{fmt}")
def export_report(report_id: str, fmt: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    report = (
        db.query(models.Report)
        .join(models.Project)
        .filter(models.Report.id == report_id, models.Project.owner_id == user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    os.makedirs(settings.upload_dir, exist_ok=True)
    out_path = os.path.join(settings.upload_dir, f"report_{report.id}.{fmt}")

    if fmt == "pdf":
        report_service.export_pdf(report.title, report.content, out_path)
        media = "application/pdf"
    elif fmt == "xlsx":
        dataset = db.query(models.Dataset).filter(models.Dataset.id == report.dataset_id).first()
        report_service.export_xlsx(report.title, report.content, dataset.profile if dataset else {}, out_path)
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif fmt == "csv":
        dataset = db.query(models.Dataset).filter(models.Dataset.id == report.dataset_id).first()
        df = data_service.load_dataframe(dataset.file_path, dataset.file_type)
        df.to_csv(out_path, index=False)
        media = "text/csv"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use pdf, xlsx, or csv.")

    report.file_path = out_path
    db.commit()
    return FileResponse(out_path, media_type=media, filename=os.path.basename(out_path))
