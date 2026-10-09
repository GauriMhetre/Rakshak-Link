from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import AuditLog

class UserContext:
    def __init__(self, role: str, district: str):
        self.role = role
        self.district = district

    def can_access_district(self, target_district: str) -> bool:
        if self.role in ["Investigating Officer", "CWC Officer", "Admin"]:
            return True
        return self.district == target_district

def get_user_context(
    x_user_role: Optional[str] = Header("Station Officer"),
    x_user_district: Optional[str] = Header("Pune")
) -> UserContext:
    role = x_user_role or "Station Officer"
    district = x_user_district or "Pune"
    return UserContext(role=role, district=district)

def log_audit_event(
    db: Session,
    user_context: UserContext,
    action: str,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    audit = AuditLog(
        user_role=user_context.role,
        user_district=user_context.district,
        action=action,
        target_id=str(target_id) if target_id is not None else None,
        details=details or {}
    )
    db.add(audit)
    db.commit()
