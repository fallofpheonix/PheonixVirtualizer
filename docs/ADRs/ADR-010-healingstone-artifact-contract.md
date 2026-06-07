---
adr-id: ADR-010
project: [[05_PROJECTS/ACTIVE/healingstone]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, architecture, contracts]
---
# ADR-010: Fixed artifact output contract for every healingstone run

## Context (reconstructed)
Fragment reconstruction runs need to produce consistent, comparable output. Researchers need to compare results across different parameter settings and datasets.

## Decision
Every pipeline run produces a fixed set of scoped artifacts: metrics.json, reconstruction.ply, alignment_metrics.json, similarity_matrix.png.

## Why This Was Chosen (reconstructed)
- Reproducibility: same inputs must produce the same artifact set
- Comparability: standardized output format enables automated comparison across runs
- Evidence from codebase: output/ directory with structured artifact generation

## Alternatives That Were Likely Considered
- **Ad-hoc output** — whatever the pipeline produces. No consistency guarantees.
- **Database-backed results** — more queryable but adds infrastructure complexity

## Consequences (observed)
Positive:
- Every run is self-documenting — artifacts tell you what happened
- Easy to diff results between runs
- Quality gate: if any artifact is missing, the run is invalid

Negative / trade-offs:
- Rigid schema — adding new output types requires updating the contract
- File-based output doesn't scale to thousands of runs (would need a results database)

## Would You Make This Decision Again?
Yes — the artifact contract is the best design decision in this project. Would formalize it even more with JSON Schema validation.
