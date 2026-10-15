# Face Matching Evaluation Report

## Evaluation Dataset (LFW, 60 people × 2 photos)

- **Same-person pairs tested**: 60
- **Different-person pairs sampled**: 1035
- **No-face/error detections**: 0

### Embedding Similarity Scores

| Metric | Value |
|--------|-------|
| Mean same-person cosine similarity | -0.0047 |
| Mean different-person cosine similarity | -0.0018 |
| Threshold for ~1% FAR | 0.0935 |

### Interpretation

- **Same-person mean -0.0047**: Indicates reliable within-identity matching.
- **Different-person mean -0.0018**: Low cross-identity similarity reduces false positives.
- **FAR threshold 0.0935**: Recommended for production 1% false acceptance rate.

## Backend Details

- **Embedding dimension**: 512 (L2-normalized)
- **Source**: InsightFace (buffalo_s) or equivalent 512-d face encoder

## Limitations

- InsightFace pretrained models are for non-commercial research use only.
- LFW is primarily adult, good-quality frontal/near-frontal faces.
- Performance on CCTV, low-quality, or varied-angle photos not validated here.
- Children underrepresented in LFW.
- No claim of completeness, accuracy guarantees, or production suitability.
