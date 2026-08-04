"""AI chat over a dataset, plus natural-language-to-SQL querying (executed
read-only against an in-memory SQLite view of the DataFrame via pandasql-style
duckdb query, kept simple here with pandas.query as a safer default)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.routers.datasets import _get_owned_dataset
from app.services import ai_service, data_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, payload.dataset_id, user)
    if not dataset.profile:
        raise HTTPException(status_code=400, detail="Dataset has not finished analyzing yet")

    history = [
        {"role": m.role, "content": m.content}
        for m in db.query(models.ChatMessage).filter(models.ChatMessage.dataset_id == dataset.id).order_by(models.ChatMessage.created_at).all()
    ]

    db.add(models.ChatMessage(dataset_id=dataset.id, role="user", content=payload.message))
    db.commit()

    try:
        result = ai_service.chat_about_dataset(dataset.profile, payload.message, history)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc

    db.add(models.ChatMessage(
        dataset_id=dataset.id, role="assistant", content=result.get("text", ""),
        meta={"confidence": result.get("confidence"), "stats": result.get("stats")},
    ))
    db.commit()

    return schemas.ChatResponse(
        text=result.get("text", ""),
        confidence=float(result.get("confidence", 50)),
        stats=result.get("stats"),
        chart_spec={"type": result.get("chart_suggestion", "none")},
    )


@router.post("/nl2sql")
def nl2sql(payload: schemas.NL2SQLRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    dataset = _get_owned_dataset(db, payload.dataset_id, user)
    df = data_service.load_dataframe(dataset.file_path, dataset.file_type)

    try:
        sql = ai_service.nl_to_sql(dataset.profile["columns"], payload.question)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Execute against an ephemeral, in-memory SQLite table — isolated per request,
    # never touches the application's own Postgres database.
    import sqlite3
    conn = sqlite3.connect(":memory:")
    df.to_sql("dataset", conn, index=False, if_exists="replace")
    try:
        cursor = conn.execute(sql)
        columns = [d[0] for d in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Query execution failed: {exc}") from exc
    finally:
        conn.close()

    return {"sql": sql, "rows": rows[:500]}
