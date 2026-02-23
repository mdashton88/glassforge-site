# Vehicle Forge — Versioning & Data Architecture

**Last Verified:** 2026-02-23  
**Commit:** 0bcc69f + this commit  
**Status:** ALL CLEAN — 594 unique vehicles, 408 armed, 0 broken references

---

## Single Source of Truth

The **weapon catalogue** lives in `vehicle-forge.html` as `var WEAPONS=[]`. This array of 127 weapons across 7 eras is the canonical definition of every weapon's name, damage, AP, RoF, range, and notes. All other files inherit from it.

The **core vehicle builds** live in `vehicle-forge.html` as `var CANON_BUILDS=[]`. These 47 vehicles (27 armed) reproduce SWADE Core Rules pp.82-86 exactly.

When resolving any discrepancy, `vehicle-forge.html` wins. Always.

---

## File Architecture

### Live Tool (browser loads this)
| File | Role |
|------|------|
| `vehicle-forge.html` | THE tool. Contains WEAPONS catalogue (127), CANON_BUILDS (47), all UI logic. |

### Downloadable Packs (users import these)
Each pack exists as a paired `.vfx` and `.cvf.json` file in `packs/`. The VFX and CVF versions must always contain identical vehicle and weapon data. Each pack embeds a copy of the weapons it references from the canonical catalogue.

| Directory | Packs | Vehicles | Armed | Theme |
|-----------|-------|----------|-------|-------|
| `packs/00_Core_Tool/` | 3 | ~47 each | 27 | SWADE core reference |
| `packs/01_Blood_and_Thunder/` | 6 | 53 | 48 | Naval warfare, all eras |
| `packs/02_Iron_and_Steel/` | 8 | 73 | 71 | Ground combat, all eras |
| `packs/03_Talons_and_Contrails/` | 5 | 43 | 43 | Air warfare, all eras |
| `packs/04_Star_and_Void/` | 5 | 43 | 38 | Sci-fi starships |
| `packs/05_Fang_and_Claw/` | 5 | 43 | 38 | Mechs and walkers |
| `packs/06_Sails_and_Gasbags/` | 3 | 23 | 16 | Fantasy airships |
| `packs/07_Chrome_and_Fury/` | 4 | 33 | 23 | Modern civilian/chase |
| `packs/08_Dread_and_Ruin/` | 3 | 23 | 7 | Horror vehicles |
| `packs/09_Saddle_and_Fang/` | 4 | 33 | 0 | Mounts and beasts |
| `packs/10_Rust_and_Ruin/` | 3 | 23 | 16 | Post-apocalyptic |
| `packs/11_Brass_and_Steam/` | 3 | 23 | 19 | Steampunk/Victorian |
| `packs/12_Wire_and_Chrome/` | 3 | 23 | 10 | Cyberpunk |

**Total unique pack vehicles:** 547 (381 armed, 793 weapon mounts)  
**Plus CANON_BUILDS:** 47 (27 armed, 78 weapon mounts)  
**Grand total:** 594 unique vehicles, 408 armed

### Development / Calibration Data
| File | Status | Notes |
|------|--------|-------|
| `v5.0/data/canon-vehicles.json` | DEVELOPMENT | 75 vehicles, calibration reference |
| `v5.0/data/ammaria-vehicles.json` | DEVELOPMENT | 12 Tribute Lands vehicles |
| `v5.0/data/swade-core-rebuild.json` | DEVELOPMENT | 47 vehicles, formula calibration |
| `v5.0/data/swade-core-rebuilds.json` | DEVELOPMENT | 47 vehicles, unarmed calibration |
| `vehicle-database.json` | LEGACY EXPORT | 47 vehicles, mirrors CANON_BUILDS |

### Archived (no active vehicle data)
| Directory | Notes |
|-----------|-------|
| `archive/v4.0/presets/*.vfx` | 12 empty placeholder files from v4.0 |

### Generated Exports
| File | Notes |
|------|-------|
| `Vehicle_Forge_Core_Reference_Builds.vfx` | Generated from CANON_BUILDS, v1.1 |

---

## Weapon Catalogue Summary

127 weapons across 7 eras. The 25 weapons used in SWADE Core vehicle loadouts are verified line-by-line against pp.79-86.

| Era | Count | Examples |
|-----|-------|----------|
| Ancient | 8 | Scorpion, Onager, Greek Fire Siphon, Bronze Ram |
| Medieval | 8 | Catapult, Trebuchet, Ballista, Boiling Oil |
| Blackpowder | 8 | Light/Medium/Heavy Cannon, Carronade, Swivel Gun |
| Industrial | 17 | MMG, HMG, 20mm–88mm guns, Flamethrower, Torpedo |
| Modern | 24 | MMG/HMG, 25mm–125mm, TOW, Hellfire, Sidewinder, CIWS |
| Future | 40 | Gatling Laser, Autocannons, Missiles, Ion Cannons |
| Advanced | 22 | Mass Drivers, Particle Beams/Cannons, Super Lasers, Railgun |

Era variant pairs (e.g., `mmg` / `mmg_modern`) share identical stats and exist to allow era-appropriate filtering in the UI.

---

## Update Procedure

When changing weapon stats:
1. Edit `var WEAPONS=[]` in `vehicle-forge.html` — this is the only place stats are authored
2. Run the canon audit script to verify SWADE compliance
3. Regenerate any affected pack files (embedded weapon DBs must match)
4. Regenerate `Vehicle_Forge_Core_Reference_Builds.vfx`
5. Commit with audit results in the commit message

When adding vehicles to packs:
1. Build in the Vehicle Forge UI using canonical weapons
2. Export to `.vfx` format
3. Generate matching `.cvf.json`
4. Place both in the appropriate `packs/XX_Name/` directory

---

## Audit History

| Date | Commit | Result |
|------|--------|--------|
| 2026-02-23 | 0bcc69f | 47/47 CANON_BUILDS verified. 19/19 weapon definitions match SWADE. 6 loadout fixes applied. |
| 2026-02-23 | (this) | 594 unique vehicles audited. 0 broken refs. 0 embedded DB mismatches. All packs clean. |
