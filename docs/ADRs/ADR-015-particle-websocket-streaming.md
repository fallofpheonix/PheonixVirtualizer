---
adr-id: ADR-015
project: [[05_PROJECTS/ACTIVE/particle-stimulator]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, networking, real-time]
---
# ADR-015: WebSocket for real-time simulation data streaming

## Context (reconstructed)
ParticleStimulator runs long Monte Carlo simulations that produce particle events continuously. Users need to see results in real-time as the simulation progresses, not wait for batch completion.

## Decision
WebSocket server at ws://127.0.0.1:8001/events for live event streaming from simulation to frontend.

## Why This Was Chosen (reconstructed)
- Full-duplex communication — server pushes events as they're generated
- Low latency compared to HTTP polling
- Natural fit for streaming simulation data (each particle collision is an event)
- Browser-native WebSocket API integrates cleanly with React frontend

## Alternatives That Were Likely Considered
- **Server-Sent Events (SSE)** — unidirectional only, can't receive client commands mid-simulation
- **HTTP polling** — high latency, wastes bandwidth on empty polls
- **gRPC streaming** — good performance but adds complexity, not browser-native

## Consequences (observed)
Positive:
- Live simulation visualization works — users see particles as they collide
- Low latency between simulation engine and frontend

Negative / trade-offs:
- No backpressure handling — if frontend falls behind, messages queue unbounded (audit defect)
- No typed event schema — WebSocket messages are untyped JSON
- Connection drops require manual reconnection logic

## Would You Make This Decision Again?
Yes — WebSocket is correct for this use case. Would add typed events (Pydantic schemas) and backpressure from day one.
