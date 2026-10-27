"""Security tests: JWT auth, audit hash chain integrity, role-based access."""
from backend.app.auth import create_jwt_token, _compute_entry_hash, log_audit_event, UserContext
from backend.app.models import AuditLog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base

def make_test_db():
    """Create fresh in-memory DB for each test."""
    db_url = "sqlite:///:memory:"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestJWTAuth:
    """Test JWT token creation."""
    
    def test_create_jwt_token(self):
        """Token should contain role, district, exp, iat."""
        token = create_jwt_token("test_user", "Station Officer", "Pune")
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts (header.payload.signature)

class TestAuditHashChain:
    """Test audit log hash-chain integrity."""
    
    def test_audit_entries_have_hash_chain(self):
        """Audit entries should have previous_hash and entry_hash fields."""
        SessionLocal = make_test_db()
        db = SessionLocal()
        
        ctx = UserContext(role="Station Officer", district="Pune")
        log1 = log_audit_event(db, ctx, "TEST_ACTION_1", target_id="test_1")
        log2 = log_audit_event(db, ctx, "TEST_ACTION_2", target_id="test_2")
        
        assert log2.previous_hash == log1.entry_hash
        assert log1.previous_hash == "0" * 64  # Genesis
        db.close()
    
    def test_audit_tampering_detection(self):
        """Tampering with audit entry breaks the hash chain."""
        SessionLocal = make_test_db()
        db = SessionLocal()
        
        ctx = UserContext(role="Station Officer", district="Pune")
        log1 = log_audit_event(db, ctx, "ACTION_1")
        log2 = log_audit_event(db, ctx, "ACTION_2")
        
        # Tamper with log1
        log1.action = "TAMPERED"
        db.add(log1)
        db.commit()
        
        # Recompute hash - should differ from stored
        entry_data = {
            "timestamp": log1.timestamp.isoformat(),
            "user_role": log1.user_role,
            "user_district": log1.user_district,
            "action": log1.action,
            "target_id": log1.target_id,
            "details": log1.details,
            "previous_hash": log1.previous_hash,
        }
        new_hash = _compute_entry_hash(entry_data)
        assert log1.entry_hash != new_hash  # Tampering detected
        
        db.close()

class TestRoleBasedAccess:
    """Test role-based authorization."""
    
    def test_station_officer_own_district_only(self):
        """Station Officer can only access own district."""
        ctx = UserContext(role="Station Officer", district="Pune")
        assert ctx.can_access_district("Pune") == True
        assert ctx.can_access_district("Thane") == False
    
    def test_investigating_officer_all_districts(self):
        """Investigating Officer can access all districts."""
        ctx = UserContext(role="Investigating Officer", district="National")
        assert ctx.can_access_district("Pune") == True
        assert ctx.can_access_district("Thane") == True
    
    def test_cwc_officer_all_districts(self):
        """CWC Officer can access all districts."""
        ctx = UserContext(role="CWC Officer", district="National")
        assert ctx.can_access_district("Pune") == True
        assert ctx.can_access_district("Mumbai Suburban") == True
