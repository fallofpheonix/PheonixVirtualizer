---
adr-id: ADR-003
project: [[05_PROJECTS/ACTIVE/udie]]
status: ACCEPTED (retroactive)
decision-date: 2026-02
documented-date: 2026-05-12
tags: [adr, retroactive, caching, streaming]
---
# ADR-003: Redis for cache and stream coordination in UDIE

## Context (reconstructed)
UDIE's hot-path (real-time risk evaluation, live signal ingestion) requires sub-millisecond reads for frequently accessed data (active risk cells, current hotspots). The cold-path (PostgreSQL) is the authoritative store, but read latency is too high for real-time mobile client updates.

## Decision
Redis deployed alongside PostgreSQL — used for hot-path caching of materialized views and as a coordination layer for stream processing between workers.

## Why This Was Chosen (reconstructed)
- Sub-millisecond read latency for cached risk cells and hotspot data
- Pub/Sub and Streams for coordinating worker processes
- Simple key-value interface for materialized view caching
- Well-supported in NestJS ecosystem

## Alternatives That Were Likely Considered
- **In-process cache (Map/LRU)** — doesn't survive restarts, can't be shared across worker processes
- **Memcached** — no Pub/Sub, no Streams, less flexible data structures
- **Kafka** — overkill for the current scale, adds significant operational complexity

## Consequences (observed)
Positive:
- Hot-path reads are fast enough for real-time mobile clients
- Worker coordination via Redis Streams is reliable

Negative / trade-offs:
- Cache invalidation complexity (must sync with PostgreSQL writes)
- Additional infrastructure component to manage
- Potential connection pool exhaustion under load (common Redis failure mode)

## Would You Make This Decision Again?
Yes — Redis is the standard choice for this pattern. Would add connection pool monitoring from day one.
