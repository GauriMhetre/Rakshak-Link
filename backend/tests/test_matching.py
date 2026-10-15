import pytest
import datetime
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, Base, engine
from backend.app.models import Case
from backend.app.services.matching import evaluate_match_score
from backend.seed import PLANTED_MATCHES_DATA, seed_db

@pytest.fixture(scope="module")
def seeded_db():
    seed_db()
    db = SessionLocal()
    yield db
    db.close()

def test_planted_matches_rank_top_5(seeded_db: Session):
    # Retrieve all MISSING cases and all FOUND cases
    missing_cases = seeded_db.query(Case).filter(Case.type == "MISSING").all()
    found_cases = seeded_db.query(Case).filter(Case.type == "FOUND").all()

    assert len(missing_cases) >= 15, "Expected at least 15 missing cases"
    assert len(found_cases) >= 15, "Expected at least 15 found cases"

    top5_hits = 0
    total_planted_tested = 0

    for planted in PLANTED_MATCHES_DATA:
        m_name = planted["missing"]["name"]
        f_name = planted["found"]["name"]

        # Find the query missing case
        m_case = seeded_db.query(Case).filter(Case.type == "MISSING", Case.name == m_name).first()
        assert m_case is not None, f"Query missing case {m_name} not found in DB"

        m_dict = {
            "id": m_case.id, "name": m_case.name, "devanagari_name": m_case.devanagari_name,
            "age": m_case.age, "sex": m_case.sex, "height_cm": m_case.height_cm,
            "marks": m_case.marks, "clothing": m_case.clothing,
            "latitude": m_case.latitude, "longitude": m_case.longitude,
            "last_seen_found_time": m_case.last_seen_found_time,
            "phone_numbers": m_case.phone_numbers, "photo_embedding": m_case.photo_embedding,
        }

        # Score against all FOUND cases
        scored_candidates = []
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
            scored_candidates.append((f_case, res["total_score"], res["breakdown"]))

        # Sort by total score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        top_5_names = [cand[0].name for cand in scored_candidates[:5]]
        total_planted_tested += 1

        if f_name in top_5_names:
            top5_hits += 1

    precision_at_5 = top5_hits / float(total_planted_tested)
    print(f"\nPrecision@5 on planted test set: {precision_at_5 * 100:.2f}% ({top5_hits}/{total_planted_tested})")

    # Assert that precision@5 is >= 90% (all or nearly all planted matches rank in top 5)
    assert precision_at_5 >= 0.90, f"Precision@5 too low: {precision_at_5}"

def test_no_face_detected_skips_signal():
    """Test that None embeddings don't crash matching and face signal is skipped."""
    c1 = {
        "id": 1, "name": "Alice", "devanagari_name": None,
        "age": 25, "sex": "FEMALE", "height_cm": 160.0,
        "marks": "Scar", "clothing": "Red dress",
        "latitude": 18.5, "longitude": 73.8,
        "last_seen_found_time": datetime.datetime.utcnow(),
        "phone_numbers": [], "photo_embedding": None,  # No face
    }
    c2 = {
        "id": 2, "name": "Alice Similar", "devanagari_name": None,
        "age": 25, "sex": "FEMALE", "height_cm": 161.0,
        "marks": "Scar", "clothing": "Red dress",
        "latitude": 18.5, "longitude": 73.8,
        "last_seen_found_time": datetime.datetime.utcnow(),
        "phone_numbers": [], "photo_embedding": None,  # No face
    }
    
    result = evaluate_match_score(c1, c2)
    assert result["total_score"] >= 0.0
    assert result["total_score"] <= 1.0
    assert result["breakdown"]["face_score"] == 0.5  # Neutral fallback
    print(f"No-face test passed. Score: {result['total_score']}")

def test_transliteration_and_fuzzy():
    from backend.app.services.transliteration import devanagari_to_latin, compute_phonetic_fuzzy_similarity
    latin = devanagari_to_latin("रमेश शर्मा")
    assert "ramesh" in latin.lower()

    sim = compute_phonetic_fuzzy_similarity("Ramesh Sharma", "रमेश शर्मा", "Ramesh Shrama", "रमेश शर्मा")
    assert sim >= 0.85
