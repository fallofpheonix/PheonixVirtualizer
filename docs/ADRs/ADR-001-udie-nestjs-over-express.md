---
adr-id: ADR-001
project: [[05_PROJECTS/ACTIVE/udie]]
status: ACCEPTED (retroactive)
decision-date: 2026-02
documented-date: 2026-05-12
tags: [adr, retroactive, backend, typescript]
---

# ADR-001: NestJS over Express or Fastify for UDIE backend

## Context (reconstructed)
UDIE needed a TypeScript backend framework to handle complex module organization (ingestion, risk, forecast, digital-twin, routing, traffic-control, metrics), dependency injection, and structured middleware. The project was building a multi-module monolith that would later need clean boundaries for potential microservice extraction.

## Decision
NestJS was chosen as the primary backend framework, running on Node.js with TypeScript.

## Why This Was Chosen (reconstructed)
- NestJS provides built-in module system with dependency injection — critical for a system with 7+ domain modules
- Decorator-based architecture maps naturally to the domain-driven design of UDIE modules
- Built-in support for WebSockets, GraphQL, and microservice transport layers
- TypeScript-first (not bolted on) — matches the project's type-safety requirements
- The codebase structure (src/modules/, src/platform/) directly mirrors NestJS module conventions

## Alternatives That Were Likely Considered
- **Express.js** — too minimal, would require manual DI container and module system. For a 7-module system, this becomes a framework-building exercise.
- **Fastify** — faster raw performance, but lacks NestJS's module/DI system. Would need manual architecture scaffolding.
- **Python (FastAPI)** — used for spatial utilities but not the main backend. TypeScript was preferred for the primary service to match the mobile client ecosystem.

## Consequences (observed)
Positive:
- Clean module boundaries visible in folder structure
- Easy to add new domain modules without architectural refactoring
- Middleware and guards integrated naturally for auth and validation

Negative / trade-offs:
- NestJS has higher learning curve than Express
- Decorator-heavy code can obscure control flow
- The "dual backend surface" audit defect may be partly caused by NestJS making it too easy to create additional entry points

## Would You Make This Decision Again?
Yes — for a system of this complexity, the module system pays for itself. The alternative was building a custom module system on top of Express, which is just NestJS with extra steps.
