#!/usr/bin/env python3
"""
Fetch LFW faces and export 2 photos per person for 60 people.
"""
import os
import json
from sklearn.datasets import fetch_lfw_people
from PIL import Image

def fetch_and_export_faces():
    print("Fetching LFW dataset (min_faces_per_person=2)...")
    lfw = fetch_lfw_people(min_faces_per_person=2)
    
    target_names = lfw.target_names
    targets = lfw.target
    data = lfw.images  # shape: (n_samples, h, w)
    
    # Group by person
    person_photos = {}
    for idx, person_id in enumerate(targets):
        person_name = target_names[person_id]
        if person_name not in person_photos:
            person_photos[person_name] = []
        person_photos[person_name].append(data[idx])
    
    # Select first 60 people with at least 2 photos each
    selected_people = [(name, photos) for name, photos in person_photos.items() 
                       if len(photos) >= 2][:60]
    
    os.makedirs("data/faces", exist_ok=True)
    
    exported_count = 0
    for person_id, (person_name, photos) in enumerate(selected_people):
        person_dir = f"data/faces/{person_id:03d}"
        os.makedirs(person_dir, exist_ok=True)
        
        # Export first 2 photos
        for photo_idx in range(2):
            photo_data = photos[photo_idx]
            img = Image.fromarray((photo_data * 255).astype('uint8'))
            img.save(f"{person_dir}/{photo_idx}.jpg")
        
        exported_count += 1
    
    print(f"Exported {exported_count} people × 2 photos to data/faces/")
    
    # Save metadata
    metadata = {
        "person_count": exported_count,
        "photos_per_person": 2,
        "source": "LFW via sklearn",
    }
    with open("docs/face_eval_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to docs/face_eval_metadata.json")

if __name__ == "__main__":
    fetch_and_export_faces()
