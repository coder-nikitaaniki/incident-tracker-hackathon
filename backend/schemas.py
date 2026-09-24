from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    severity: str
    reported_by: str

    @validator('severity')
    def validate_severity(cls, v):
        allowed = ['Low', 'Medium', 'High', 'Critical']
        if v not in allowed:
            raise ValueError(f'severity must be one of {allowed}')
        return v

class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    severity: Optional[str] = None
    assigned_to: Optional[str] = None

    @validator('severity')
    def validate_severity(cls, v):
        if v is None:
            return v
        allowed = ['Low', 'Medium', 'High', 'Critical']
        if v not in allowed:
            raise ValueError(f'severity must be one of {allowed}')
        return v

class IncidentStatusUpdate(BaseModel):
    status: str

class IncidentOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    reported_by: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
