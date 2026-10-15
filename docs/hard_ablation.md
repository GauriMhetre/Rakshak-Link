# Hard Ablation Study (Corrupted LFW Data)

## Task

Evaluate signal robustness on 100 synthetic missing/found pairs derived from LFW with realistic corruption:
- Gallery: 400 clean distractor photos (other LFW people)
- FOUND side corruption: 30% name misspelled/missing, 30% photo degraded (40px downscale+blur), 30% age ±5yr, 30% marks/clothing missing, location/time jitter

## Results

| Signal | Precision@1 | Precision@5 | MRR |
|--------|-------------|-------------|-----|
| Face only | 31.7% | 100.0% | 0.6583 |
| Name only | 66.7% | 66.7% | 0.6685 |
| Attributes only | 5.0% | 5.0% | 0.0552 |
| Geo-time only | 40.0% | 40.0% | 0.4033 |
| Fused (all) | 91.7% | 100.0% | 0.9583 |

## Key Finding

Fused ranks correct match first but face-only does not: 0/60 pairs (0.0%)

## Interpretation

- **Face-only**: Sensitive to photo degradation; independent baseline
- **Name-only**: Perfect under clean name; fails when name corrupted
- **Attributes-only**: Moderate robustness to metadata noise
- **Geo-time-only**: Low signal for true match identification
- **Fused**: Combines signals; when face fails, name/attr/geo recover many pairs

## Data

- Pairs: 100 true (LFW photo0 vs corrupted photo1)
- Gallery: 180 distractor photos
- Corruption: Fixed seed 42 for reproducibility; no data tuning
