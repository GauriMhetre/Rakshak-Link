import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import AuditLog

# Demo JWT secret (use env var in production)
JWT_SECRET = "demo-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# Demo mock users (role, district, password)
DEMO_USERS = {
    "officer_pune": {"role": "Station Officer", "district": "Pune", "password": "demo123"},
    "cwc_thane": {"role": "CWC Officer", "district": "Thane", "password": "demo123"},
    "io_investigator": {"role": "Investigating Officer", "district": "National", "password": "demo123"},
}

class UserContext:
    def __init__(self, role: str, district: str):
        self.role = role
        self.district = district

    def can_access_district(self, target_district: str) -> bool:
        if self.role in ["Investigating Officer", "CWC Officer", "Admin"]:
            return True
        return self.district == target_district

def create_jwt_token(username: str, role: str, district: str, expires_in_hours: int = 24) -> str:
    """Create a demo JWT token."""
    payload = {
        "username": username,
        "role": role,
        "district": district,
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_context(
    x_user_role: Optional[str] = Header(None),
    x_user_district: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
) -> UserContext:
    """Extract user context from JWT token or fallback to header-based demo auth."""
    # Try JWT if provided
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = verify_jwt_token(token)
        return UserContext(role=payload["role"], district=payload["district"])
    
    # Fallback to demo headers (for backward compatibility)
    role = x_user_role or "Station Officer"
    district = x_user_district or "Pune"
    return UserContext(role=role, district=district)

def _compute_entry_hash(entry: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of audit log entry."""
    entry_str = json.dumps(entry, sort_keys=True, default=str)
    return hashlib.sha256(entry_str.encode()).hexdigest()

def log_audit_event(
    db: Session,
    user_context: UserContext,
    action: str,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Log an audit event with hash-chain integrity."""
    # Get previous entry to compute hash chain
    previous_entry = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    previous_hash = previous_entry.entry_hash if previous_entry else "0" * 64  # Genesis block
    
    # Build entry dict for hashing
    entry_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_role": user_context.role,
        "user_district": user_context.district,
        "action": action,
        "target_id": target_id,
        "details": details or {},
        "previous_hash": previous_hash,
    }
    
    # Compute hash
    entry_hash = _compute_entry_hash(entry_data)
    
    audit = AuditLog(
        user_role=user_context.role,
        user_district=user_context.district,
        action=action,
        target_id=str(target_id) if target_id is not None else None,
        details=details or {},
        previous_hash=previous_hash,
        entry_hash=entry_hash,
    )
    db.add(audit)
    db.commit()
    return audit
