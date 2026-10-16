import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Case, MatchLink
from app.schemas import CaseCreate, CaseResponse
from app.auth import get_user_context, UserContext, log_audit_event
from app.services.matching import default_extractor, evaluate_match_score

router = APIRouter(prefix="/api/cases", tags=["Cases"])

def sanitize_case_for_privacy(case: Case, user_context: UserContext) -> CaseResponse:
    case_resp = CaseResponse.model_validate(case)
    # Cross-district sharing uses embeddings only, never raw photos for unverified cases
    if user_context.role == "Station Officer" and case.district != user_context.district:
        case_resp.photo_url = None  # Anonymize raw photo across district boundaries
    return case_resp

@router.get("", response_model=List[CaseResponse])
def get_cases(
    type: Optional[str] = Query(None, description="MISSING or FOUND"),
    district: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(Case)

    # Scoping filter - enforce role-based access
    if user_context.role == "Station Officer":
        # Station Officer can only see their own district cases (and any MATCHED cases for cross-district collaboration)
        if district and district != user_context.district:
            # Attempting to access another district - DENY unless role has cross-district access
            raise HTTPException(status_code=403, detail=f"Station Officer can only access cases from their own district: {user_context.district}")
        query = query.filter((Case.district == user_context.district) | (Case.status == "MATCHED"))
    elif user_context.role == "Investigating Officer":
        # IO can see all cases across all districts
        if district:
            query = query.filter(Case.district == district)
    elif user_context.role == "CWC Officer":
        # CWC can see all districts
        if district:
            query = query.filter(Case.district == district)
    else:
        raise HTTPException(status_code=403, detail="Unknown role")

    if type:
        query = query.filter(Case.type == type)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Case.name.ilike(search_pattern)) |
            (Case.case_number.ilike(search_pattern)) |
            (Case.marks.ilike(search_pattern))
        )

    cases = query.order_by(Case.created_at.desc()).all()

    # Log Audit
    log_audit_event(db, user_context, "VIEW_CASES_LIST", details={"filter_type": type, "district": district, "count": len(cases)})

    return [sanitize_case_for_privacy(c, user_context) for c in cases]

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    log_audit_event(db, user_context, "VIEW_CASE_DETAILS", target_id=str(case_id), details={"case_number": case.case_number, "district": case.district})

    return sanitize_case_for_privacy(case, user_context)

@router.post("", response_model=CaseResponse)
def create_case(
    case_in: CaseCreate,
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    # Auto-generate case number if missing
    dist_prefix = case_in.district[:3].upper()
    type_prefix = "M" if case_in.type == "MISSING" else "F"
    count = db.query(Case).count() + 1001
    case_num = case_in.case_number or f"{dist_prefix}-2026-{type_prefix}{count}"

    # Generate synthetic embedding if not supplied
    photo_seed = f"{case_in.name}_{case_in.age}_{case_in.district}"
    embedding = default_extractor.extract_embedding(photo_seed)

    new_case = Case(
        case_number=case_num,
        type=case_in.type,
        status="OPEN",
        name=case_in.name,
        devanagari_name=case_in.devanagari_name,
        aliases=case_in.aliases or [],
        age=case_in.age,
        sex=case_in.sex,
        height_cm=case_in.height_cm,
        marks=case_in.marks or "",
        clothing=case_in.clothing or "",
        language=case_in.language or "Marathi",
        last_seen_found_place=case_in.last_seen_found_place,
        last_seen_found_time=case_in.last_seen_found_time or datetime.datetime.utcnow(),
        latitude=case_in.latitude,
        longitude=case_in.longitude,
        district=case_in.district,
        phone_numbers=case_in.phone_numbers or [],
        photo_url=case_in.photo_url or f"https://picsum.photos/seed/{count}/200/200",
        photo_embedding=embedding,
        created_at=datetime.datetime.utcnow(),
        created_by_role=user_context.role,
        created_by_district=user_context.district,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    # Automatically run candidate match search against opposite type cases
    opposite_type = "FOUND" if new_case.type == "MISSING" else "MISSING"
    candidates = db.query(Case).filter(Case.type == opposite_type, Case.status == "OPEN").all()

    c1_dict = {
        "id": new_case.id, "name": new_case.name, "devanagari_name": new_case.devanagari_name,
        "age": new_case.age, "sex": new_case.sex, "height_cm": new_case.height_cm,
        "marks": new_case.marks, "clothing": new_case.clothing,
        "latitude": new_case.latitude, "longitude": new_case.longitude,
        "last_seen_found_time": new_case.last_seen_found_time,
        "phone_numbers": new_case.phone_numbers, "photo_embedding": new_case.photo_embedding,
    }

    new_matches_created = 0
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
        score = res["total_score"]
        if score >= 0.65:
            # Create MatchLink
            source_id = new_case.id if new_case.type == "MISSING" else cand.id
            target_id = cand.id if new_case.type == "MISSING" else new_case.id
            match_link = MatchLink(
                source_case_id=source_id,
                target_case_id=target_id,
                score=score,
                score_breakdown=res["breakdown"],
                status="PROBABLE"
            )
            db.add(match_link)
            new_matches_created += 1

    db.commit()

    log_audit_event(db, user_context, "INTAKE_CASE", target_id=str(new_case.id), details={
        "case_number": new_case.case_number,
        "type": new_case.type,
        "district": new_case.district,
        "matches_generated": new_matches_created
    })

    return sanitize_case_for_privacy(new_case, user_context)
