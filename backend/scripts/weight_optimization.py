#!/usr/bin/env python3
"""
Weight optimization script using sklearn GridSearchCV.
Finds optimal weights (face, name, attr, geotime) to maximize Precision@5 on planted matches.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import Case, MatchLink, Feedback
from app.services.matching import evaluate_match_score
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np
import json

class MatchWeightTuner(BaseEstimator, ClassifierMixin):
    """Sklearn-compatible wrapper for weight tuning."""
    def __init__(self, face_weight=0.35, name_weight=0.25, attr_weight=0.20, geotime_weight=0.20):
        self.face_weight = face_weight
        self.name_weight = name_weight
        self.attr_weight = attr_weight
        self.geotime_weight = geotime_weight

    def fit(self, X, y):
        return self

    def score(self, X, y):
        """Score based on Precision@5 on planted matches."""
        scores = []
        for case1_dict, case2_dict, is_match in X:
            res = evaluate_match_score(
                case1_dict, case2_dict,
                face_weight=self.face_weight,
                name_weight=self.name_weight,
                attr_weight=self.attr_weight,
                geotime_weight=self.geotime_weight
            )
            scores.append((res["total_score"], is_match))

        scores.sort(reverse=True, key=lambda x: x[0])
        top5 = scores[:5]
        correct = sum(1 for _, is_match in top5 if is_match)
        precision_at_5 = correct / len(top5) if top5 else 0
        return precision_at_5

    def get_params(self, deep=True):
        return {
            'face_weight': self.face_weight,
            'name_weight': self.name_weight,
            'attr_weight': self.attr_weight,
            'geotime_weight': self.geotime_weight
        }

    def set_params(self, **params):
        for key, value in params.items():
            setattr(self, key, value)
        return self


def fetch_planted_matches():
    """Fetch planted matches (verified=True) with both case records."""
    db = SessionLocal()
    try:
        verified_links = db.query(MatchLink).filter(MatchLink.status == 'VERIFIED').all()
        
        X = []
        y = []
        
        for link in verified_links:
            source = db.query(Case).filter(Case.id == link.source_case_id).first()
            target = db.query(Case).filter(Case.id == link.target_case_id).first()
            
            if source and target:
                case1_dict = {
                    "id": source.id, "name": source.name, "devanagari_name": source.devanagari_name,
                    "age": source.age, "sex": source.sex, "height_cm": source.height_cm,
                    "marks": source.marks, "clothing": source.clothing,
                    "latitude": source.latitude, "longitude": source.longitude,
                    "last_seen_found_time": source.last_seen_found_time,
                    "phone_numbers": source.phone_numbers, "photo_embedding": source.photo_embedding,
                }
                case2_dict = {
                    "id": target.id, "name": target.name, "devanagari_name": target.devanagari_name,
                    "age": target.age, "sex": target.sex, "height_cm": target.height_cm,
                    "marks": target.marks, "clothing": target.clothing,
                    "latitude": target.latitude, "longitude": target.longitude,
                    "last_seen_found_time": target.last_seen_found_time,
                    "phone_numbers": target.phone_numbers, "photo_embedding": target.photo_embedding,
                }
                X.append((case1_dict, case2_dict, True))
                y.append(1)
        
        # Add negative samples (rejected matches)
        rejected_links = db.query(MatchLink).filter(MatchLink.status == 'REJECTED').all()
        for link in rejected_links[:len(verified_links)]:  # balance dataset
            source = db.query(Case).filter(Case.id == link.source_case_id).first()
            target = db.query(Case).filter(Case.id == link.target_case_id).first()
            if source and target:
                case1_dict = {
                    "id": source.id, "name": source.name, "devanagari_name": source.devanagari_name,
                    "age": source.age, "sex": source.sex, "height_cm": source.height_cm,
                    "marks": source.marks, "clothing": source.clothing,
                    "latitude": source.latitude, "longitude": source.longitude,
                    "last_seen_found_time": source.last_seen_found_time,
                    "phone_numbers": source.phone_numbers, "photo_embedding": source.photo_embedding,
                }
                case2_dict = {
                    "id": target.id, "name": target.name, "devanagari_name": target.devanagari_name,
                    "age": target.age, "sex": target.sex, "height_cm": target.height_cm,
                    "marks": target.marks, "clothing": target.clothing,
                    "latitude": target.latitude, "longitude": target.longitude,
                    "last_seen_found_time": target.last_seen_found_time,
                    "phone_numbers": target.phone_numbers, "photo_embedding": target.photo_embedding,
                }
                X.append((case1_dict, case2_dict, False))
                y.append(0)
        
        return X, np.array(y)
    finally:
        db.close()


def optimize_weights():
    """Run grid search optimization."""
    print("Fetching planted matches...")
    X, y = fetch_planted_matches()
    
    if len(X) == 0:
        print("No planted matches found. Using default weights.")
        return {"face": 0.35, "name": 0.25, "attr": 0.20, "geotime": 0.20}
    
    print(f"Dataset: {len(X)} samples ({sum(y)} positive)")
    
    param_grid = {
        'face_weight': [0.25, 0.30, 0.35, 0.40, 0.45],
        'name_weight': [0.15, 0.20, 0.25, 0.30],
        'attr_weight': [0.15, 0.20, 0.25],
        'geotime_weight': [0.15, 0.20, 0.25],
    }
    
    tuner = MatchWeightTuner()
    grid = GridSearchCV(tuner, param_grid, cv=3, scoring='precision', n_jobs=-1, verbose=1)
    
    print("Running grid search optimization...")
    grid.fit(X, y)
    
    best_params = grid.best_params_
    best_score = grid.best_score_
    
    print(f"\nBest Precision@5: {best_score:.4f}")
    print(f"Optimal weights: {best_params}")
    
    return {
        "face": float(best_params.get('face_weight', 0.35)),
        "name": float(best_params.get('name_weight', 0.25)),
        "attr": float(best_params.get('attr_weight', 0.20)),
        "geotime": float(best_params.get('geotime_weight', 0.20))
    }


if __name__ == '__main__':
    weights = optimize_weights()
    print(json.dumps(weights, indent=2))
