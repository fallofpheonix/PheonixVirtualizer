---
adr-id: ADR-023
project: [[05_PROJECTS/ACTIVE/autoeit-suite]]
status: PROPOSED (retroactive — merge not yet executed)
decision-date: 2026-05
documented-date: 2026-05-12
tags: [adr, retroactive, architecture, monorepo]
---
# ADR-023: Merging audio_transcription + AutoEIT-STS into one suite

## Context (reconstructed)
Two separate repos exist: audio_transcription (Whisper-based Spanish ASR) and AutoEIT-STS (deterministic scoring). They form a natural pipeline: audio_transcription's output (transcribed sentences in Excel) is AutoEIT-STS's input. Currently, a researcher must manually run one tool, then the other, copying files between them.

## Decision
Merge both repos into a single autoeit-suite monorepo with a packages/ structure: autoeit_transcribe, autoeit_score, autoeit_common.

## Why This Was Chosen (reconstructed)
- Natural upstream/downstream pipeline — output of transcription is input of scoring
- Shared code (compatibility layers) is currently duplicated between repos
- Single CLI entry point for end-to-end processing reduces researcher friction
- Ecosystem audit explicitly recommends this merge

## Alternatives That Were Likely Considered
- **Keep separate repos, add API contract** — maintains independence but forces file-copying workflow
- **Publish as separate pip packages with shared dependency** — too much infra for a two-person research tool
- **Monorepo with no shared package** — misses the opportunity to deduplicate compatibility code

## Consequences (expected)
Positive:
- End-to-end pipeline in one command: audio in → audit report out
- Shared code deduplicated into autoeit_common
- Single CI pipeline covers both tools

Negative / trade-offs:
- Merge requires BFG cleanup of committed binaries first
- Both tools lose independent versioning
- Monorepo tooling (workspaces) adds initial setup complexity

## Would You Make This Decision Again?
Yes — these tools are a pipeline, not independent projects. The merge is overdue.
