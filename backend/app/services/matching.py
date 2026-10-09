import math
import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from rapidfuzz import fuzz
from .transliteration import compute_phonetic_fuzzy_similarity

# --- Pluggable Embedding Extractor Interface ---
class EmbeddingExtractorInterface:
    """
    Pluggable Face Embedding Extractor Interface.
    Default implementation uses deterministic synthetic feature hashing.
    In production, this interface can be backed by ResNet / ArcFace / FaceNet models.
    """
    def extract_embedding(self, input_data: str) -> List[float]:
        raise NotImplementedError("Subclasses must implement extract_embedding")

class SyntheticEmbeddingExtractor(EmbeddingExtractorInterface):
    """
    Default deterministic synthetic embedding extractor.
    LIMITATION: Generates pseudo-random 128-dim normalized vectors based on input hash.
    For production face recognition, replace with deep learning vision model.
    """
    def extract_embedding(self, input_data: str) -> List[float]:
        seed_val = int(abs(hash(input_data))) % (2**32)
        rng = np.random.RandomState(seed_val)
        vec = rng.randn(128)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

# Singleton default extractor instance
default_extractor = SyntheticEmbeddingExtractor()

# --- Signal Computation Helpers ---

def compute_cosine_similarity(vec1: Optional[List[float]], vec2: Optional[List[float]]) -> float:
    if not vec1 or not vec2:
        return 0.5  # Neutral fallback when embedding missing
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    dot_prod = np.dot(v1, v2)
    sim = dot_prod / (norm1 * norm2)
    # Clamp to [0, 1]
    return float(max(0.0, min(1.0, (sim + 1.0) / 2.0)))

def compute_attribute_similarity(c1: Dict[str, Any], c2: Dict[str, Any]) -> tuple[float, Dict[str, Any]]:
    # Sex match
    sex_score = 1.0 if c1.get("sex") == c2.get("sex") else 0.0

    # Age difference penalty
    age1 = c1.get("age", 0)
    age2 = c2.get("age", 0)
    age_diff = abs(age1 - age2)
    if age_diff == 0:
        age_score = 1.0
    elif age_diff <= 2:
        age_score = 0.9
    elif age_diff <= 5:
        age_score = 0.6
    else:
        age_score = max(0.0, 1.0 - (age_diff / 15.0))

    # Height difference penalty
    h1 = c1.get("height_cm", 160.0)
    h2 = c2.get("height_cm", 160.0)
    h_diff = abs(h1 - h2)
    if h_diff <= 2.0:
        height_score = 1.0
    elif h_diff <= 5.0:
        height_score = 0.8
    else:
        height_score = max(0.0, 1.0 - (h_diff / 25.0))

    # Marks overlap using token ratio
    m1 = c1.get("marks", "") or ""
    m2 = c2.get("marks", "") or ""
    marks_score = fuzz.token_set_ratio(m1, m2) / 100.0 if (m1 and m2) else 0.5

    # Clothing overlap
    cl1 = c1.get("clothing", "") or ""
    cl2 = c2.get("clothing", "") or ""
    clothing_score = fuzz.token_set_ratio(cl1, cl2) / 100.0 if (cl1 and cl2) else 0.5

    # Composite attribute score
    total_attr = (0.25 * sex_score + 0.25 * age_score + 0.20 * height_score + 0.15 * marks_score + 0.15 * clothing_score)
    details = {
        "sex_match": sex_score,
        "age_score": round(age_score, 2),
        "height_score": round(height_score, 2),
        "marks_score": round(marks_score, 2),
        "clothing_score": round(clothing_score, 2),
    }
    return float(total_attr), details

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def compute_geotime_similarity(c1: Dict[str, Any], c2: Dict[str, Any]) -> tuple[float, Dict[str, Any]]:
    lat1, lon1 = c1.get("latitude", 0.0), c1.get("longitude", 0.0)
    lat2, lon2 = c2.get("latitude", 0.0), c2.get("longitude", 0.0)
    dist_km = haversine_distance_km(lat1, lon1, lat2, lon2)

    t1 = c1.get("last_seen_found_time")
    t2 = c2.get("last_seen_found_time")

    if isinstance(t1, str):
        t1 = datetime.datetime.fromisoformat(t1)
    if isinstance(t2, str):
        t2 = datetime.datetime.fromisoformat(t2)

    if t1 and t2:
        hours_diff = abs((t2 - t1).total_seconds()) / 3600.0
    else:
        hours_diff = 24.0

    # Required travel speed (km/h)
    req_speed = dist_km / max(hours_diff, 1.0)

    # Plausibility scoring curve for inter-district transport in Maharashtra
    if dist_km < 5.0 and hours_diff <= 72.0:
        geo_score = 1.0
    elif req_speed <= 80.0:  # Normal road/rail transport speed
        geo_score = max(0.6, 1.0 - (dist_km / 1500.0))
    elif req_speed <= 150.0: # High speed highway/express train
        geo_score = 0.5
    else:
        geo_score = 0.2

    details = {
        "distance_km": round(dist_km, 1),
        "time_diff_hours": round(hours_diff, 1),
        "required_speed_kmh": round(req_speed, 1),
    }
    return float(geo_score), details

# --- Fused Match Evaluator ---

def evaluate_match_score(c1_dict: Dict[str, Any], c2_dict: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Face Cosine Similarity
    face_sim = compute_cosine_similarity(c1_dict.get("photo_embedding"), c2_dict.get("photo_embedding"))

    # 2. Name Similarity (Fuzzy + Phonetic + Devanagari)
    name_sim = compute_phonetic_fuzzy_similarity(
        c1_dict.get("name", ""), c1_dict.get("devanagari_name", ""),
        c2_dict.get("name", ""), c2_dict.get("devanagari_name", "")
    )

    # 3. Attribute Overlap
    attr_sim, attr_details = compute_attribute_similarity(c1_dict, c2_dict)

    # 4. Geo-Time Plausibility
    geotime_sim, geotime_details = compute_geotime_similarity(c1_dict, c2_dict)

    # Fused Weighted Score
    # Face: 0.35, Name: 0.25, Attr: 0.20, GeoTime: 0.20
    total_score = (0.35 * face_sim) + (0.25 * name_sim) + (0.20 * attr_sim) + (0.20 * geotime_sim)

    # Flag phone match bonus if shared phone numbers exist
    phones1 = set(c1_dict.get("phone_numbers") or [])
    phones2 = set(c2_dict.get("phone_numbers") or [])
    shared_phones = list(phones1.intersection(phones2))
    if shared_phones:
        total_score = min(1.0, total_score + 0.10)

    breakdown = {
        "face_score": round(face_sim, 3),
        "name_score": round(name_sim, 3),
        "attr_score": round(attr_sim, 3),
        "geotime_score": round(geotime_sim, 3),
        "details": {
            "attr_details": attr_details,
            "geotime_details": geotime_details,
            "shared_phones": shared_phones,
        }
    }

    return {
        "total_score": round(total_score, 3),
        "breakdown": breakdown
    }
