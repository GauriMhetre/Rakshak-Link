import os
import random
import datetime
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import Case, MatchLink, Feedback, AuditLog
from app.services.matching import EMBEDDING_DIM

# Pluggable deterministic synthetic embedding generator
def generate_synthetic_embedding(seed_str: str, noise_level: float = 0.0) -> list[float]:
    # Hash seed_str to create a base seed integer
    seed_val = int(abs(hash(seed_str))) % (2**32)
    rng = np.random.RandomState(seed_val)
    vec = rng.randn(EMBEDDING_DIM)
    if noise_level > 0:
        noise = np.random.randn(EMBEDDING_DIM) * noise_level
        vec = vec + noise
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

def load_real_face_embedding(photo_path: str) -> list[float]:
    """Load real face embedding from InsightFace."""
    try:
        from app.services.insightface_extractor import InsightFaceExtractor
        extractor = InsightFaceExtractor()
        emb = extractor.extract_embedding(photo_path)
        if emb is None:
            return generate_synthetic_embedding(f"fallback_{photo_path}")
        return emb
    except Exception as e:
        print(f"  Warning: failed to extract face from {photo_path}: {e}")
        return generate_synthetic_embedding(f"fallback_{photo_path}")

DISTRICT_COORDS = {
    "Pune": (18.5204, 73.8567),
    "Mumbai Suburban": (19.0760, 72.8777),
    "Thane": (19.2183, 72.9781),
    "Nagpur": (21.1458, 79.0882),
}

FIRST_NAMES = ["Aarav", "Ramesh", "Priya", "Rahul", "Ananya", "Vikram", "Suresh", "Kavita", "Siddharth", "Pooja", "Sunil", "Meera", "Amit", "Neha", "Vijay", "Deepak", "Sneha", "Ganesh", "Rohit", "Lakshmi"]
LAST_NAMES = ["Sharma", "Deshmukh", "Kulkarni", "Patil", "Jadhav", "Pawar", "Shinde", "Chavan", "Gaekwad", "Joshi", "More", "Rao", "Kamble", "Sawant", "Bhosale", "Wagh", "Pandey", "Verma", "Singh", "Gupta"]

CLOTHING_ITEMS = ["Blue jeans, white t-shirt", "Red saree, gold border", "Black trousers, striped shirt", "Yellow salwar kameez", "Green jacket, grey denim", "Brown shirt, khaki pants", "Floral print dress"]
MARKS_ITEMS = ["Mole on right cheek", "Scar on left knee", "Tattoo of trident on forearm", "Burn mark on right hand", "Mole on forehead", "Missing upper left tooth", "Birthmark on neck"]
LANGUAGES = ["Marathi", "Hindi", "English", "Gujarati", "Kannada"]

