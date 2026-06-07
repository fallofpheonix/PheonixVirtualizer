---
adr-id: ADR-014
project: [[05_PROJECTS/ACTIVE/sira]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, algorithms, simulation]
---
# ADR-014: Stochastic (Gillespie) over deterministic ODE simulation for sira

## Context (reconstructed)
Epidemiological models can be simulated deterministically (solve ODE system directly) or stochastically (simulate individual events). The project needed training data for a neural vector-field approximation.

## Decision
Gillespie stochastic simulation algorithm with ensemble averaging to generate training data.

## Why This Was Chosen (reconstructed)
- Stochastic simulation captures variance and rare events that deterministic ODEs miss
- Ensemble averaging (many stochastic runs → mean trajectory) produces smoother training targets
- Gillespie is the gold-standard exact stochastic simulation algorithm for chemical/biological kinetics
- The gap between stochastic reality and deterministic approximation is scientifically interesting

## Alternatives That Were Likely Considered
- **Direct ODE integration (scipy.integrate.odeint)** — faster but misses stochastic effects
- **Tau-leaping** — faster approximate stochastic method but less accurate than exact Gillespie
- **Agent-based models** — more realistic but computationally expensive and harder to derive vector fields from

## Consequences (observed)
Positive:
- Training data captures real stochastic dynamics
- Ensemble averaging provides smooth vector-field targets
- Scientifically rigorous — Gillespie is exact

Negative / trade-offs:
- Gillespie is slow for large populations (each event simulated individually)
- Ensemble of simulations requires significant compute time
- Training data generation is the bottleneck, not model training

## Would You Make This Decision Again?
Yes — for equation discovery, stochastic simulation is the correct data source. Would add tau-leaping as an optional fast mode for quick iterations.
