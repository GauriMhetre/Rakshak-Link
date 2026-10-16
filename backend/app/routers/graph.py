from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_user_context, UserContext, log_audit_event
from app.services.graph_service import build_trafficking_graph

router = APIRouter(prefix="/api/graph", tags=["Graph"])

@router.get("")
def get_graph(
    user_context: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    graph_data = build_trafficking_graph(db)

    log_audit_event(db, user_context, "VIEW_GRAPH", details={
        "total_nodes": graph_data["summary"]["total_nodes"],
        "clusters_flagged": graph_data["summary"]["cluster_count"]
    })

    return graph_data
