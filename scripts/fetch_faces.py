#!/usr/bin/env python3
"""Fetch LFW faces and export to data/faces/<id>/{0,1}.jpg"""
import os
import numpy as np
from pathlib import Path
from PIL import Image
from sklearn.datasets import fetch_lfw_people

DATA_DIR = Path("data/faces")
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("Fetching LFW people (min_faces_per_person=2)...")
lfw = fetch_lfw_people(min_faces_per_person=2, download_if_missing=True, color=True)

# lfw is a Bunch with: images, target, data, target_names, DESCR
# Group images by person
people_images = {}
for img, person_id in zip(lfw.images, lfw.target):
    if person_id not in people_images:
        people_images[person_id] = []
    people_images[person_id].append(img)

# Export first 60 people, 2 photos each
people_exported = 0
for person_id in sorted(people_images.keys())[:60]:
    images = people_images[person_id]
    if len(images) < 2:
        continue

    person_dir = DATA_DIR / f"person_{person_id:03d}"
    person_dir.mkdir(parents=True, exist_ok=True)

    for photo_num in range(2):
        img_array = images[photo_num]
        img = Image.fromarray((img_array * 255).astype('uint8'))
        img.save(person_dir / f"{photo_num}.jpg")

    people_exported += 1

print(f"Exported {people_exported} people to {DATA_DIR}")

