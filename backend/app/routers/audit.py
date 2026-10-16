from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponse
from app.auth import get_user_context, UserContext, log_audit_event

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(50, le=200),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)

    # If Station Officer, scope audit logs to their district or system actions
    if user_context.role == "Station Officer":
        query = query.filter((AuditLog.user_district == user_context.district) | (AuditLog.user_district == "State HQ"))

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    log_audit_event(db, user_context, "VIEW_AUDIT_LOGS", details={"retrieved_count": len(logs)})

    return logs
