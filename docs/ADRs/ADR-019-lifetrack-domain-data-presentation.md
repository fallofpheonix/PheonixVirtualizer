---
adr-id: ADR-019
project: [[05_PROJECTS/ACTIVE/lifetrack]]
status: ACCEPTED (retroactive)
decision-date: 2026-02
documented-date: 2026-05-12
tags: [adr, retroactive, architecture, flutter]
---
# ADR-019: Domain/Data/Presentation architecture pattern for LifeTrack

## Context (reconstructed)
LifeTrack is a large Flutter app with 6+ feature modules (Vitals, Activity, Hydration, Nutrition, Medical, Profile). A clear architectural pattern was needed to prevent feature modules from becoming monolithic.

## Decision
Domain/Data/Presentation separation: domain models as POJOs, data layer with Drift repositories, presentation layer with Riverpod state management and Flutter widgets.

## Why This Was Chosen (reconstructed)
- Clean Architecture principles applied to Flutter
- Domain models are framework-independent (testable without Flutter)
- Data layer (Drift) is isolated behind repository interfaces
- Presentation layer uses Riverpod providers for reactive state

## Alternatives That Were Likely Considered
- **BLoC pattern** — used in other projects but more boilerplate than Riverpod
- **Provider (raw)** — simpler but less structured than Riverpod
- **MVC** — doesn't map well to Flutter's reactive model

## Consequences (observed)
Positive:
- Each feature module follows the same pattern — consistent codebase
- Domain models are testable independently
- Repository pattern abstracts database access

Negative / trade-offs:
- Lots of boilerplate (model + repository + provider + widget for each feature)
- Drift code generation adds build complexity

## Would You Make This Decision Again?
Yes — this pattern is correct for a feature-rich Flutter app. The boilerplate is a reasonable cost for maintainability.
