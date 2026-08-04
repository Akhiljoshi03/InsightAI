"""Admin panel endpoints: manage users, datasets, reports, storage, AI usage, logs.
All routes require an admin user (see app.deps.require_admin)."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.get("/stats")
def system_stats(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    return {
        "total_users": db.query(func.count(models.User.id)).scalar(),
        "total_projects": db.query(func.count(models.Project.id)).scalar(),
        "total_datasets": db.query(func.count(models.Dataset.id)).scalar(),
        "total_reports": db.query(func.count(models.Report.id)).scalar(),
        "total_rows_processed": db.query(func.coalesce(func.sum(models.Dataset.row_count), 0)).scalar(),
    }


@router.get("/logs")
def audit_logs(limit: int = 100, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    return (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )


@router.delete("/users/{user_id}", status_code=204)
def deactivate_user(user_id: str, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
