---
adr-id: ADR-011
project: [[05_PROJECTS/ACTIVE/healingstone]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, quality, tooling]
---
# ADR-011: mypy strict + ruff as quality gate stack for healingstone

## Context (reconstructed)
Healingstone is a research pipeline where correctness matters more than velocity. Type errors in descriptor matching or reconstruction can produce silently wrong results. A strict quality gate was needed.

## Decision
mypy in strict mode + ruff for linting + pytest with coverage reporting. All three must pass in CI.

## Why This Was Chosen (reconstructed)
- mypy strict catches type errors that would silently corrupt reconstruction results
- ruff is faster than flake8+isort+black combined, reducing CI time
- Coverage reporting ensures test gaps are visible

## Alternatives That Were Likely Considered
- **pylint** — more opinionated, slower, harder to configure for scientific code
- **pyright** — also good but mypy has broader ecosystem support
- **No type checking** — unacceptable for a pipeline where silent type coercion causes wrong results

## Consequences (observed)
Positive:
- Most mature quality gate stack of all 7 repos (audit observation)
- Type errors caught at CI, not at runtime
- ruff is fast enough to run on every save

Negative / trade-offs:
- mypy strict can be verbose for scientific code with numpy arrays
- Initial setup cost of adding type annotations to all functions

## Would You Make This Decision Again?
Yes — this is the model quality stack. Every other project should adopt this.
