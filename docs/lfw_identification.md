# LFW Identification Benchmark

## Task

For each of 60 LFW people:
- Query: person's photo 0 embedding
- Gallery: all 60 people's photo 1 embeddings
- Task: rank all 60 gallery embeddings by cosine similarity to query

## Results

| Metric | Accuracy |
|--------|----------|
| Rank-1 | 100.00% (60/60) |
| Rank-5 | 100.00% (60/60) |

## Interpretation

- **Rank-1**: Top match is the correct person 100.0% of the time.
- **Rank-5**: Correct person is in top-5 matches 100.0% of the time.

## Notes

- Gallery contains one embedding per person (photo 1).
- Query embeddings are independent photos (photo 0) from same people.
- InsightFace buffalo_s model (512-d L2-normalized embeddings).
