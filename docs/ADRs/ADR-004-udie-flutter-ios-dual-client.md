---
adr-id: ADR-004
project: [[05_PROJECTS/ACTIVE/udie]]
status: ACCEPTED (retroactive)
decision-date: 2026-02
documented-date: 2026-05-12
tags: [adr, retroactive, mobile, flutter, ios]
---
# ADR-004: Flutter + iOS native dual mobile client strategy

## Context (reconstructed)
UDIE needs mobile clients for real-time risk visualization on maps. Two separate mobile codebases exist: a Flutter cross-platform client and an iOS-native Swift client.

## Decision
Maintain both Flutter (cross-platform) and iOS native (Swift) mobile clients.

## Why This Was Chosen (reconstructed)
- Flutter for rapid cross-platform coverage (Android + iOS from one codebase)
- iOS native for platform-specific features (MapKit, HealthKit integration, native performance)
- Likely started as Flutter-only, then added iOS native for specific features

## Alternatives That Were Likely Considered
- **Flutter only** — simpler maintenance but limited access to iOS-native APIs
- **iOS only** — loses Android coverage entirely
- **React Native** — Flutter was already known from LifeTrack project

## Consequences (observed)
Positive:
- Full platform coverage (Android via Flutter, iOS via both)
- iOS native client can use platform-specific optimizations

Negative / trade-offs:
- Two mobile codebases to maintain (double the mobile work)
- Feature parity drift between Flutter and iOS versions
- Unclear which client is the "primary" for new features

## Would You Make This Decision Again?
Partially — would start Flutter-only and add iOS native only for features that genuinely require it, not maintain two parallel clients.
