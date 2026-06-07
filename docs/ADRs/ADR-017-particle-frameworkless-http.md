---
adr-id: ADR-017
project: [[05_PROJECTS/ACTIVE/particle-stimulator]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, backend, api]
---
# ADR-017: Frameworkless HTTP server instead of FastAPI for ParticleStimulator

## Context (reconstructed)
ParticleStimulator needs HTTP endpoints for health checks, simulation triggers, ML training, and prediction. Rather than using FastAPI (the standard choice across the portfolio), a frameworkless HTTP approach was used.

## Decision
Custom frameworkless HTTP server using Python's built-in http.server or aiohttp without a full framework.

## Why This Was Chosen (reconstructed)
- Rationale unknown — decision predates documentation. Possibly chosen for minimal dependencies or because the WebSocket server was already custom.
- The simulation server was likely built before FastAPI became the portfolio standard.

## Alternatives That Were Likely Considered
- **FastAPI** — the standard choice across 7 other repos. Would have provided auto-docs, validation, and middleware.
- **Flask** — lightweight but synchronous, which conflicts with WebSocket needs
- **Starlette** — FastAPI's foundation, lighter weight

## Consequences (observed)
Positive:
- Zero framework dependencies
- Full control over request handling

Negative / trade-offs:
- No request validation (Pydantic)
- No auto-generated API docs
- No middleware stack (auth, logging, error handling)
- May limit scalability (audit defect)
- Diverges from portfolio-wide FastAPI pattern

## Would You Make This Decision Again?
No — would use FastAPI. The frameworkless approach creates technical debt and diverges from the portfolio standard. This is a refactor target.