PLANTED_MATCHES_DATA = [
    {
        "missing": {"name": "Ramesh Sharma", "devanagari": "रमेश शर्मा", "district": "Pune", "age": 14, "sex": "MALE", "height": 152.0, "marks": "Mole on right cheek", "clothing": "Blue jeans, white shirt", "phone": "+919820012345", "days_ago": 10},
        "found": {"name": "Ramesh Shrama", "devanagari": "रमेश शर्मा", "district": "Thane", "age": 14, "sex": "MALE", "height": 154.0, "marks": "Black mole right cheek", "clothing": "Blue trousers, light top", "phone": "+919820012345", "days_ago": 7},
    },
    {
        "missing": {"name": "Priya Kulkarni", "devanagari": "प्रिया कुलकर्णी", "district": "Mumbai Suburban", "age": 16, "sex": "FEMALE", "height": 160.0, "marks": "Scar on left knee", "clothing": "Yellow salwar kameez", "phone": "+919820012345", "days_ago": 15},
        "found": {"name": "Pria Kulkarnii", "devanagari": "प्रिया कुलकर्णी", "district": "Nagpur", "age": 17, "sex": "FEMALE", "height": 161.0, "marks": "Old scar left leg knee", "clothing": "Yellow kurti", "phone": "+919820012345", "days_ago": 11},
    },
    {
        "missing": {"name": "Rahul Deshmukh", "devanagari": "राहुल देशमुख", "district": "Pune", "age": 12, "sex": "MALE", "height": 145.0, "marks": "Tattoo of trident on forearm", "clothing": "Red t-shirt, shorts", "phone": "+919820012345", "days_ago": 20},
        "found": {"name": "Rahul Dashmukh", "devanagari": "राहुल देशमुख", "district": "Thane", "age": 12, "sex": "MALE", "height": 146.0, "marks": "Trident tattoo left arm", "clothing": "Red shirt", "phone": "+919820012345", "days_ago": 18},
    },
    {
        "missing": {"name": "Ananya Patil", "devanagari": "अनन्या पाटील", "district": "Thane", "age": 15, "sex": "FEMALE", "height": 155.0, "marks": "Mole on forehead", "clothing": "Green jacket", "phone": "+919930098765", "days_ago": 8},
        "found": {"name": "Ananya Patel", "devanagari": "अनन्या पाटील", "district": "Mumbai Suburban", "age": 15, "sex": "FEMALE", "height": 156.0, "marks": "Small mole center forehead", "clothing": "Green hoodie", "phone": "+919930098765", "days_ago": 5},
    },
    {
        "missing": {"name": "Vikram Pawar", "devanagari": "विक्रम पवार", "district": "Nagpur", "age": 22, "sex": "MALE", "height": 175.0, "marks": "Burn mark on right hand", "clothing": "Black trousers, grey shirt", "phone": "+919930098765", "days_ago": 12},
        "found": {"name": "Vikram Powar", "devanagari": "विक्रम पवार", "district": "Pune", "age": 22, "sex": "MALE", "height": 174.0, "marks": "Burn mark right wrist", "clothing": "Dark pants", "phone": "+919930098765", "days_ago": 9},
    },
    {
        "missing": {"name": "Suresh Jadhav", "devanagari": "सुरेश जाधव", "district": "Pune", "age": 10, "sex": "MALE", "height": 138.0, "marks": "Missing upper left tooth", "clothing": "School uniform white blue", "phone": "+919811122233", "days_ago": 6},
        "found": {"name": "Suresh Jadav", "devanagari": "सुरेश जाधव", "district": "Mumbai Suburban", "age": 10, "sex": "MALE", "height": 139.0, "marks": "Missing tooth front left", "clothing": "Dirty school uniform", "phone": "+919811122233", "days_ago": 4},
    },
    {
        "missing": {"name": "Kavita Shinde", "devanagari": "कविता शिंदे", "district": "Mumbai Suburban", "age": 18, "sex": "FEMALE", "height": 158.0, "marks": "Birthmark on neck", "clothing": "Floral print dress", "phone": "+919711223344", "days_ago": 25},
        "found": {"name": "Kavita Shinde", "devanagari": "कविता शिंदे", "district": "Nagpur", "age": 18, "sex": "FEMALE", "height": 158.0, "marks": "Brown birthmark right neck", "clothing": "Floral frock", "phone": "+919711223344", "days_ago": 21},
    },
    {
        "missing": {"name": "Siddharth Chavan", "devanagari": "सिद्धार्थ चव्हाण", "district": "Thane", "age": 13, "sex": "MALE", "height": 148.0, "marks": "Mole on right cheek", "clothing": "Checkered shirt", "phone": "+919611334455", "days_ago": 14},
        "found": {"name": "Sidarth Chavan", "devanagari": "सिद्धार्थ चव्हाण", "district": "Pune", "age": 13, "sex": "MALE", "height": 150.0, "marks": "Mole right side cheek", "clothing": "Red checkered shirt", "phone": "+919611334455", "days_ago": 10},
    },
    {
        "missing": {"name": "Pooja Gaekwad", "devanagari": "पूजा गायकवाड", "district": "Nagpur", "age": 19, "sex": "FEMALE", "height": 162.0, "marks": "Scar on left knee", "clothing": "Blue denim top", "phone": "+919511445566", "days_ago": 18},
        "found": {"name": "Pooja Gaikwad", "devanagari": "पूजा गायकवाड", "district": "Thane", "age": 19, "sex": "FEMALE", "height": 163.0, "marks": "Knee scar left leg", "clothing": "Blue denim top", "phone": "+919511445566", "days_ago": 15},
    },
    {
        "missing": {"name": "Sunil Joshi", "devanagari": "सुनील जोशी", "district": "Pune", "age": 28, "sex": "MALE", "height": 170.0, "marks": "Tattoo of trident on forearm", "clothing": "Grey polo shirt", "phone": "+919411556677", "days_ago": 30},
        "found": {"name": "Suneel Joshi", "devanagari": "सुनील जोशी", "district": "Nagpur", "age": 28, "sex": "MALE", "height": 171.0, "marks": "Trident tattoo arm", "clothing": "Grey t-shirt", "phone": "+919411556677", "days_ago": 26},
    },
    {
        "missing": {"name": "Meera More", "devanagari": "मीरा मोरे", "district": "Mumbai Suburban", "age": 11, "sex": "FEMALE", "height": 140.0, "marks": "Mole on forehead", "clothing": "Pink sweater", "phone": "+919311667788", "days_ago": 9},
        "found": {"name": "Meera Mohite", "devanagari": "मीरा मोरे", "district": "Pune", "age": 11, "sex": "FEMALE", "height": 141.0, "marks": "Mole center forehead", "clothing": "Pink jacket", "phone": "+919311667788", "days_ago": 7},
    },
    {
        "missing": {"name": "Amit Rao", "devanagari": "अमित राव", "district": "Thane", "age": 17, "sex": "MALE", "height": 168.0, "marks": "Burn mark on right hand", "clothing": "White hoodie", "phone": "+919211778899", "days_ago": 16},
        "found": {"name": "Amitt Rao", "devanagari": "अमित राव", "district": "Nagpur", "age": 17, "sex": "MALE", "height": 169.0, "marks": "Hand burn scar right", "clothing": "White sweater", "phone": "+919211778899", "days_ago": 12},
    },
    {
        "missing": {"name": "Neha Kamble", "devanagari": "नेहा कांबळे", "district": "Nagpur", "age": 14, "sex": "FEMALE", "height": 150.0, "marks": "Missing upper left tooth", "clothing": "Purple dress", "phone": "+919111889900", "days_ago": 22},
        "found": {"name": "Neha Kamble", "devanagari": "नेहा कांबळे", "district": "Mumbai Suburban", "age": 14, "sex": "FEMALE", "height": 151.0, "marks": "Missing left upper tooth", "clothing": "Purple kurti", "phone": "+919111889900", "days_ago": 19},
    },
    {
        "missing": {"name": "Vijay Sawant", "devanagari": "विजय सावंत", "district": "Pune", "age": 25, "sex": "MALE", "height": 172.0, "marks": "Birthmark on neck", "clothing": "Brown jacket", "phone": "+919011990011", "days_ago": 11},
        "found": {"name": "Vijay Sawannt", "devanagari": "विजय सावंत", "district": "Thane", "age": 25, "sex": "MALE", "height": 172.0, "marks": "Neck birthmark back", "clothing": "Brown coat", "phone": "+919011990011", "days_ago": 8},
    },
    {
        "missing": {"name": "Deepak Bhosale", "devanagari": "दीपक भोसले", "district": "Mumbai Suburban", "age": 15, "sex": "MALE", "height": 158.0, "marks": "Mole on right cheek", "clothing": "Orange track suit", "phone": "+918911001122", "days_ago": 13},
        "found": {"name": "Dipak Bhosale", "devanagari": "दीपक भोसले", "district": "Nagpur", "age": 15, "sex": "MALE", "height": 159.0, "marks": "Dark mole right cheek", "clothing": "Orange jacket", "phone": "+918911001122", "days_ago": 10},
    },
]

