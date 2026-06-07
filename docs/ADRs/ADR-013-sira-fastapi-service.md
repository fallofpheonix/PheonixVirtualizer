---
adr-id: ADR-013
project: [[05_PROJECTS/ACTIVE/sira]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, backend, api]
---
# ADR-013: FastAPI over Flask/Django for sira inference service

## Context (reconstructed)
The trained MLP model needed to be served via HTTP for real-time epidemic parameter inference. The API surface is simple (model inference endpoint + health check), so a lightweight framework was needed.

## Decision
FastAPI + Uvicorn for the inference service.

## Why This Was Chosen (reconstructed)
- FastAPI's async support matches the inference use case (I/O-bound model loading, CPU-bound inference)
- Automatic OpenAPI docs from Pydantic models — no separate API documentation needed
- Already used in 7 other repos in the portfolio — established pattern

## Alternatives That Were Likely Considered
- **Flask** — synchronous by default, no built-in validation, no auto-docs
- **Django** — too heavy for a single-endpoint inference service
- **gRPC** — better for service-to-service, but this is a user-facing HTTP API

## Consequences (observed)
Positive:
- Clean, minimal API surface
- Auto-generated docs at /docs
- Pydantic validation catches bad input before model inference

Negative / trade-offs:
- FastAPI startup time includes model loading — cold starts are slow
- No authentication or rate limiting configured

## Would You Make This Decision Again?
Yes — FastAPI is the correct choice for Python ML inference services.
