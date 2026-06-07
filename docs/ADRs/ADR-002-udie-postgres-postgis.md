---
adr-id: ADR-002
project: [[05_PROJECTS/ACTIVE/udie]]
status: ACCEPTED (retroactive)
decision-date: 2026-02
documented-date: 2026-05-12
tags: [adr, retroactive, database, spatial]
---
# ADR-002: PostgreSQL + PostGIS over alternatives for UDIE

## Context (reconstructed)
UDIE processes geospatial urban disruption signals that need spatial queries (proximity, containment, intersection), H3 hexagonal indexing, and event-sourced persistence. The database must handle both relational data (users, configs, alerts) and spatial data (risk cells, hotspots, disruption signals) in a single authoritative store.

## Decision
PostgreSQL 14+ with PostGIS extension, running in Docker.

## Why This Was Chosen (reconstructed)
- PostGIS provides native spatial indexing, geometry types, and spatial queries — eliminates the need for a separate spatial engine
- PostgreSQL handles the relational+event-sourced persistence model (append-only event log + materialized projections)
- H3 spatial indexing integrates cleanly via PostgreSQL extensions
- Strong ACID guarantees for the authoritative event log

## Alternatives That Were Likely Considered
- **MongoDB** — good for flexible schemas but weak spatial query performance at scale, no ACID for event sourcing
- **TimescaleDB** — better for pure time-series but UDIE needs spatial+temporal, not just temporal
- **DynamoDB** — no spatial queries, vendor lock-in

## Consequences (observed)
Positive:
- Single database handles both relational and spatial needs
- Event sourcing works naturally with PostgreSQL's append-only patterns
- Docker deployment is straightforward

Negative / trade-offs:
- Migration sprawl — too many migrations accumulated (audit defect)
- PostGIS adds significant container size
- Spatial queries can be expensive without careful index design

## Would You Make This Decision Again?
Yes — PostgreSQL + PostGIS is the correct choice for a spatial intelligence system. The migration sprawl is a process problem, not a technology problem.