def seed_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    now = datetime.datetime.utcnow()
    case_counter = 1000
    
    # Check if real faces are available and backend is insightface
    # Resolve path relative to project root (parent of backend/)
    faces_dir = Path(__file__).parent.parent / "data" / "faces"
    use_real_faces = faces_dir.exists() and os.getenv("EMBEDDING_BACKEND", "synthetic").lower() == "insightface"
    
    if use_real_faces:
        person_dirs = sorted([d for d in faces_dir.iterdir() if d.is_dir()])
        real_face_paths = [str(person_dirs[i] / f"{j}.jpg") for i in range(len(person_dirs)) for j in range(2)]
        print(f"Using {len(person_dirs)} real face pairs from data/faces/")
    else:
        real_face_paths = []
        if not faces_dir.exists():
            print("data/faces/ not found, using synthetic embeddings")
        elif os.getenv("EMBEDDING_BACKEND", "synthetic").lower() != "insightface":
            print(f"EMBEDDING_BACKEND={os.getenv('EMBEDDING_BACKEND')}, using synthetic embeddings")

    print("Seeding planted cross-district matches...")
    # 1. Plant 15 pairs (30 cases total)
    for idx, item in enumerate(PLANTED_MATCHES_DATA):
        missing = item["missing"]
        found = item["found"]
        shared_person_key = f"planted_person_{idx}"

        # Use real faces if available; pair photo0 and photo1 from same LFW person
        if use_real_faces and idx < len(person_dirs):
            person_id = idx % len(person_dirs)
            photo0_path = str(faces_dir / f"{person_id:03d}" / "0.jpg")
            photo1_path = str(faces_dir / f"{person_id:03d}" / "1.jpg")
            missing_vec = load_real_face_embedding(photo0_path)
            found_vec = load_real_face_embedding(photo1_path)
            print(f"  Planted match {idx}: using real LFW person {person_id}")
        else:
            # Synthetic: base vector embedding with slight noise for realistic cosine similarity (~0.90)
            missing_vec = generate_synthetic_embedding(shared_person_key, noise_level=0.0)
            found_vec = generate_synthetic_embedding(shared_person_key, noise_level=0.15)

        # Dist coordinate offset
        m_base_lat, m_base_lng = DISTRICT_COORDS[missing["district"]]
        f_base_lat, f_base_lng = DISTRICT_COORDS[found["district"]]

        case_counter += 1
        m_case = Case(
            case_number=f"CAS-2026-M{case_counter}",
            type="MISSING",
            status="OPEN",
            name=missing["name"],
            devanagari_name=missing["devanagari"],
            aliases=[missing["name"].split()[0]],
            age=missing["age"],
            sex=missing["sex"],
            height_cm=missing["height"],
            marks=missing["marks"],
            clothing=missing["clothing"],
            language="Marathi",
            last_seen_found_place=f"Central Bus Stand, {missing['district']}",
            last_seen_found_time=now - datetime.timedelta(days=missing["days_ago"]),
            latitude=m_base_lat + random.uniform(-0.02, 0.02),
            longitude=m_base_lng + random.uniform(-0.02, 0.02),
            district=missing["district"],
            phone_numbers=[missing["phone"]],
            photo_url=f"https://picsum.photos/seed/{case_counter}/200/200",
            photo_embedding=missing_vec,
            created_at=now - datetime.timedelta(days=missing["days_ago"]),
            created_by_role="Station Officer",
            created_by_district=missing["district"],
        )
        db.add(m_case)

        case_counter += 1
        f_case = Case(
            case_number=f"CAS-2026-F{case_counter}",
            type="FOUND",
            status="OPEN",
            name=found["name"],
            devanagari_name=found["devanagari"],
            aliases=[],
            age=found["age"],
            sex=found["sex"],
            height_cm=found["height"],
            marks=found["marks"],
            clothing=found["clothing"],
            language="Marathi",
            last_seen_found_place=f"Railway Shelter, {found['district']}",
            last_seen_found_time=now - datetime.timedelta(days=found["days_ago"]),
            latitude=f_base_lat + random.uniform(-0.02, 0.02),
            longitude=f_base_lng + random.uniform(-0.02, 0.02),
            district=found["district"],
            phone_numbers=[found["phone"]],
            photo_url=f"https://picsum.photos/seed/{case_counter}/200/200",
            photo_embedding=found_vec,
            created_at=now - datetime.timedelta(days=found["days_ago"]),
            created_by_role="CWC Officer",
            created_by_district=found["district"],
        )
        db.add(f_case)

    db.commit()

    # 2. Seed ~170 distractor records (bringing total to ~200)
    print("Seeding ~170 distractor records...")
    districts = ["Pune", "Mumbai Suburban", "Thane", "Nagpur"]
    types = ["MISSING", "FOUND"]
    sexes = ["MALE", "FEMALE"]
    
    # Use remaining real faces for distractors if available
    real_face_idx = 15 if use_real_faces else 0  # Skip first 15 (used for planted matches)

    for i in range(170):
        case_counter += 1
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        c_type = random.choice(types)
        c_dist = random.choice(districts)
        base_lat, base_lng = DISTRICT_COORDS[c_dist]
        days_ago = random.randint(1, 60)
        c_phone = f"+91{random.randint(9000000000, 9999999999)}"
        c_name = f"{fn} {ln}"
        
        # Use real faces for distractors if available
        if use_real_faces and real_face_idx < len(person_dirs):
            person_id = real_face_idx % len(person_dirs)
            photo_idx = (real_face_idx // len(person_dirs)) % 2
            photo_path = str(faces_dir / f"{person_id:03d}" / f"{photo_idx}.jpg")
            vec = load_real_face_embedding(photo_path)
            real_face_idx += 1
        else:
            vec = generate_synthetic_embedding(f"distractor_{i}_{c_name}")

        case = Case(
            case_number=f"CAS-2026-R{case_counter}",
            type=c_type,
            status="OPEN",
            name=c_name,
            devanagari_name=None,
            aliases=[],
            age=random.randint(6, 50),
            sex=random.choice(sexes),
            height_cm=float(random.randint(120, 185)),
            marks=random.choice(MARKS_ITEMS),
            clothing=random.choice(CLOTHING_ITEMS),
            language=random.choice(LANGUAGES),
            last_seen_found_place=f"Market Yard, {c_dist}",
            last_seen_found_time=now - datetime.timedelta(days=days_ago),
            latitude=base_lat + random.uniform(-0.05, 0.05),
            longitude=base_lng + random.uniform(-0.05, 0.05),
            district=c_dist,
            phone_numbers=[c_phone],
            photo_url=f"https://picsum.photos/seed/{case_counter}/200/200",
            photo_embedding=vec,
            created_at=now - datetime.timedelta(days=days_ago),
            created_by_role="Station Officer",
            created_by_district=c_dist,
        )
        db.add(case)

    db.commit()

    # Log audit event for seeding
    audit = AuditLog(
        user_role="System",
        user_district="State HQ",
        action="SEED_DATASET",
        target_id="SYSTEM",
        details={"record_count": db.query(Case).count(), "planted_matches": len(PLANTED_MATCHES_DATA)},
    )
    db.add(audit)
    db.commit()

    total_cases = db.query(Case).count()
    print(f"Successfully seeded database with {total_cases} cases!")
    db.close()

if __name__ == "__main__":
    seed_db()
