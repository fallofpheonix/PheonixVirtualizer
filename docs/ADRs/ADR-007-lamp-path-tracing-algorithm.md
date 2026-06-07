---
adr-id: 007-lamp-path-tracing-algorithm
project: [[05_PROJECTS/ACTIVE/lamp]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, algorithms,path-tracing]
---
# ADR-007-lamp-path-tracing-algorithm: Probabilistic path tracing algorithm selection for LAMP

## Context (reconstructed)
LAMP models ancient movement across terrain using slope, roughness, surface penalty, path priors, and visibility coupling. The algorithm must produce reproducible cost surfaces.

## Decision
Custom probabilistic path tracer with configurable cost factors and optional visibility coupling from viewshed output.

## Why This Was Chosen (reconstructed)
Multiple cost factors (slope, roughness, visibility) need to combine into a single movement cost. The coupling contract (viewshed_probability.tif feeds into path cost) requires a custom implementation.

## Alternatives That Were Likely Considered
- **A* or Dijkstra on a grid** — A* or Dijkstra on a grid (standard but doesn't support probabilistic cost combination)
- **Least-cost path analysis** — Least-cost path analysis (GIS standard but too simplistic for multi-factor coupling)

## Consequences (observed)
Positive:
- Flexible multi-factor cost surfaces, coupling contract between Task 1 and Task 2

Negative / trade-offs:
- Custom algorithm requires more testing than standard GIS tools. Reproducibility depends on floating-point determinism.

## Would You Make This Decision Again?
Yes — the coupling between viewshed and path tracing is the key research contribution.
