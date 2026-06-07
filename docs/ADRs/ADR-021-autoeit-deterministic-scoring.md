---
adr-id: ADR-021
project: [[05_PROJECTS/ACTIVE/autoeit-suite]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, algorithms, linguistics]
---
# ADR-021: Deterministic rule-based scoring over ML for AutoEIT

## Context (reconstructed)
AutoEIT-STS scores Spanish Elicited Imitation Task responses on a 0-4 scale. Linguistic researchers require auditable, reproducible scoring — the same input must always produce the same score, and the scoring logic must be explainable to non-technical linguists.

## Decision
Deterministic rule-based rubric scoring. No ML. Single scoring function with conservative 2/3 boundary for inter-rater reliability. Accent-insensitive comparison for practical transcription handling.

## Why This Was Chosen (reconstructed)
- Audit trail: every score is traceable to a specific rule in the rubric
- Reproducibility: deterministic scoring means longitudinal studies can re-score historical data and get identical results
- Stakeholder trust: linguists can read and validate the rubric, unlike an ML black box
- Inter-rater reliability: conservative 2/3 boundary prevents ambiguous scores

## Alternatives That Were Likely Considered
- **ML-based scoring (BERT/GPT)** — better at capturing nuance but non-deterministic, non-auditable, and requires training data from expert raters
- **Hybrid (rules + ML confidence)** — interesting but adds complexity that stakeholders didn't need
- **Human scoring only** — the baseline, but slow and expensive for large datasets

## Consequences (observed)
Positive:
- 100% reproducible scoring — same input always produces same output
- Auditable: any score can be traced to a specific rule
- No ML training data required

Negative / trade-offs:
- Cannot capture linguistic nuance that falls outside the rubric rules
- New patterns require manual rule additions
- Conservative boundary may under-score borderline responses

## Would You Make This Decision Again?
Yes — for research requiring audit trails and reproducibility, deterministic scoring is the only correct choice.
