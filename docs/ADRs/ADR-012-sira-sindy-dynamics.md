---
adr-id: ADR-012
project: [[05_PROJECTS/ACTIVE/sira]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, algorithms, scientific-computing]
---
# ADR-012: SINDy for sparse identification of dynamical systems in sira

## Context (reconstructed)
After training an MLP to approximate the SIR vector field from Gillespie simulations, the project needed a way to discover interpretable governing equations from the learned dynamics. The goal was not just prediction but scientific insight — what differential equations govern the epidemic spread?

## Decision
Sparse Identification of Nonlinear Dynamics (SINDy) for sparse regression over a candidate function library.

## Why This Was Chosen (reconstructed)
- SINDy discovers parsimonious governing equations (sparse coefficients over candidate functions)
- Produces interpretable results — actual differential equations, not black-box predictions
- Complements the MLP: neural network for prediction, SINDy for interpretation

## Alternatives That Were Likely Considered
- **MLP only** — good prediction but no interpretability
- **Symbolic regression (PySR)** — also discovers equations but computationally expensive and less principled
- **Physics-informed neural networks (PINNs)** — constrains NN with known physics, but sira's goal is to discover the physics

## Consequences (observed)
Positive:
- Produces sparse, human-readable governing equations
- Validates the MLP approximation against known SIR dynamics

Negative / trade-offs:
- SINDy requires careful tuning of the sparsity threshold
- Candidate function library must be manually designed (domain knowledge required)

## Would You Make This Decision Again?
Yes — SINDy is the right tool for equation discovery. It's the scientific contribution of this project.
