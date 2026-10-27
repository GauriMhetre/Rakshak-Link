"""
InsightFace-backed face embedding extractor.
Lazy singleton model loading.
"""
import numpy as np
from typing import List, Optional
from ..services.matching import EmbeddingExtractorInterface

EMBEDDING_DIM = 512

class InsightFaceExtractor(EmbeddingExtractorInterface):
    """Extract face embeddings using InsightFace buffalo_s model."""
    
    _instance = None
    _analyzer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_model(self):
        """Lazy-load InsightFace model on first call."""
        if self._analyzer is None:
            try:
                from insightface.app import FaceAnalysis
                self._analyzer = FaceAnalysis(name="buffalo_s", providers=[('CPUExecutionProvider', {})])
                self._analyzer.prepare(ctx_id=-1, det_size=(320, 320))
            except Exception as e:
                raise RuntimeError(f"Failed to load InsightFace model: {e}")
    
    def extract_embedding(self, input_data: str) -> Optional[List[float]]:
        """
        Extract face embedding from image path or return None if no face detected.
        
        Args:
            input_data: Path to image file
        
        Returns:
            L2-normalized 512-d embedding, or None if no face detected
        """
        self._load_model()
        
        try:
            import cv2
            img = cv2.imread(input_data)
            if img is None:
                return None
            
            faces = self._analyzer.get(img)
            if not faces:
                return None
            
            # Take largest face
            largest_face = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
            emb = largest_face.normed_embedding  # Already L2-normalized
            
            # Ensure it's exactly 512-d
            if len(emb) != EMBEDDING_DIM:
                raise ValueError(f"Expected embedding dim {EMBEDDING_DIM}, got {len(emb)}")
            
            return emb.tolist()
        except Exception as e:
            raise RuntimeError(f"Failed to extract embedding from {input_data}: {e}")
