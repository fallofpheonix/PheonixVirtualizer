---
adr-id: ADR-005
project: [[05_PROJECTS/ACTIVE/udie]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, infrastructure, kubernetes]
---
# ADR-005: Kubernetes for UDIE infrastructure orchestration

## Context (reconstructed)
UDIE runs multiple services: NestJS backend, PostgreSQL + PostGIS, Redis, Prometheus, Grafana. Local development uses Docker Compose, but the system is designed for Kubernetes deployment for production scaling.

## Decision
Kubernetes manifests for production orchestration, Docker Compose for local development.

## Why This Was Chosen (reconstructed)
- Multiple services need coordinated deployment and scaling
- Kubernetes provides service discovery, health checks, and auto-restart
- Prometheus + Grafana integrate naturally with Kubernetes monitoring

## Alternatives That Were Likely Considered
- **Docker Compose only** — sufficient for development but no auto-scaling or health management
- **AWS ECS / GCP Cloud Run** — vendor lock-in, less portable
- **Bare metal / systemd** — too manual for multi-service orchestration

## Consequences (observed)
Positive:
- Production-ready infrastructure pattern from the start
- Observability stack (Prometheus/Grafana) integrates cleanly
- Portable across cloud providers

Negative / trade-offs:
- Kubernetes adds significant operational complexity for a solo developer
- Local development still uses Docker Compose (potential config drift)
- No deployment SLOs defined yet (audit defect)

## Would You Make This Decision Again?
Partially — Kubernetes is correct for the target scale, but deploying it too early adds operational burden. Would use Docker Compose longer and migrate to K8s only when scaling requires it.
