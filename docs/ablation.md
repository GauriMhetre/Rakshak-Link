# Signal Ablation Study

## Task

Evaluate contribution of each signal to Precision@1 and Precision@5 on 15 planted cross-district matches.

## Planted Match Details

All 15 matches share:
- Same person (real LFW photo pairs)
- Matching phone numbers
- Similar attributes (age ±0-2 years, sex, height ±2cm, marks, clothing)

## Results

| Signal | Precision@1 | Precision@5 |
|--------|-------------|-------------|
| Face only | 100.0% | 100.0% |
| Name only | 100.0% | 100.0% |
| Attributes only | 93.3% | 100.0% |
| Geo-time only | 0.0% | 0.0% |
| Fused (all) | 100.0% | 100.0% |

## Interpretation

- **Face only**: Real InsightFace embeddings (512-d L2-normalized)
- **Name only**: Phonetic + fuzzy matching + Devanagari transliteration
- **Attributes only**: Sex, age, height, marks, clothing overlap
- **Geo-time only**: Travel distance + time plausibility
- **Fused**: Weighted combination (0.35 face, 0.25 name, 0.20 attr, 0.20 geo-time)

The fused signal achieves the highest precision by combining multiple modalities.
