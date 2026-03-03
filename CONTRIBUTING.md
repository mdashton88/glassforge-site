# Contributing to Vehicle Forge

## Quick Start

```bash
git clone https://github.com/mdashton88/glassforge-site.git
cd glassforge-site
python3 sync_and_audit.py --audit-only    # Verify everything's clean
python3 test_combat_regression.py          # Run combat sanity checks
```

If either script reports failures, do not commit until resolved.

## Before You Touch Anything

**Read `DATA_GOVERNANCE.md` first.** It defines the source of truth hierarchy, the calibration framework, and the audit procedures. All data flows from `vehicle-forge.html` downward. Never edit downstream files directly.

For architecture, formulas, and design rationale, see `Vehicle_Forge_Technical_Reference_v1_0.md`.

## Source of Truth

| Data | Source | Backups |
|------|--------|---------|
| Weapons (127) | `var WEAPONS[]` in `vehicle-forge.html` | `canonical-weapons.json` |
| Vehicles (47) | `var CANON_BUILDS[]` in `vehicle-forge.html` | `canonical-vehicles.json` |
| Specials (34) | `var SPECIALS[]` in `vehicle-forge.html` | `canonical-specials.json` |
| Mods (41) | `var MODS[]` in `vehicle-forge.html` | `canonical-mods.json` |

**Never edit the backup JSONs.** They are generated from the HTML and verified by the audit.

## Making Changes

1. Edit `vehicle-forge.html` (the source of truth)
2. Run `python3 sync_and_audit.py` — this propagates changes to all 6 downstream files and runs the full audit
3. Run `python3 test_combat_regression.py` — sanity-check combat feel
4. Regenerate backups if weapons/mods/specials changed
5. Commit with a descriptive message
6. Push — the GitHub Action will verify everything automatically

The Action blocks merges on Tier 1 failures (wrong SWADE stats, broken refs, stale files). Tier 2 warnings (content naming, calibration) are informational.

## What the Audit Checks

The audit runs 13 checks across two tiers:

**Tier 1 (blocks build):** SWADE canon weapon stats, era variant parity, family monotonic progression, pack integrity (all weapon refs resolve), downstream sync (6 files current).

**Tier 2 (warnings):** Calibration classification, description-vs-loadout consistency, specials-vs-description consistency, IP compliance (descriptions and catalogue names), crew count cross-reference, scaling benchmark, canonical backup verification (weapons, vehicles, specials, mods).

## IP Compliance

Vehicle Forge is an original design system producing Savage Worlds-compatible stat blocks. It is **not** a reproduction of the Science Fiction Companion's vehicle construction rules. Our formulas, weapon names, modification names, and special ability names are all original. The audit script scans for accidental IP contamination.

Do not paste stat blocks, weapon tables, or formulas from any Pinnacle publication. Reference SWADE pp.80–81 for the 19 published vehicular weapons only.

## Pack Files (.vfx)

Extension packs live in `packs/` organised by family. Each `.vfx` is a JSON file containing vehicles with weapon loadouts referencing the master catalogue. The audit verifies every weapon reference resolves and every description matches its mechanical data.

When writing vehicle descriptions, use our **game weapon names** (Light Autocannon, ATGM Launcher) rather than real-world calibre designations (30mm, Hellfire). The content integrity checker enforces this.

## Tagged Baselines

Clean audit states are tagged. If something goes wrong, roll back:

```bash
git tag -l 'audit-clean-*'         # List verified baselines
git checkout audit-clean-v2        # Restore last known-good state
```
