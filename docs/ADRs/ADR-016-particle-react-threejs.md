---
adr-id: ADR-016
project: [[05_PROJECTS/ACTIVE/particle-stimulator]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, frontend, visualization]
---
# ADR-016: React + Three.js for 3D particle visualization

## Context (reconstructed)
Particle collision events need to be visualized in 3D space — showing particle trajectories, collision points, detector geometry, and energy distributions. The visualization must update in real-time as WebSocket events arrive.

## Decision
React for UI framework + Three.js for 3D rendering, bundled with Vite.

## Why This Was Chosen (reconstructed)
- Three.js is the standard browser-based 3D engine — handles particle rendering, camera controls, and scene management
- React provides component-based UI for dashboard controls, parameter inputs, and data displays
- Vite provides fast HMR for development iteration
- Already used React in other projects (AI4MH, TerraHerb)

## Alternatives That Were Likely Considered
- **Plotly/D3.js** — 2D only, not suitable for 3D particle visualization
- **Unity WebGL** — heavy, slow to iterate, overkill for scientific visualization
- **Babylon.js** — viable alternative to Three.js but smaller community and fewer scientific examples

## Consequences (observed)
Positive:
- 3D particle visualization works in the browser — no desktop app needed
- React state management cleanly separates simulation controls from visualization

Negative / trade-offs:
- Three.js has a steep learning curve for custom particle rendering
- No frame rate benchmarks — unclear if visualization keeps up at high event rates

## Would You Make This Decision Again?
Yes — React + Three.js is the standard choice for browser-based 3D scientific visualization.
