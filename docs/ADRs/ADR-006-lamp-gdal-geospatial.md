---
adr-id: 006-lamp-gdal-geospatial
project: [[05_PROJECTS/ACTIVE/lamp]]
status: ACCEPTED (retroactive)
decision-date: 2026-03
documented-date: 2026-05-12
tags: [adr, retroactive, geospatial,gis]
---
# ADR-006-lamp-gdal-geospatial: GDAL as the geospatial processing library for LAMP

## Context (reconstructed)
LAMP needed raster I/O, coordinate transforms, viewshed computation, and terrain analysis. GDAL/OGR is the industry-standard C library for geospatial data.

## Decision
GDAL/OGR via Python bindings (rasterio, fiona, osgeo).

## Why This Was Chosen (reconstructed)
GDAL is the only library with complete raster+vector+projection support. No Python-native alternative covers the full geospatial stack.

## Alternatives That Were Likely Considered
- **rasterio-only** — rasterio-only (covers rasters but not vectors or projections)
- **pure-Python alternatives like shapely+pyproj** — pure-Python alternatives like shapely+pyproj (slower, incomplete raster support)

## Consequences (observed)
Positive:
- Cross-platform geospatial processing works

Negative / trade-offs:
- GDAL version differences between macOS and Linux cause runtime failures (audit defect). GDAL is notoriously hard to install and pin.

## Would You Make This Decision Again?
Partially — GDAL is necessary but would invest more in Docker-based reproducibility from day one.
