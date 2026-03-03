# glassforge-site

**Glassforge Games — public website and tools.**
Deployed via Cloudflare Pages at [glassforge.pages.dev](https://glassforge.pages.dev)

## ⚠ Data Governance — READ FIRST

**Before working on Vehicle Forge weapon data, vehicle builds, or pack files, read [`DATA_GOVERNANCE.md`](DATA_GOVERNANCE.md).** This document defines the single source of truth, the update procedure, and the audit process. All weapon stats are authored in `vehicle-forge.html` and propagate outward to packs. See also [`VEHICLE_FORGE_VERSIONING.md`](VEHICLE_FORGE_VERSIONING.md) for the full file architecture.

## Tools

```
index.html                  Landing page — Glassforge Games branding
builder.html                Character Forge — free Savage Worlds character builder
vehicle-forge.html   Vehicle Forge — free Savage Worlds vehicle construction tool
vehicle-database.json       Vehicle database (47 SWADE core reference builds)
vehicle-forge-manual.pdf    Vehicle Forge Companion Guide
swade-core.js               Savage Worlds core rules data module
```

## Vehicle Forge

Interactive vehicle construction tool for Savage Worlds. Original Glassforge design
rules compatible with Savage Worlds vehicle mechanics (Size, Handling, Toughness,
Wounds, Mods). Ships with 47 canon reference builds from the Savage Worlds core
rulebook, three export formats (JSON, Pinnacle stat block, Fantasy Grounds XML),
and a Vehicle Hangar for saving and managing builds. Supports .vfx extension packs.

## Character Forge

Step-by-step character builder for Savage Worlds. Exports to Fantasy Grounds Unity
XML, PDF, HTML, and RTF. Displays summary-level reference data to support character
creation decisions. Full rules text remains in the published Savage Worlds rulebook.

## Deployment

Pushes to `main` auto-deploy via Cloudflare Pages (~30 seconds).

## Legal

Savage Worlds and all related marks © Pinnacle Entertainment Group.
Used under the Savage Worlds Fan License. Pinnacle makes no representation
or warranty as to the quality, viability, or suitability for purpose of
this product.

Fantasy Grounds is a trademark of SmiteWorks USA, LLC.
Foundry Virtual Tabletop is a trademark of Foundry Gaming LLC.

This product is not affiliated with or endorsed by Pinnacle Entertainment
Group, SmiteWorks, or Foundry Gaming.

Vehicle Forge and Character Forge © Glassforge Games Ltd.
