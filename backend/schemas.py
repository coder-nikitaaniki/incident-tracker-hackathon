from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class IncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    severity: str
    assigned_to: Optional[str] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or just spaces')
        return v.strip()

    @field_validator('severity')
    @classmethod
    def severity_must_be_valid(cls, v):
        allowed = ["Critical", "High", "Medium", "Low"]
        if v not in allowed:
            raise ValueError(f"Severity must be one of {allowed}")
        return v

class IncidentCreate(IncidentBase):
    reported_by: str = Field(..., min_length=1)

class IncidentUpdate(IncidentBase):
    pass

class IncidentStatusUpdate(BaseModel):
    status: str
    actor: str = Field(default="System User")
