# Face Matching Evaluation Report

## Dataset: LFW (Labeled Faces in the Wild)

- **People evaluated**: 60
- **Photo pairs**: 60 (2 per person)
- **Same-person pairs**: 60
- **Different-person pairs sampled**: 1525
- **Failed face detections**: 0

## Embedding Results (InsightFace buffalo_s, 512-dimensional)

| Metric | Value | Std Dev |
|--------|-------|---------|
| Mean same-person cosine similarity | 0.5295 | ±0.1134 |
| Mean different-person cosine similarity | 0.0179 | ±0.0742 |
| Threshold for ~1% FAR (99th percentile) | 0.1920 | — |

### Analysis

- **Same-person score 0.5295** indicates strong within-identity consistency.
- **Different-person score 0.0179** shows good separation from same-person class.
- **FAR threshold 0.1920** recommends accepting only matches above this threshold to keep false positive rate ≤1%.

### Interpretation Example

- If two face embeddings have cosine similarity ≥ 0.1920, the system should flag them as potential match.
- If cosine similarity < 0.1920, treat as non-match to minimize false alarms.

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
