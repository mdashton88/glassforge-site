# Vehicle Forge — Data Governance

**Document:** DATA_GOVERNANCE.md  
**Authority:** MANDATORY READ before any session that reads, writes, or audits vehicle or weapon data.  
**Last Audit:** 2026-02-23 (commit below)  
**Tool Version:** v0.8.22  

---

## Rule One: Read This First

Any Claude session that touches Vehicle Forge weapon data, vehicle builds, pack files, or the weapon catalogue **must read this document before making any changes.** No exceptions. If this document and another file disagree, this document wins until Mike explicitly updates it.

---

## Sources of Truth (in priority order)

### 1. Weapon Catalogue — `vehicle-forge.html` → `var WEAPONS=[]`

This is the **single canonical definition** of every weapon in the system. 127 weapons across 7 eras: ancient, medieval, blackpowder, industrial, modern, future, advanced.

Every weapon's `id`, `name`, `damage`, `ap`, `rof`, `range`, and `notes` are authored here and nowhere else. All other files — packs, exports, databases — inherit copies of these values. When a weapon stat changes, it changes here first and propagates outward.

**SWADE Core weapons (19 verified against pp.79-81):** mmg, hmg, cannon_20mm, autocannon_25mm, autocannon_30mm, tank_gun_37mm, tank_gun_75mm, tank_gun_76mm, tank_gun_88mm, tank_gun_120mm, tank_gun_125mm, flamethrower_ww, torpedo_ww, tow_missile, hellfire, sidewinder, sparrow, laser_gat, laser_heavy.

**Era variant pairs (identical stats, different IDs for UI filtering):** mmg/mmg_modern, hmg/hmg_modern, tank_gun_37mm/tank_gun_light, tank_gun_75mm/tank_gun_med, tank_gun_88mm/tank_gun_heavy, autocannon_ww/cannon_20mm, tank_gun_125mm/cannon_mod, tow_missile/atgm.

### 2. Canon Vehicle Builds — `vehicle-forge.html` → `var CANON_BUILDS=[]`

47 vehicles reproducing SWADE Core Rules pp.82-86. 27 armed, 20 unarmed, 78 weapon mounts. Every loadout verified line-by-line against the rulebook. These are what the tool loads on first visit.

### 3. Downloadable Packs — `packs/XX_Name/*.vfx` and `*.cvf.json`

54 unique packs across 13 thematic families. 547 unique vehicles, 381 armed. Each pack embeds a copy of the weapons it references from the canonical catalogue. The `.vfx` and `.cvf.json` versions of each pack must contain identical vehicle and weapon data.

### 4. Everything Else — development scaffolding

`vehicle-database.json`, `v5.0/data/*.json`, `archive/` — these are calibration data, legacy exports, or empty placeholders. They are not authoritative. Do not read from them to determine what a weapon's stats should be. Do not update them unless Mike specifically requests it.

---

## The Golden Rules

### Never invent weapon stats.
If a weapon ID doesn't exist in `var WEAPONS=[]`, it doesn't exist. Don't create approximate values. Don't guess from the name. Flag it as a broken reference and stop.

### Never assume SWADE stats from memory.
Always verify against the actual SWADE text in project knowledge (pp.79-86) or the canonical catalogue. Previous sessions may have contained errors. The catalogue is the corrected, verified version.

### Pack embedded weapons must mirror the catalogue exactly.
When regenerating packs, copy weapon definitions verbatim from `var WEAPONS=[]`. Do not reformat, round, abbreviate, or "improve" the values.

### VFX and CVF pairs must match.
If you update a `.vfx` file, update the matching `.cvf.json` file with identical vehicle and weapon data.

### Commit messages must include audit scope.
Every commit that touches weapon or vehicle data must state: how many weapons/vehicles were changed, what was verified, and against what source.

---

## File Map

