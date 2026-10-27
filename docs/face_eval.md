# Face Embedding Evaluation

## Backend: INSIGHTFACE

### Results
- **Mean same-person cosine similarity**: 0.5621
- **Mean different-person cosine similarity**: 0.0166
- **Threshold for ~1% False Accept Rate (FAR=0.01)**: 0.1773
  - FAR at threshold: 0.0130
  - FRR at threshold: 0.0000
- **No-face images**: 0
- **Same-person pairs tested**: 60
- **Different-person pairs tested**: 230

### Conclusion
INSIGHTFACE embeddings successfully differentiate same vs. different people on LFW.
