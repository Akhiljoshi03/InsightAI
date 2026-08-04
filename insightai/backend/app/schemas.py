"""Pydantic request/response schemas."""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None
    avatar_url: Optional[str] = None
    plan: str
    theme: str
    is_admin: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Projects / Datasets ----------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: Optional[str]
    created_at: datetime


class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    file_type: str
    row_count: int
    column_count: int
    status: str
    profile: Optional[dict] = None
    created_at: datetime


class CleaningRequest(BaseModel):
    operations: list[str]  # e.g. ["remove_duplicates","fill_missing_mean","strip_whitespace"]
    columns: Optional[list[str]] = None


# ---------- Chat / NL2SQL ----------
class ChatRequest(BaseModel):
    dataset_id: str
    message: str


class ChatResponse(BaseModel):
    text: str
    confidence: float
    stats: Optional[dict[str, Any]] = None
    chart_spec: Optional[dict[str, Any]] = None
    sql: Optional[str] = None


class NL2SQLRequest(BaseModel):
    dataset_id: str
    question: str


# ---------- ML ----------
class RegressionRequest(BaseModel):
    dataset_id: str
    target_column: str
    feature_columns: list[str]
    model_type: str = "linear"  # linear | logistic | decision_tree | random_forest | gradient_boosting


class ClusteringRequest(BaseModel):
    dataset_id: str
    feature_columns: list[str]
    algorithm: str = "kmeans"  # kmeans | dbscan
    n_clusters: int = 3


class ForecastRequest(BaseModel):
    dataset_id: str
    date_column: str
    value_column: str
    periods: int = 3


class AnomalyRequest(BaseModel):
    dataset_id: str
    columns: list[str]
    contamination: float = 0.05


# ---------- Reports ----------
class ReportGenerateRequest(BaseModel):
    dataset_id: str
    title: str
    sections: list[str] = ["summary", "overview", "insights", "risks", "recommendations", "predictions"]
