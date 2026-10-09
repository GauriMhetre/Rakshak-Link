# Rakshak Link 🛡️

**Cross-District Missing Person & Anti-Trafficking Intelligence System**

Rakshak Link is an AI-powered intelligence portal designed for Police Station Officers, Investigating Officers, and Child Welfare Committees (CWC) to match missing person reports with found/rescued individuals across districts and detect interstate trafficking networks.

## Features
- **Multi-Signal Matching Engine**: Combines face vector embeddings cosine similarity, fuzzy/phonetic name matching with Devanagari transliteration, physical/clothing attribute overlap, and spatio-temporal (geo-time) plausibility scoring.
- **Privacy-Preserving Cross-District Alerts**: Only biometric vector embeddings and anonymized feature signatures cross district borders—raw photos remain district-restricted.
- **Trafficking Network Analysis**: Interactive graph visualization powered by NetworkX & Cytoscape.js detecting clusters sharing phone numbers or key locations.
- **Strict Scoped Audit Logging**: Scoped API authentication & immutable action trace.

## Quick Start

```bash
# Install dependencies
make install

# Seed dataset with ~200 synthetic records & 15 cross-district matches
make seed

# Run Backend & Frontend
make run
```

## Running Tests
```bash
make test
```
