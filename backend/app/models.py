import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True)
    type = Column(String, index=True)  # MISSING or FOUND
    status = Column(String, default="OPEN", index=True)  # OPEN, MATCHED, RESOLVED
    name = Column(String, index=True)
    devanagari_name = Column(String, nullable=True)
    aliases = Column(JSON, default=list)
    age = Column(Integer)
    sex = Column(String)  # MALE, FEMALE, OTHER
    height_cm = Column(Float)
    marks = Column(Text, default="")
    clothing = Column(Text, default="")
    language = Column(String, default="")
    last_seen_found_place = Column(String)
    last_seen_found_time = Column(DateTime, default=datetime.datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
    district = Column(String, index=True)  # Pune, Mumbai Suburban, Thane, Nagpur
    phone_numbers = Column(JSON, default=list)
    photo_url = Column(String, nullable=True)
    photo_embedding = Column(JSON, nullable=True)  # List of 512 floats (InsightFace/synthetic)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by_role = Column(String, default="Station Officer")
    created_by_district = Column(String)

class MatchLink(Base):
    __tablename__ = "match_links"

    id = Column(Integer, primary_key=True, index=True)
    source_case_id = Column(Integer, ForeignKey("cases.id"), index=True)
    target_case_id = Column(Integer, ForeignKey("cases.id"), index=True)
    score = Column(Float)
    score_breakdown = Column(JSON)  # face, name, attr, geotime scores & explanations
    status = Column(String, default="PROBABLE", index=True)  # PROBABLE, VERIFIED, REJECTED
    verified_by_user = Column(String, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    source_case = relationship("Case", foreign_keys=[source_case_id])
    target_case = relationship("Case", foreign_keys=[target_case_id])

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("match_links.id"))
    user_role = Column(String)
    district = Column(String)
    feedback_type = Column(String)  # VERIFIED or REJECTED
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    user_role = Column(String)
    user_district = Column(String)
    action = Column(String, index=True)
    target_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
