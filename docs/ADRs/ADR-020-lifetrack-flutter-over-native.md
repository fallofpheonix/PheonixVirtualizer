---
adr-id: ADR-020
project: [[05_PROJECTS/ACTIVE/lifetrack]]
status: ACCEPTED (retroactive)
decision-date: 2026-02
documented-date: 2026-05-12
tags: [adr, retroactive, mobile, flutter]
---
# ADR-020: Flutter over React Native or native iOS/Android for LifeTrack

## Context (reconstructed)
LifeTrack is a health tracking app that needs to run on both iOS and Android. A cross-platform framework was preferred to avoid maintaining two codebases.

## Decision
Flutter (Dart) with Riverpod and Drift.

## Why This Was Chosen (reconstructed)
- Flutter's widget system provides pixel-perfect control for custom health dashboards
- Dart's strong typing catches errors at compile time
- Drift (SQLite) provides type-safe local persistence — critical for health data integrity
- Already familiar with Flutter from the tech stack (evidenced by portfolio)

## Alternatives That Were Likely Considered
- **React Native** — JavaScript ecosystem but less performant for custom UI, no equivalent to Drift
- **Native iOS + Android** — best platform integration (HealthKit/Google Fit) but double the codebase
- **Kotlin Multiplatform** — emerging but less mature ecosystem at decision time

## Consequences (observed)
Positive:
- Single codebase for iOS + Android
- Rich custom UI for health dashboards (fl_chart, custom widgets)
- Type-safe data layer with Drift

Negative / trade-offs:
- HealthKit/Google Fit integration requires platform channels — currently TODO (audit defect)
- Flutter's platform channel layer is more complex than native for health sensor access
- Generated platform scaffold files pollute the repo

## Would You Make This Decision Again?
Yes — Flutter is correct for this app. Would prioritize HealthKit/Google Fit integration earlier in development.
