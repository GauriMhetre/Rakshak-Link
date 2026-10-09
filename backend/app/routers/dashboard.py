from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Case, MatchLink, AuditLog
from backend.app.auth import get_user_context, UserContext, log_audit_event
from backend.app.services.graph_service import build_trafficking_graph
from backend.app.services.matching import evaluate_match_score
from backend.seed import PLANTED_MATCHES_DATA

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

def compute_seed_precision_at_5(db: Session) -> float:
    found_cases = db.query(Case).filter(Case.type == "FOUND").all()
    if not found_cases:
        return 1.0

    hits = 0
    total = len(PLANTED_MATCHES_DATA)

    for planted in PLANTED_MATCHES_DATA:
        m_name = planted["missing"]["name"]
        f_name = planted["found"]["name"]
        m_case = db.query(Case).filter(Case.type == "MISSING", Case.name == m_name).first()

        if not m_case:
            continue

        m_dict = {
            "id": m_case.id, "name": m_case.name, "devanagari_name": m_case.devanagari_name,
            "age": m_case.age, "sex": m_case.sex, "height_cm": m_case.height_cm,
            "marks": m_case.marks, "clothing": m_case.clothing,
            "latitude": m_case.latitude, "longitude": m_case.longitude,
            "last_seen_found_time": m_case.last_seen_found_time,
            "phone_numbers": m_case.phone_numbers, "photo_embedding": m_case.photo_embedding,
        }

        candidates = []
        for f_case in found_cases:
            f_dict = {
                "id": f_case.id, "name": f_case.name, "devanagari_name": f_case.devanagari_name,
                "age": f_case.age, "sex": f_case.sex, "height_cm": f_case.height_cm,
                "marks": f_case.marks, "clothing": f_case.clothing,
                "latitude": f_case.latitude, "longitude": f_case.longitude,
                "last_seen_found_time": f_case.last_seen_found_time,
                "phone_numbers": f_case.phone_numbers, "photo_embedding": f_case.photo_embedding,
            }
            res = evaluate_match_score(m_dict, f_dict)
            candidates.append((f_case.name, res["total_score"]))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top5_names = [cand[0] for cand in candidates[:5]]

        if f_name in top5_names:
            hits += 1

    return round(hits / float(total if total > 0 else 1), 3)

@router.get("")
def get_dashboard_metrics(
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    open_missing = db.query(Case).filter(Case.type == "MISSING", Case.status == "OPEN").count()
    open_found = db.query(Case).filter(Case.type == "FOUND", Case.status == "OPEN").count()
    total_open = open_missing + open_found

    probable_matches = db.query(MatchLink).filter(MatchLink.status == "PROBABLE").count()
    verified_links = db.query(MatchLink).filter(MatchLink.status == "VERIFIED").count()

    graph_data = build_trafficking_graph(db)
    flagged_clusters = graph_data["summary"]["cluster_count"]

    precision_at_5 = compute_seed_precision_at_5(db)

    # District Breakdown
    districts = ["Pune", "Mumbai Suburban", "Thane", "Nagpur"]
    district_stats = {}
    for d in districts:
        m_cnt = db.query(Case).filter(Case.district == d, Case.type == "MISSING").count()
        f_cnt = db.query(Case).filter(Case.district == d, Case.type == "FOUND").count()
        district_stats[d] = {"missing": m_cnt, "found": f_cnt, "total": m_cnt + f_cnt}

    # Recent Audit Log Activity
    recent_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()
    audit_stream = [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else "",
            "role": log.user_role,
            "district": log.user_district,
            "action": log.action,
            "target_id": log.target_id,
            "details": log.details,
        }
        for log in recent_logs
    ]

    log_audit_event(db, user_context, "VIEW_DASHBOARD")

    return {
        "metrics": {
            "total_open_cases": total_open,
            "open_missing": open_missing,
            "open_found": open_found,
            "probable_matches": probable_matches,
            "verified_links": verified_links,
            "flagged_clusters": flagged_clusters,
            "precision_at_5": precision_at_5,
            "precision_at_5_percentage": f"{int(precision_at_5 * 100)}%"
        },
        "district_stats": district_stats,
        "clusters": graph_data["flagged_clusters"],
        "recent_activity": audit_stream,
    }
