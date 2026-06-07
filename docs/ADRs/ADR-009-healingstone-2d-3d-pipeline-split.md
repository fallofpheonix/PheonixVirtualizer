---
adr-id: ADR-009
project: [[05_PROJECTS/ACTIVE/healingstone]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, architecture, 3d-reconstruction]
---
# ADR-009: Separate 2D and 3D fragment reconstruction pipelines

## Context (reconstructed)
Healingstone handles two fragment types: 2D image fragments and 3D mesh fragments (.ply). Each requires different descriptor extraction, matching, and reconstruction algorithms. The question was whether to build a unified pipeline or separate ones.

## Decision
Built as two separate pipelines (pipeline_2d/ and pipeline_3d/) sharing a common core/ for descriptor matching.

## Why This Was Chosen (reconstructed)
- 2D and 3D fragments have fundamentally different data representations (pixel arrays vs mesh vertices)
- Descriptor extraction is different (visual features vs geometric features like curvature, normals)
- Faster to build separately and unify later than to abstract prematurely

## Alternatives That Were Likely Considered
- **Unified pipeline with mode parameter** — cleaner interface but requires upfront abstraction of descriptor extraction
- **Plugin architecture** — 2D/3D as plugins. Over-engineered for two modes.

## Consequences (observed)
Positive:
- Each pipeline can evolve independently
- Clear separation of 2D vs 3D concerns

Negative / trade-offs:
- Duplicated schema/core modules between pipelines (audit defect)
- Maintenance burden of keeping two pipelines in sync

## Would You Make This Decision Again?
No — would build the unified interface from the start. The duplication is now technical debt that must be resolved.
