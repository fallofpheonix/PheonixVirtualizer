---
adr-id: ADR-022
project: [[05_PROJECTS/ACTIVE/autoeit-suite]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, output, stakeholder]
---
# ADR-022: Excel workbook as output format for AutoEIT

## Context (reconstructed)
AutoEIT-STS and audio_transcription produce scored results that researchers need to analyze, share with colleagues, and include in publications. The output format must be accessible to non-technical linguistic researchers.

## Decision
Excel workbooks (.xlsx) as the primary output format, processed via openpyxl.

## Why This Was Chosen (reconstructed)
- Researchers work in Excel — it's their native analysis tool
- Easy to share via email without requiring software installation
- Supports multiple sheets (raw scores, agreement reports, summary statistics)
- Stakeholder requirement — researchers explicitly requested Excel output

## Alternatives That Were Likely Considered
- **CSV** — simpler but no multi-sheet support, no formatting
- **JSON** — machine-readable but researchers can't analyze it directly
- **PDF reports** — good for final output but not for data analysis
- **Database export** — requires additional tooling researchers don't have

## Consequences (observed)
Positive:
- Researchers can immediately use output without additional tools
- Multi-sheet workbooks organize results cleanly

Negative / trade-offs:
- Excel files committed to git (audit defect — binary artifacts in repo)
- openpyxl dependency for a specialized format
- Version control of Excel files is poor (binary diffs)

## Would You Make This Decision Again?
Yes — but would add a parallel JSON export for programmatic access and never commit .xlsx outputs to git.
