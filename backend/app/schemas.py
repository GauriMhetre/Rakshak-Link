import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class CaseBase(BaseModel):
    case_number: Optional[str] = None
    type: str  # MISSING or FOUND
    name: str
    devanagari_name: Optional[str] = None
    aliases: List[str] = []
    age: int
    sex: str
    height_cm: float
    marks: Optional[str] = ""
    clothing: Optional[str] = ""
    language: Optional[str] = ""
    last_seen_found_place: str
    last_seen_found_time: Optional[datetime.datetime] = None
    latitude: float
    longitude: float
    district: str
    phone_numbers: List[str] = []
    photo_url: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: int
    status: str
    photo_embedding: Optional[List[float]] = None
    created_at: datetime.datetime
    created_by_role: Optional[str] = None
    created_by_district: Optional[str] = None

    class Config:
        from_attributes = True

class MatchScoreBreakdown(BaseModel):
    face_score: float
    name_score: float
    attr_score: float
    geotime_score: float
    details: Dict[str, Any] = {}

class MatchResponse(BaseModel):
    id: int
    source_case_id: int
    target_case_id: int
    score: float
    score_breakdown: MatchScoreBreakdown
    status: str
    verified_by_user: Optional[str] = None
    verified_at: Optional[datetime.datetime] = None
    rejection_reason: Optional[str] = None
    source_case: Optional[CaseResponse] = None
    target_case: Optional[CaseResponse] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime.datetime
    user_role: str
    user_district: str
    action: str
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
