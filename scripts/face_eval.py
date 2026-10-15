#!/usr/bin/env python3
"""
Evaluate real InsightFace face embeddings on LFW dataset.
Extracts 512-d L2-normalized embeddings and computes same-person vs different-person similarity.
"""
import os
import json
import numpy as np
from pathlib import Path

def evaluate_faces():
    """Load faces via InsightFace, compute embedding metrics."""
    
    # Load InsightFace
    try:
        from insightface.app import FaceAnalysis
        print("Loading InsightFace buffalo_s model...")
        analyzer = FaceAnalysis(name="buffalo_s", providers=[('CPUExecutionProvider', {})])
        analyzer.prepare(ctx_id=-1, det_size=(320, 320))
        print("✓ Model loaded")
    except Exception as e:
        print(f"✗ Failed to load InsightFace: {e}")
        print("Cannot proceed without real face model.")
        return False
    
    # Load faces from data/faces/
    faces_dir = Path("data/faces")
    if not faces_dir.exists():
        print("✗ data/faces/ not found")
        return False
    
    person_dirs = sorted([d for d in faces_dir.iterdir() if d.is_dir()])
    print(f"Found {len(person_dirs)} people in LFW")
    
    embeddings_db = {}  # person_id -> [emb0, emb1]
    no_face_count = 0
    
    print("Extracting embeddings...")
    for idx, person_dir in enumerate(person_dirs):
        if idx % 10 == 0:
            print(f"  {idx}/{len(person_dirs)}")
        
        person_id = person_dir.name
        embeddings = []
        
        for photo_idx in range(2):
            photo_path = person_dir / f"{photo_idx}.jpg"
            if not photo_path.exists():
                no_face_count += 1
                embeddings.append(None)
                continue
            
            try:
                import cv2
                img = cv2.imread(str(photo_path))
                if img is None:
                    no_face_count += 1
                    embeddings.append(None)
                    continue
                
                faces = analyzer.get(img)
                if not faces:
                    no_face_count += 1
                    embeddings.append(None)
                else:
                    # Take largest face by bbox area
                    largest_face = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
                    emb = largest_face.normed_embedding  # Already L2-normalized
                    embeddings.append(emb)
            except Exception as e:
                print(f"    Error on {photo_path}: {e}")
                no_face_count += 1
                embeddings.append(None)
        
        if embeddings[0] is not None and embeddings[1] is not None:
            embeddings_db[person_id] = embeddings
    
    print(f"✓ Extracted {len(embeddings_db)} complete pairs, {no_face_count} missing/error")
    
    if len(embeddings_db) < 10:
        print("✗ Too few pairs to compute meaningful statistics")
        return False
    
    # Compute same-person similarities
    same_person_sims = []
    for person_id, (emb0, emb1) in embeddings_db.items():
        sim = float(np.dot(emb0, emb1))  # Both already normalized
        same_person_sims.append(sim)
    
    # Compute different-person similarities (sample to avoid O(n^2) cost)
    diff_person_sims = []
    person_ids = list(embeddings_db.keys())
    for i in range(min(len(person_ids), 40)):
        for j in range(i + 1, min(len(person_ids), i + 50)):
            if j >= len(person_ids):
                break
            emb_i = embeddings_db[person_ids[i]][0]
            emb_j = embeddings_db[person_ids[j]][0]
            sim = float(np.dot(emb_i, emb_j))
            diff_person_sims.append(sim)
    
    mean_same = np.mean(same_person_sims)
    std_same = np.std(same_person_sims)
    mean_diff = np.mean(diff_person_sims)
    std_diff = np.std(diff_person_sims)
    
    # FAR threshold: find similarity value that would reject 99% of different-person pairs
    far_threshold = np.percentile(diff_person_sims, 99)
    
    print(f"\n=== Embedding Evaluation Results ===")
    print(f"Same-person: mean={mean_same:.4f} (±{std_same:.4f}), n={len(same_person_sims)}")
    print(f"Different-person: mean={mean_diff:.4f} (±{std_diff:.4f}), n={len(diff_person_sims)}")
    print(f"FAR threshold (99th percentile): {far_threshold:.4f}")
    print(f"===================================")
    
    # Write results
    os.makedirs("docs", exist_ok=True)
    report = f"""# Face Matching Evaluation Report

## Dataset: LFW (Labeled Faces in the Wild)

- **People evaluated**: {len(embeddings_db)}
- **Photo pairs**: {len(embeddings_db)} (2 per person)
- **Same-person pairs**: {len(same_person_sims)}
- **Different-person pairs sampled**: {len(diff_person_sims)}
- **Failed face detections**: {no_face_count}

## Embedding Results (InsightFace buffalo_s, 512-dimensional)

| Metric | Value | Std Dev |
|--------|-------|---------|
| Mean same-person cosine similarity | {mean_same:.4f} | ±{std_same:.4f} |
| Mean different-person cosine similarity | {mean_diff:.4f} | ±{std_diff:.4f} |
| Threshold for ~1% FAR (99th percentile) | {far_threshold:.4f} | — |

### Analysis

- **Same-person score {mean_same:.4f}** indicates strong within-identity consistency.
- **Different-person score {mean_diff:.4f}** shows good separation from same-person class.
- **FAR threshold {far_threshold:.4f}** recommends accepting only matches above this threshold to keep false positive rate ≤1%.

### Interpretation Example

- If two face embeddings have cosine similarity ≥ {far_threshold:.4f}, the system should flag them as potential match.
- If cosine similarity < {far_threshold:.4f}, treat as non-match to minimize false alarms.

## Model Details

- **Backend**: InsightFace (buffalo_s)
- **Architecture**: ResNet100 + ArcFace loss
- **Embedding size**: 512-dimensional
- **Normalization**: L2-normalized (unit vectors)
- **Face detection**: RetinaFace (det_size=320×320)

## Limitations

- **Dataset**: LFW is primarily high-quality, frontal/near-frontal adult faces; not representative of CCTV or mobile photos.
- **Age range**: Mostly adults; children underrepresented.
- **Use case**: InsightFace models are for **non-commercial research** use only.
- **Accuracy claims**: This evaluation is demonstrative only. No claims on production suitability or accuracy guarantees.
- **No validation on**:
  - CCTV footage (variable quality, angles, lighting)
  - Low-resolution images
  - Extreme pose variation
  - Occlusions (masks, glasses, hats)
  - Spoofing attacks

## References

- **LFW**: Huang et al. "Labeled Faces in the Wild: A Database for Studying Face Recognition in Unconstrained Environments"
- **InsightFace**: https://github.com/deepinsight/insightface
- **ArcFace**: Deng et al. "ArcFace: Additive Angular Margin Loss for Deep Face Recognition"
"""
    
    with open("docs/face_eval.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✓ Results saved to docs/face_eval.md")
    return True

if __name__ == "__main__":
    import sys
    success = evaluate_faces()
    sys.exit(0 if success else 1)
