# LFW Identification Benchmark

## Task

For each of 60 LFW people:
- Query: person's photo 0 embedding
- Gallery: 60 embeddings (all photo 1s)
- Task: rank gallery by cosine similarity to query

## Results

| Metric | Accuracy | Gallery Size |
|--------|----------|--------------|
| Rank-1 | 100.00% (60/60) | 60 |
| Rank-5 | 100.00% (60/60) | 60 |

## Interpretation

- **Rank-1**: Top match is correct 100.0% of the time.
- **Rank-5**: Correct person in top-5 matches 100.0% of the time.
- **Gallery**: 60 embeddings from LFW (one per person).

## Notes

- Query and gallery are independent photos from same people.
- InsightFace buffalo_s model (512-d L2-normalized embeddings).
- High accuracy shows strong generalization across photos.
