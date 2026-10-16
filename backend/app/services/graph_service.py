from typing import Dict, Any, List
import networkx as nx
from sqlalchemy.orm import Session
from app.models import Case, MatchLink

def build_trafficking_graph(db: Session) -> Dict[str, Any]:
    G = nx.Graph()
    cases = db.query(Case).all()
    verified_matches = db.query(MatchLink).filter(MatchLink.status == "VERIFIED").all()

    nodes = []
    edges = []

    # 1. Add Case Nodes
    for case in cases:
        node_id = f"case_{case.id}"
        G.add_node(node_id, type="case", district=case.district, case_type=case.type, name=case.name, status=case.status)
        nodes.append({
            "data": {
                "id": node_id,
                "label": f"{case.case_number}: {case.name}",
                "type": "case",
                "case_type": case.type,
                "district": case.district,
                "status": case.status,
                "age": case.age,
                "sex": case.sex,
                "phone_numbers": case.phone_numbers,
            },
            "classes": f"node-case {case.type.lower()} district-{case.district.lower().replace(' ', '-')}"
        })

        # Add phone nodes and edges
        for phone in case.phone_numbers or []:
            phone_node_id = f"phone_{phone}"
            if not G.has_node(phone_node_id):
                G.add_node(phone_node_id, type="phone", phone=phone)
                nodes.append({
                    "data": {
                        "id": phone_node_id,
                        "label": f"📞 {phone}",
                        "type": "phone",
                    },
                    "classes": "node-phone"
                })
            G.add_edge(node_id, phone_node_id, relationship="SHARES_PHONE")
            edges.append({
                "data": {
                    "id": f"edge_{node_id}_{phone_node_id}",
                    "source": node_id,
                    "target": phone_node_id,
                    "label": "Shared Phone"
                },
                "classes": "edge-phone"
            })

        # Add location nodes and edges
        if case.last_seen_found_place:
            loc_node_id = f"loc_{case.district}_{case.last_seen_found_place.split(',')[0].strip()}"
            if not G.has_node(loc_node_id):
                G.add_node(loc_node_id, type="location", location=case.last_seen_found_place)
                nodes.append({
                    "data": {
                        "id": loc_node_id,
                        "label": f"📍 {case.last_seen_found_place.split(',')[0].strip()}",
                        "type": "location",
                        "district": case.district,
                    },
                    "classes": "node-location"
                })
            G.add_edge(node_id, loc_node_id, relationship="LAST_SEEN_FOUND_AT")
            edges.append({
                "data": {
                    "id": f"edge_{node_id}_{loc_node_id}",
                    "source": node_id,
                    "target": loc_node_id,
                    "label": "Location"
                },
                "classes": "edge-location"
            })

    # Add verified match edges
    for match in verified_matches:
        source_id = f"case_{match.source_case_id}"
        target_id = f"case_{match.target_case_id}"
        if G.has_node(source_id) and G.has_node(target_id):
            G.add_edge(source_id, target_id, relationship="VERIFIED_LINK")
            edges.append({
                "data": {
                    "id": f"edge_match_{match.id}",
                    "source": source_id,
                    "target": target_id,
                    "label": f"Verified Match ({int(match.score*100)}%)",
                    "score": match.score,
                },
                "classes": "edge-verified"
            })

    # Flag clusters of 3+ cases sharing a node (e.g. phone or location)
    flagged_clusters = []
    cluster_idx = 1
    for node, data in G.nodes(data=True):
        if data.get("type") in ["phone", "location"]:
            neighbors = [nbr for nbr in G.neighbors(node) if G.nodes[nbr].get("type") == "case"]
            if len(neighbors) >= 3:
                case_ids = [int(nbr.replace("case_", "")) for nbr in neighbors]
                districts = list(set([G.nodes[nbr].get("district") for nbr in neighbors]))
                flagged_clusters.append({
                    "cluster_id": f"CLUSTER-{cluster_idx:02d}",
                    "shared_node_type": data.get("type"),
                    "shared_value": node.replace("phone_", "").replace("loc_", ""),
                    "case_count": len(neighbors),
                    "case_ids": case_ids,
                    "districts": districts,
                    "risk_level": "CRITICAL" if len(districts) > 1 else "HIGH"
                })
                cluster_idx += 1

    return {
        "elements": {
            "nodes": nodes,
            "edges": edges,
        },
        "flagged_clusters": flagged_clusters,
        "summary": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "cluster_count": len(flagged_clusters)
        }
    }
