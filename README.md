# Rakshak Link 🛡️

**Cross-District Missing Person & Anti-Trafficking Intelligence Portal**

Rakshak Link is an AI-powered intelligence portal built for Police Station Officers, Child Welfare Committees (CWC), and Investigating Officers (IO) to match missing person reports with found/rescued individuals across districts and detect interstate trafficking networks.

---

## Key Features

1. **Multi-Signal Matching Engine (`backend/app/services/matching.py`)**:
   - **Biometric Cosine Similarity**: Compares 128-dimensional face vector embeddings.
   - **Fuzzy & Phonetic Name Similarity**: Integrates RapidFuzz ratio/token algorithms, Jellyfish Metaphone, and Devanagari to Latin phonetic transliteration (`backend/app/services/transliteration.py`).
   - **Attribute Overlap**: Composite scoring across age difference, sex match, height variance, physical marks, and clothing description tokens.
   - **Geo-Time Plausibility**: Computes required travel speed between last-seen/found locations and times using Haversine distance.

2. **Privacy-Preserving Cross-District Data Sharing**:
   - Biometric vector embeddings and anonymized feature signatures cross district borders for automated scoring.
   - Raw photograph URLs are restricted to the originating district until a match link is officially verified by an Investigating Officer.

3. **Trafficking Syndicate Network Graph (`backend/app/services/graph_service.py`)**:
   - Graph visualization powered by Cytoscape.js & NetworkX mapping case nodes, phone numbers, and location hubs.
   - Automated detection of syndicates flagging clusters with 3+ cases sharing phone numbers or key transport hubs.

4. **District-Scoped Access & Audit Logging**:
   - Role-based authorization headers (`Station Officer`, `CWC Officer`, `Investigating Officer`).
   - Scoped database views and immutable audit log trace of all views, matches, and decisions.

---

## Technology Stack

- **Backend**: FastAPI, SQLite (SQLAlchemy 2.0), Pydantic v2
- **Data & Intelligence**: NumPy, RapidFuzz, Jellyfish, NetworkX
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Cytoscape.js
- **Testing**: pytest

---

## Quick Start & Installation

```bash
# 1. Install all backend (Python) and frontend (npm) dependencies
make install

# 2. Seed database (~200 synthetic records, 4 districts, 15 planted cross-district matches, 2 trafficking clusters)
make seed

# 3. Run application (Backend API on :8000 & Frontend Vite on :3000)
make run
```

### Running Test Suite
```bash
make test
```
*pytest asserts that 100% of planted cross-district test cases rank in top-5 candidate matches.*

---

## 🎬 2-Minute End-to-End Demo Script

Follow these steps to demonstrate the full intelligence workflow:

### Step 1: Switch Context to Pune Station Officer
- Select **Role**: `Station Officer` and **District**: `Pune` from the top header dropdown.

### Step 2: Register Missing Person Report in Pune
- Click **"File Intake Report"** tab.
- Submit a Missing Person report:
  - **Type**: `MISSING PERSON REPORT`
  - **Name**: `Ramesh Sharma` (Devanagari: `रमेश शर्मा`)
  - **Age**: `14`, **Sex**: `MALE`, **Height**: `152` cm
  - **Marks**: `Mole on right cheek`
  - **District**: `Pune`
  - **Location**: `Shivajinagar Bus Stand, Pune`
  - **Phone**: `+919820012345`
- Click **"Submit Intake & Search Cross-District Matches"**.

### Step 3: View Candidate Match Alert in Thane
- Switch **Role** to `Investigating Officer` or `Station Officer (Thane)`.
- Click **"Match Review"** tab.
- Observe candidate match identified with **Found Case in Thane** (`Ramesh Shrama`, Age 14, Height 154 cm, Found at Railway Shelter Thane, Phone `+919820012345`).
- Inspect the **Fused Score Breakdown** showing high Face similarity (~91%), Name phonetic match (~92%), Attribute overlap (~90%), and Geo-Time plausibility (~95%), along with the **Shared Phone Warning**.

### Step 4: Verify Match & Trigger Cross-District Alert
- Click **"Verify & Alert Districts"**.
- A joint alert is dispatched to both Pune & Thane Police Stations, changing both case statuses to `MATCHED` and making raw photo URLs accessible to both teams.

### Step 5: Detect Trafficking Syndicate Cluster
- Click **"Trafficking Graph"** tab.
- Observe **CRITICAL TRAFFICKING SYNDICATE ALERT (CLUSTER-01)** highlighting phone `+919820012345` linking 4 cases across Pune, Thane, and Nagpur.
- Click on the phone diamond node to inspect linked cases in the Graph Inspector.

---

## Limitations & Production Roadmap

1. **Embedding Extractor Interface**: The default extractor (`SyntheticEmbeddingExtractor`) uses deterministic feature hashing to generate 128-dimensional vector embeddings for demo reproducibility. In production, replace `SyntheticEmbeddingExtractor` in `backend/app/services/matching.py` with a deep learning vision pipeline (e.g., InsightFace / ArcFace ResNet50 model).
2. **Database Engine**: Current storage uses SQLite for zero-dependency execution; production deployment should utilize PostgreSQL with `pgvector` for indexing high-dimensional biometrics at scale.
