#!/usr/bin/env python3
"""
LFW Identification: for each of 60 people, query=photo0, gallery=all 60 photo1s.
Report rank-1 and rank-5 accuracy.
"""
import os
import numpy as np
from pathlib import Path

def rank_accuracy():
    """Compute rank-1 and rank-5 identification accuracy on LFW."""
    
    from insightface.app import FaceAnalysis
    print("Loading InsightFace buffalo_s model...")
    analyzer = FaceAnalysis(name="buffalo_s", providers=[('CPUExecutionProvider', {})])
    analyzer.prepare(ctx_id=-1, det_size=(320, 320))
    print("✓ Model loaded")
    
    faces_dir = Path("data/faces")
    person_dirs = sorted([d for d in faces_dir.iterdir() if d.is_dir()])
    print(f"Found {len(person_dirs)} people")
    
    # Extract all photo0 (queries) and photo1 (gallery)
    queries = {}  # person_id -> embedding
    gallery = {}  # person_id -> embedding
    
    print("Extracting embeddings...")
    for idx, person_dir in enumerate(person_dirs):
        if idx % 10 == 0:
            print(f"  {idx}/{len(person_dirs)}")
        
        person_id = person_dir.name
        
        for photo_idx, store_dict in [(0, queries), (1, gallery)]:
            photo_path = person_dir / f"{photo_idx}.jpg"
            try:
                import cv2
                img = cv2.imread(str(photo_path))
                if img is None:
                    print(f"    Error reading {photo_path}")
                    continue
                
                faces = analyzer.get(img)
                if not faces:
                    print(f"    No face in {photo_path}")
                    continue
                
                largest_face = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
                emb = largest_face.normed_embedding
                store_dict[person_id] = emb
            except Exception as e:
                print(f"    Error {photo_path}: {e}")
    
    print(f"✓ Extracted {len(queries)} queries, {len(gallery)} gallery embeddings")
    
    # Rank identification: for each query, compute distances to all gallery
    rank1_correct = 0
    rank5_correct = 0
    total = 0
    
    print("Computing rank-1 and rank-5 accuracy...")
    for person_id in sorted(queries.keys()):
        query_emb = queries[person_id]
        
        # Compute distances to all gallery embeddings
        distances = []
        for gal_person_id in sorted(gallery.keys()):
            gal_emb = gallery[gal_person_id]
            # Cosine distance = 1 - cosine_similarity
            sim = np.dot(query_emb, gal_emb)
            dist = 1.0 - sim
            distances.append((dist, gal_person_id))
        
        # Sort by distance (ascending; smallest is closest)
        distances.sort(key=lambda x: x[0])
        
        # Check rank-1
        if distances[0][1] == person_id:
            rank1_correct += 1
        
        # Check rank-5
        top5_ids = [d[1] for d in distances[:5]]
        if person_id in top5_ids:
            rank5_correct += 1
        
        total += 1
    
    rank1_acc = rank1_correct / total
    rank5_acc = rank5_correct / total
    
    print(f"\n=== LFW Identification Results ===")
    print(f"Rank-1 accuracy: {rank1_acc * 100:.2f}% ({rank1_correct}/{total})")
    print(f"Rank-5 accuracy: {rank5_acc * 100:.2f}% ({rank5_correct}/{total})")
    print(f"==================================")
    
    # Write report
    os.makedirs("docs", exist_ok=True)
    report = f"""# LFW Identification Benchmark

## Task

For each of 60 LFW people:
- Query: person's photo 0 embedding
- Gallery: all 60 people's photo 1 embeddings
- Task: rank all 60 gallery embeddings by cosine similarity to query

## Results

| Metric | Accuracy |
|--------|----------|
| Rank-1 | {rank1_acc * 100:.2f}% ({rank1_correct}/{total}) |
| Rank-5 | {rank5_acc * 100:.2f}% ({rank5_correct}/{total}) |

## Interpretation

- **Rank-1**: Top match is the correct person {rank1_acc * 100:.1f}% of the time.
- **Rank-5**: Correct person is in top-5 matches {rank5_acc * 100:.1f}% of the time.

## Notes

- Gallery contains one embedding per person (photo 1).
- Query embeddings are independent photos (photo 0) from same people.
- InsightFace buffalo_s model (512-d L2-normalized embeddings).
"""
    
    with open("docs/lfw_identification.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✓ Results saved to docs/lfw_identification.md")
    
    return True

if __name__ == "__main__":
    import sys
    success = rank_accuracy()
    sys.exit(0 if success else 1)
