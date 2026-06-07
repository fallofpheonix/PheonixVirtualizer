---
adr-id: 008-lamp-docker-reproducibility
project: [[05_PROJECTS/ACTIVE/lamp]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, docker,reproducibility]
---
# ADR-008-lamp-docker-reproducibility: Docker for environment reproducibility in LAMP

## Context (reconstructed)
LAMP depends on GDAL which has notoriously inconsistent behavior across platforms. macOS, Linux, and Windows all handle GDAL differently.

## Decision
Docker as the primary development and deployment environment.

## Why This Was Chosen (reconstructed)
GDAL installation and behavior varies significantly across platforms. Docker provides a known-good environment with exact library versions.

## Alternatives That Were Likely Considered
- **conda environments** — conda environments (partially solve the problem but conda-forge GDAL versions lag)
- **manual GDAL compilation** — manual GDAL compilation (fragile, platform-specific)

## Consequences (observed)
Positive:
- Cross-platform reproducibility for the GIS stack

Negative / trade-offs:
- Docker adds container overhead for local development. GDAL Docker images are large (~1GB+).

## Would You Make This Decision Again?
Yes — Docker is essential for GDAL-dependent projects.
