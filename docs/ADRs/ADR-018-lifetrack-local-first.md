---
adr-id: ADR-018
project: [[05_PROJECTS/ACTIVE/lifetrack]]
status: ACCEPTED (retroactive)
decision-date: 2026-02
documented-date: 2026-05-12
tags: [adr, retroactive, architecture, mobile, privacy]
---
# ADR-018: Local-first architecture with no backend sync for LifeTrack

## Context (reconstructed)
LifeTrack stores sensitive health data (vitals, medical records, activity logs). A decision was needed about where this data lives — on a backend server with sync, or locally on the device only.

## Decision
Zero-cloud architecture. All data stored locally using Drift (SQLite). No backend server, no cloud sync, no remote data storage.

## Why This Was Chosen (reconstructed)
- Privacy-first: health data never leaves the device
- Simplicity: no backend to build, deploy, or maintain
- Offline-first: app works without internet connectivity
- GDPR/HIPAA concerns avoided by not collecting data at all

## Alternatives That Were Likely Considered
- **Backend + sync (Firebase/Supabase)** — enables cross-device sync but requires cloud data storage of sensitive health information
- **End-to-end encrypted sync** — best of both worlds but significantly more complex to implement
- **Local + optional manual export** — current approach with FHIR export planned

## Consequences (observed)
Positive:
- Zero privacy liability — no server breach can leak health data
- Works fully offline
- No backend infrastructure costs

Negative / trade-offs:
- No cross-device sync (data locked to one phone)
- No backup if phone is lost — all data lost
- No encrypted storage — data is accessible if device is compromised (audit defect)
- No threat model — the "privacy-first" claim isn't backed by actual security measures

## Would You Make This Decision Again?
Partially — local-first is correct for health data, but would add encrypted storage and local backup from day one. "No cloud" does not mean "no security."