```
vehicle-forge.html                          ← THE SOURCE OF TRUTH
  └─ var WEAPONS=[]                         ← 127 weapons, 7 eras (CANONICAL)
  └─ var CANON_BUILDS=[]                    ← 47 SWADE core vehicles (CANONICAL)

packs/
  00_Core_Tool/                             ← Core reference packs (3 packs, ~47 veh)
  01_Blood_and_Thunder/                     ← Naval (6 packs, 53 vehicles)
  02_Iron_and_Steel/                        ← Ground (8 packs, 73 vehicles)
  03_Talons_and_Contrails/                  ← Air (5 packs, 43 vehicles)
  04_Star_and_Void/                         ← Sci-fi (5 packs, 43 vehicles)
  05_Fang_and_Claw/                         ← Mechs (5 packs, 43 vehicles)
  06_Sails_and_Gasbags/                     ← Airships (3 packs, 23 vehicles)
  07_Chrome_and_Fury/                       ← Chase/civilian (4 packs, 33 vehicles)
  08_Dread_and_Ruin/                        ← Horror (3 packs, 23 vehicles)
  09_Saddle_and_Fang/                       ← Mounts (4 packs, 33 vehicles, all unarmed)
  10_Rust_and_Ruin/                         ← Post-apoc (3 packs, 23 vehicles)
  11_Brass_and_Steam/                       ← Steampunk (3 packs, 23 vehicles)
  12_Wire_and_Chrome/                       ← Cyberpunk (3 packs, 23 vehicles)
  Total: 54 packs, 547 vehicles + 47 CANON_BUILDS = 594 unique

Vehicle_Forge_Core_Reference_Builds.vfx     ← Generated export of CANON_BUILDS
VEHICLE_MANIFEST.json                       ← Machine-readable file inventory
DATA_GOVERNANCE.md                          ← THIS FILE
VEHICLE_FORGE_VERSIONING.md                 ← Human-readable architecture overview
Vehicle_Forge_Technical_Reference_v1_0.md   ← Full technical reference (formulas, etc.)
```

---

## Inventory at Last Audit

| Metric | Count |
|--------|-------|
| Weapons in catalogue | 127 |
| Weapons verified vs SWADE canon | 19/19 |
| Unique vehicles (deduplicated) | 594 |
| Armed vehicles | 408 |
| Weapon mounts (all vehicles) | 871 |
| Unique weapon IDs referenced in packs | 40 |
| Broken weapon references | 0 |
| Embedded DB mismatches | 0 |
| VFX/CVF pair mismatches | 2 (cosmetic, Core_Tool only) |
| Pack families | 13 |
| Unique packs | 54 |

---

## Update Procedure

### Changing a weapon stat
1. Edit `var WEAPONS=[]` in `vehicle-forge.html`
2. If it's a SWADE Core weapon, verify against pp.79-81
3. If it has an era variant pair, update both IDs
4. Search all `.vfx` and `.cvf.json` files for embedded copies — update them
5. Regenerate `Vehicle_Forge_Core_Reference_Builds.vfx` if affected
6. Commit with: what changed, how many files affected, what was verified

### Adding a weapon
1. Add to `var WEAPONS=[]` with a unique `id`
2. Assign correct `era`
3. If it's a real-world weapon, verify stats against published Savage Worlds source
4. Commit with source citation

### Adding a vehicle to a pack
1. Build in Vehicle Forge UI using existing catalogue weapons
2. Export `.vfx`, generate matching `.cvf.json`
3. Verify all weaponIds resolve to catalogue
4. Place in correct `packs/XX_Name/` directory

### Adding a new pack family
1. Create `packs/XX_Name/` directory
2. Follow naming convention: `XX_Name_PackTitle.vfx` / `.cvf.json`
3. Update this document's inventory table
4. Update `VEHICLE_MANIFEST.json`

---

## Automated Sync & Audit

**Script:** `python3 sync_and_audit.py`  
**CI Pipeline:** `.github/workflows/vehicle-audit.yml`

The audit runs automatically on every push or pull request that touches weapon data, vehicle builds, pack files, or the audit script itself. It also runs on manual dispatch. The pipeline performs two checks: first the full audit (Tier 1 hard canon, era variants, family progressions, pack integrity, downstream sync), then a desync detection that runs the sync engine and fails if any downstream file would be changed — meaning someone edited the source of truth but forgot to propagate.

**To run locally** before committing:

```
python3 sync_and_audit.py              # Full sync + audit
python3 sync_and_audit.py --audit-only # Audit without syncing
python3 sync_and_audit.py --sync-only  # Sync without full audit
```

