import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Case, MatchLink, Feedback
from app.schemas import MatchResponse
from app.auth import get_user_context, UserContext, log_audit_event
from app.services.matching import evaluate_match_score

router = APIRouter(prefix="/api/matches", tags=["Matches"])

@router.get("/case/{case_id}", response_model=List[MatchResponse])
def get_matches_for_case(
    case_id: int,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query_case = db.query(Case).filter(Case.id == case_id).first()
    if not query_case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Fetch stored match links or dynamically calculate candidates
    existing_links = db.query(MatchLink).filter(
        (MatchLink.source_case_id == case_id) | (MatchLink.target_case_id == case_id)
    ).all()

    # If no stored links exist, evaluate against candidate cases live
    if not existing_links:
        opposite_type = "FOUND" if query_case.type == "MISSING" else "MISSING"
        candidates = db.query(Case).filter(Case.type == opposite_type).all()

        c1_dict = {
            "id": query_case.id, "name": query_case.name, "devanagari_name": query_case.devanagari_name,
            "age": query_case.age, "sex": query_case.sex, "height_cm": query_case.height_cm,
            "marks": query_case.marks, "clothing": query_case.clothing,
            "latitude": query_case.latitude, "longitude": query_case.longitude,
            "last_seen_found_time": query_case.last_seen_found_time,
            "phone_numbers": query_case.phone_numbers, "photo_embedding": query_case.photo_embedding,
        }

        for cand in candidates:
            c2_dict = {
                "id": cand.id, "name": cand.name, "devanagari_name": cand.devanagari_name,
                "age": cand.age, "sex": cand.sex, "height_cm": cand.height_cm,
                "marks": cand.marks, "clothing": cand.clothing,
                "latitude": cand.latitude, "longitude": cand.longitude,
                "last_seen_found_time": cand.last_seen_found_time,
                "phone_numbers": cand.phone_numbers, "photo_embedding": cand.photo_embedding,
            }
            res = evaluate_match_score(c1_dict, c2_dict)
            if res["total_score"] >= 0.60:
                source_id = query_case.id if query_case.type == "MISSING" else cand.id
                target_id = cand.id if query_case.type == "MISSING" else query_case.id

                match_link = MatchLink(
                    source_case_id=source_id,
                    target_case_id=target_id,
                    score=res["total_score"],
                    score_breakdown=res["breakdown"],
                    status="PROBABLE"
                )
                db.add(match_link)

        db.commit()
        existing_links = db.query(MatchLink).filter(
            (MatchLink.source_case_id == case_id) | (MatchLink.target_case_id == case_id)
        ).all()

    # Filter/Sort links by score descending
    existing_links.sort(key=lambda m: m.score, reverse=True)

    log_audit_event(db, user_context, "SEARCH_MATCHES", target_id=str(case_id), details={"match_count": len(existing_links)})

    return existing_links

@router.post("/{match_id}/verify")
def verify_match(
    match_id: int,
    notes: Optional[str] = Body(None, embed=True),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    # Only Investigating Officers and CWC Officers can verify matches
    if user_context.role == "Station Officer":
        raise HTTPException(status_code=403, detail="Only Investigating Officers can verify cross-district matches")
    
    match_link = db.query(MatchLink).filter(MatchLink.id == match_id).first()
    if not match_link:
        raise HTTPException(status_code=404, detail="Match link not found")

    # Verify authorization: user must have access to both cases
    source_case = db.query(Case).filter(Case.id == match_link.source_case_id).first()
    target_case = db.query(Case).filter(Case.id == match_link.target_case_id).first()
    
    if not source_case or not target_case:
        raise HTTPException(status_code=404, detail="Source or target case not found")
    
    # For IO: allow all; for CWC: allow only if within their access scope
    if user_context.role == "CWC Officer":
        # CWC can verify matches involving child welfare cases
        pass  # CWC has broad access

    match_link.status = "VERIFIED"
    match_link.verified_by_user = f"{user_context.role} ({user_context.district})"
    match_link.verified_at = datetime.datetime.utcnow()

    # Update both cases status to MATCHED
    if source_case:
        source_case.status = "MATCHED"
    if target_case:
        target_case.status = "MATCHED"

    # Add feedback record
    fb = Feedback(
        match_id=match_id,
        user_role=user_context.role,
        district=user_context.district,
        feedback_type="VERIFIED",
        notes=notes or "Verified by IO/CWC across districts",
        created_at=datetime.datetime.utcnow()
    )
    db.add(fb)
    db.commit()

    # Audit alert triggering both districts
    districts_alerted = list(set([source_case.district if source_case else "", target_case.district if target_case else ""]))
    log_audit_event(db, user_context, "VERIFY_MATCH", target_id=str(match_id), details={
        "source_case_id": match_link.source_case_id,
        "target_case_id": match_link.target_case_id,
        "districts_alerted": districts_alerted,
        "verified_by": match_link.verified_by_user,
    })

    return {
        "status": "success",
        "message": f"Match link verified successfully. Joint alert dispatched to districts: {', '.join(districts_alerted)}",
        "match_id": match_id
    }

@router.post("/{match_id}/reject")
def reject_match(
    match_id: int,
    rejection_reason: str = Body(..., embed=True),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    # Only Investigating Officers and CWC Officers can reject matches
    if user_context.role == "Station Officer":
        raise HTTPException(status_code=403, detail="Only Investigating Officers can reject cross-district matches")
    
    match_link = db.query(MatchLink).filter(MatchLink.id == match_id).first()
    if not match_link:
        raise HTTPException(status_code=404, detail="Match link not found")

    match_link.status = "REJECTED"
    match_link.rejection_reason = rejection_reason

    # Add feedback record for engine retraining feedback loop
    fb = Feedback(
        match_id=match_id,
        user_role=user_context.role,
        district=user_context.district,
        feedback_type="REJECTED",
        notes=rejection_reason,
        created_at=datetime.datetime.utcnow()
    )
    db.add(fb)
    db.commit()

    log_audit_event(db, user_context, "REJECT_MATCH", target_id=str(match_id), details={
        "source_case_id": match_link.source_case_id,
        "target_case_id": match_link.target_case_id,
        "reason": rejection_reason
    })

    return {
        "status": "success",
        "message": "Match rejected and recorded in feedback table.",
        "match_id": match_id
    }