**Exit codes:** 0 = all clear, 1 = Tier 1 failure (must fix), 2 = Tier 2 warnings (review).

### What the script checks

**Sync:** Pushes corrected weapon loadouts from `Vehicle_Forge_Core_Reference_Builds.vfx` to all downstream files automatically. No manual propagation.

**Tier 1 — Hard Canon (must match exactly):**
- 19 SWADE Core weapon definitions vs pp.79-81 (damage, AP, RoF, range)
- 8 era variant pairs must have identical stats
- 12 weapon family progressions must increase monotonically
- All pack embedded weapon DBs must mirror the canonical catalogue
- All downstream files must be in sync with canon

**Tier 2 — Calibration Sense Check:**
- Damage graded A through E with scaled tolerances
- AP classified into penetration bands by delivery method
- Weapon counts reported per grade and band for manual review

---

## Calibration Framework

### Damage Grades

Tolerance scales with the weapon's output. At the light end, even a single point changes combat outcomes. At the heavy end, several points make no practical difference.

| Grade | Avg Damage | Tolerance | Covers |
|-------|-----------|-----------|--------|
| A | ≤7 | ±0 (exact) | Daggers, javelins, scorpions, bow batteries |
| B | 7–11 | ±1 | Machine guns, ballista, rams, swivel guns |
| C | 11–18 | ±2 | Autocannons, flamethrowers, Sidewinders, catapults |
| D | 18–28 | ±3 | Tank guns, TOW, Hellfire, Heavy Laser, Sparrow |
| E | 28+ | ±4 | Torpedoes, cruise missiles, mega lasers, railguns |

### AP Bands

AP represents penetration capability — the weapon's ability to defeat protective material. It is not proportional to damage. A flamethrower does heavy damage with AP 0 (heat, not penetration). A Heavy Laser does moderate damage with AP 30 (concentrated energy cuts through armour). The band must match the weapon's delivery method.

| Band | AP Range | Logic |
|------|----------|-------|
| NONE | 0 | Blast, fire, fragmentation. No penetration. |
| LIGHT | 1–2 | Rifle-calibre, bolts, arrows. Defeats cover and light skin. |
| MEDIUM | 3–6 | HMG, autocannon, medium guns, frag warheads. Defeats light vehicles. |
| HEAVY | 7–16 | HVAP, heavy AT guns, improved penetrators. Defeats medium armour. |
| VERY HEAVY | 17–34 | Modern tank guns, shaped charges, torpedoes. Defeats heavy armour. |
| CAPITAL | 35+ | Top-tier guided AT, mega weapons. Defeats anything. |

### Additional Hard Checks

- **RoF must be exact.** Small integer that directly affects action economy.
- **Weapon families must progress monotonically.** A Medium Laser must do less than a Heavy Laser.
- **Era variants must be identical.** `mmg` and `mmg_modern` are the same weapon in different UI filters.

---

## Audit Procedure

Before any commit touching weapon or vehicle data:

1. Run `python3 sync_and_audit.py`
2. If exit code 0: commit freely
3. If exit code 1: fix all Tier 1 failures before committing
4. If exit code 2: review Tier 2 warnings, fix or document exceptions
5. Include audit result summary in commit message

---

## Audit Log

| Date | Commit | Scope | Result |
|------|--------|-------|--------|
| 2026-02-23 | 2703190 | 19 SWADE Core weapon definitions | 19/19 match pp.80-81 |
| 2026-02-23 | 0bcc69f | 47 CANON_BUILDS loadouts | 47/47 match pp.82-86. 6 fixes applied. |
| 2026-02-23 | adb9fdf | Full repo: 594 vehicles, 114 files | 0 broken refs, 0 stat mismatches |
| 2026-02-23 | 1955993 | Downstream sync: 6 secondary files | All synced with corrected canon |
| 2026-02-23 | (this) | sync_and_audit.py first run | T1: 19/19, Variants: 8/8, Families: 12/12, Packs: 53/53, Sync: 6/6 |
| 2026-02-23 | (this) | 100-encounter combat proving ground | 960 attacks, 37 weapons, 5 grades, 5 AP bands. All sanity checks pass. |
