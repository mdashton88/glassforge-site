# Vehicle Forge — Technical Reference v1.0

**DiceForge Studios Ltd.**
**Document 601 — February 2026**

---

## Purpose

This document is the canonical reference for the Vehicle Forge tool — its architecture, design philosophy, formulas, data structures, file locations, and development history. It exists so that new conversations can orient quickly without reconstructing decisions from transcripts.

---

## 1. What Vehicle Forge Is

Vehicle Forge is a free, browser-based vehicle construction tool for Savage Worlds. It lives at `diceforgestudios.pages.dev/vehicle-forge` and runs entirely client-side — no backend, no accounts, no login. All data persists in `localStorage`.

The tool is designed around Savage Worlds' *Fast! Furious! Fun!* philosophy. Six sliders control the core statistics. Weapons snap into mount points. Modifications add capability. Special abilities add character. The stat block generates in real time. A vehicle that takes thirty minutes to build from reference tables takes three minutes in the Forge.

Vehicle Forge is **not** a reproduction of the Science Fiction Companion's vehicle construction rules. It is an original DiceForge design system that produces Savage Worlds-compatible stat blocks. This distinction matters for IP compliance (see Section 9).

### Current Version: v0.8.22

---

## 2. Repository Structure

**Repo:** `github.com/mdashton88/diceforge-site`
**Deployment:** Cloudflare Pages, auto-deploys on push to `main` (~30 seconds)
**Live URL:** `diceforgestudios.pages.dev`

### Root Files — Active

| File | Purpose |
|------|---------|
| `vehicle-forge.html` | **The tool.** Single-file SPA, 171,618 bytes, 1,524 lines, 154 functions. Contains all HTML, CSS, JS, and data arrays inline. |
| `vehicle-forge-manual.pdf` | Companion Guide PDF (14 pages). Built by `build_manual.py`. |
| `build_manual.py` | Reportlab script that generates the Companion Guide PDF. |
| `vehicle-database.json` | Reference database: 47 SWADE core vehicles + 32 weapons + grade system. Used by the tool for canon reference data. |
| `vehicle-forge-landing.html` | Marketing landing page for the Forge. |
| `og-vehicle-forge.png` | Open Graph preview image for social sharing. |
| `index.html` | DiceForge Studios landing page (all tools). |
| `builder.html` | Character Forge — separate tool, character builder for Savage Worlds. |
| `swade-core.js` | Savage Worlds core rules data module (shared across tools). |
| `swade-rules.js` | Rules reference data. |
| `README.md` | Repo documentation. |
| `CHANGELOG_VF_v5_1.md` | Historical changelog from the v4→v5 IP independence rewrite. |
| `ARMOUR_V2_DESIGN_SPEC.md` | Design spec for the current armour slider system. |
| `Vehicle_Forge_Format_Strategy_v1_0.md` | Format strategy for export pipelines (JSON, stat block, FG XML). |
| `functions/api/commit.js` | Cloudflare Pages Function — server-side API for Character Vault canon commits (not Vehicle Forge). |

### Root Files — Other Tools (Not Vehicle Forge)

`adventure-forge.html`, `adventure-vault.html`, `character-vault.html`, `character-db.html`, `npc-manager.html`, `forge-help.html`, `foundry.html`, `pa-forge.html`, `task-vault.html`, `walker-workshop.html`, `vault-help.html` — these are other DiceForge tools, not part of Vehicle Forge.

Supporting: `ammaria.js`, `encoding-fix.js`, `marked.min.js`, `tool-navigation.js`, `vault-integration.js`, `tribute-lands.css`, `vault-common.css`, `adventures.json`, `task-vault-data.json`, `enrich_vehicles.py`.

### Directories

| Directory | Contents |
|-----------|----------|
| `packs/` | 53 `.vfx` extension packs + matching `.cvf.json` source files. 13 family folders (00–12). |
| `v5.0/` | **Archive.** Previous v5.0 build (`combat-vehicle-forge.html`) and legacy data files. Not live. |
| `archive/v4.0/` | **Archive.** Previous v4.0 build, old supplements, old presets. Not live. |

### DOCX Files (Root)

| File | Contents |
|------|----------|
| `Vehicle_Forge_Companion_Guide_v7_1.docx` | Legacy Word version of the guide (superseded by PDF). |
| `Vehicle_Forge_Release_Schedule_v2_0.docx` | Pack release schedule and commercial projections. |

---

## 3. The Six Sliders — Core Formulas

Every vehicle is defined by Size (which sets the frame) plus five adjustment sliders. The formulas below are extracted verbatim from `vehicle-forge.html`.

### Frame (derived from Size)

```
Base Toughness = 5 + Size
Mod Slots = floor(Size × 2.5), minimum 3
Cost Base = 1000 × Size²
```

| Category | Size | Base Handling | Wounds | Base Crew |
|----------|------|---------------|--------|-----------|
| Light | 1–3 | +1 | 3 | 1 |
| Medium | 4–7 | 0 | 4 | 1 |
| Heavy | 8–11 | −1 | 5 | 5 |
| Super-Heavy | 12–20 | −2 | 6 | 20 |
| Capital | 21–25 | −3 | 7 | 100 |
| Titan | 26+ | −4 | 8 | 500 |

### Toughness Slider (toughLevel: −5 to +5)

```
Structural = max(1, (5 + Size) + toughLevel × toughStep)
toughStep = max(1, round(Size / 4) + 1)
```

### Armour Slider (armourLevel: −5 to +5)

```
Armour = max(0, armourBase + armourLevel × armourStep)
Total Toughness = Structural + Armour
```

`armourBase` and `armourStep` are lookup tables indexed by Size and locomotion group (ground/walker, water, air). These tables were hand-tuned to produce SWADE-compatible armour values across all vehicle types. The full tables are in the source code — they are too large to reproduce here but follow the pattern: larger vehicles and ground vehicles have higher base armour and larger steps.

### Speed Slider (speedLevel: −5 to +5)

```
Speed = max(1, locoBaseSpeed + speedLevel)
```

Base speeds by locomotion: Sail 2, Tracked 3, Water Propeller 3, Wheeled 4, Water Jet 4, Hover 5, Multileg 5, Bipedal 6, VTOL 7, Turboprop 10, Jet 12.

Speed is an abstract rating, not MPH. It represents relative positioning within locomotion groups for chase scenes and pursuits.

### Handling Slider (handlingLevel: −5 to +5)

```
Handling = frameBaseHandling + handlingLevel
```

### Wounds Slider (woundsLevel: −3 to +2)

```
Wounds = max(1, frameBaseWounds + woundsLevel)
```

### Design Decision: Sliders vs Slot-Buying

The Science Fiction Companion uses mod slots to purchase Toughness and Armour — each point costs slots. Vehicle Forge uses **free sliders** for stats, reserving mod slots entirely for equipment (weapons, sensors, countermeasures, crew facilities). This is a deliberate design choice:

- It keeps the mod slot budget focused on interesting choices, not stat-buying bookkeeping.
- It means Vehicle Forge mod slot counts will always be **lower** than SFC equivalents for the same Size — this is correct by design.
- It makes the tool genuinely original IP rather than a reproduction of SFC mechanics.
- A Size 8 tank gets 20 mod slots in the Forge vs 50+ in SFC, but achieves the same final stats because our sliders handle what their slots handle.

---

## 4. Content Catalogue

### Weapons: 111

Seven technology eras: Ancient (8), Medieval (8), Black Powder (8), Industrial (11), Modern (14), Future (40), Advanced (22). Each weapon has damage, AP, range, RoF, minimum Size, mod cost, and notes. Users can also create custom weapons stored in `localStorage`.

### Modifications: 41

Eight categories: Drawbacks (8), Core Systems (7), Defensive Systems (7), Offensive Systems (2), Locomotion & Power (8), Personnel (5), Structural (2), Walker Systems (2). Drawbacks have negative mod costs (free up slots). Some mods are tiered (can be taken multiple times up to a maximum).

### Special Abilities: 33

Zero mod slot cost. Toggle on/off. Grouped as Mobility, Construction, Combat, Utility, and Quirks. The quirk abilities (Cursed, Haunted, Sentient, Prototype) were designed for the Dread & Ruin supplement but work in any setting.

### Locomotion Types: 11

Wheeled, Tracked, Hover (Ground/Driving); VTOL, Turboprop, Jet (Air/Piloting); Sail, Propeller, Jet (Water/Boating); Bipedal, Multileg (Walker/Piloting). Walkers automatically gain Heavy Armor and unlock Walker Systems mods.

### Weapon Mounts: 3

Pintle (base cost, 180° arc), Fixed Front (half cost rounded up, forward only), Turret (double cost, 360°). Linked weapons: ×2 (+1 damage die, double cost), ×4 (+2 dice, quadruple cost).

---

## 5. The Class System

DiceForge Class provides an at-a-glance combat rating using the same A–Z scale for both vehicles and weapons. Vehicle Class = total Toughness. Weapon Class = average damage + AP. Because both use the same scale, GMs compare them instantly.

| Class | Value Range | SFC Equivalent |
|-------|-------------|----------------|
| A | 0–15 | I |
| B | 16–25 | II |
| C | 26–35 | III |
| D | 36–45 | IV |
| E | 46–55 | V |
| F | 56–65 | VI |
| G | 66–75 | VII |
| H+ | 76+ | — (beyond SFC) |

Each class band has +/− modifiers showing position within the range. The SFC roman numeral equivalent appears in parentheses in every stat block: e.g., "Class C+ (III)".

---

## 6. Core Reference Builds (47)

The tool ships with 47 vehicles from the Savage Worlds core rulebook (pages 83–85), pre-loaded as locked "DF Canon" builds. These were systematically calibrated in February 2026 against the canonical SWADE stat lines.

### Calibration Methodology

For each vehicle, all slider combinations (toughLevel, armourLevel, handlingLevel from −5 to +5) were tested to minimise weighted error: `|T_delta| + 1.5×|A_delta| + 2×|H_delta|`. Speed sliders were calibrated for correct relative ordering within each locomotion group (e.g., B-17 slowest turboprop, Mustang fastest prop).

### Calibration Results

- **47/47 within ±2 Toughness, ±2 Armour, exact Handling**
- Average Toughness error: 0.6
- Average Armour error: 0.5
- 12/47 perfect matches (Toughness, Armour, and Handling all exact)

This accuracy is well within Savage Worlds design tolerances. The tool uses abstract slider positions, not direct stat entry, so ±1 or ±2 is inherent to the system and acceptable.

### Key Reference Vehicles

| Vehicle | Size | Loco | TL | AL | SL | HL | Tool T(A) | Canon T(A) |
|---------|------|------|----|----|----|-----|-----------|-------------|
| M4 Sherman | 8 | Tracked | +1 | −3 | 0 | 0 | 23(7) | 24(8) |
| M1A1 Abrams | 9 | Tracked | +2 | +5 | 0 | 0 | 58(38) | 57(37) |
| Japanese Zero | 6 | Turboprop | −1 | −1 | 1 | 0 | 11(3) | 12(2) |
| F-15 Eagle | 9 | Jet | 0 | −3 | +3 | 0 | 17(3) | 18(4) |
| Learjet | 8 | Jet | −2 | −5 | 0 | +2 | 9(1) | 10(2) |
| PT Boat | 8 | Water Turbo | +1 | −3 | +1 | +1 | 15(2) | 15(2) |

---

## 7. Extension Pack System (.vfx)

### Format

`.vfx` files are JSON with this schema:

```json
{
  "id": "unique-pack-id",
  "name": "Pack Display Name",
  "version": "1.0",
  "publisher": "DiceForge Studios",
  "description": "Pack description",
  "price": "$2.99",
  "weapons": [],
  "mods": [],
  "specials": [],
  "vehicles": [
    {
      "name": "Vehicle Name",
      "desc": "Short description",
      "notes": "GM notes",
      "image": "",
      "size": 8,
      "loco": "tracked",
      "toughLevel": 1,
      "armourLevel": -3,
      "speedLevel": 0,
      "handlingLevel": 0,
      "woundsLevel": 0,
      "mods": {},
      "weapons": [
        {"weaponId": "tank_gun_med", "mount": "turret", "linked": 0}
      ],
      "specials": ["enclosed"]
    }
  ]
}
```

All weapon, mod, and special IDs must reference entries in the tool's built-in data arrays (or custom entries from the same pack's `weapons`/`mods`/`specials` arrays).

### Distribution Pipeline

User buys pack on DriveThruRPG/itch.io → downloads `.vfx` file → drags into Vehicle Forge Extensions panel → vehicles appear in Hangar under DF Canon tab.

### Pack Catalogue (53 packs, 530 vehicles)

| Family | Packs | Vehicles | Theme |
|--------|-------|----------|-------|
| 00 Core Tool | 1 | 47 | SWADE core rulebook reference builds |
| 01 Blood & Thunder | 6 | 53 | Naval warfare across all eras |
| 02 Iron & Steel | 8 | 73 | Armoured ground warfare |
| 03 Talons & Contrails | 5 | 43 | Military aviation |
| 04 Star & Void | 5 | 43 | Science fiction spacecraft |
| 05 Fang & Claw | 5 | 43 | Mechs, walkers, kaiju |
| 06 Sails & Gasbags | 3 | 23 | Fantasy skyships and airships |
| 07 Chrome & Fury | 4 | 33 | Modern vehicles, chases, spy cars |
| 08 Dread & Ruin | 3 | 23 | Horror vehicles (haunted, cursed) |
| 09 Saddle & Fang | 4 | 33 | Creature mounts and living vehicles |
| 10 Rust & Ruin | 3 | 23 | Post-apocalyptic wasteland vehicles |
| 11 Brass & Steam | 3 | 23 | Steampunk and Victorian |
| 12 Wire & Chrome | 3 | 23 | Cyberpunk vehicles |

Each family also has `.cvf.json` source files alongside the `.vfx` files. The `.cvf.json` format is the raw vehicle data; the `.vfx` wraps it with pack metadata and optional custom content definitions.

### Data Integrity

All 53 packs verified: zero broken weapon, mod, special, or locomotion IDs. All reference only built-in tool definitions (no packs currently ship custom weapons/mods/specials).

---

## 8. Export Formats

Three formats from a single source of truth:

| Format | File | Purpose |
|--------|------|---------|
| JSON | `.json` | Native Vehicle Forge format. Backup, batch import/export, sharing. |
| Stat Block | `.txt` | Pinnacle-format plain text. Universal — works everywhere. |
| FG XML | `.xml` | Fantasy Grounds Unity `db.xml` fragments for direct import. |

**Batch Export** saves all vehicles as one JSON file. **Print All** generates printable stat block index cards.

---

## 9. IP Compliance

### Pinnacle Fan Licence

Vehicle Forge operates under the Pinnacle Fan Licence (free products) or SWAG terms (paid products). The tool references the Savage Worlds game system but does not reproduce its rules.

### Key IP Boundaries

- **No SFC mechanics reproduced.** The slot-buying system for Toughness/Armour is SFC's design. Our slider system is original.
- **No SFC mod names.** All 41 modifications use original DiceForge names and descriptions.
- **No protected terminology.** The v4→v5 rewrite removed all SFC-derived content. Roman numeral damage class notation removed. Weapon properties renamed to original or generic military terms.
- **Mod slot counts deliberately differ from SFC** — this is a feature, not a bug. Different accounting, same compatible output.
- **The Class system (A–G) is original.** The SFC equivalents (I–VII) are provided as a convenience mapping, not a reproduction.

### Trademark Attribution

Every export and the manual include: *"This game references the Savage Worlds game system, available from Pinnacle Entertainment Group at www.peginc.com. Savage Worlds and all associated logos and trademarks are copyrights of Pinnacle Entertainment Group. Used with permission. Pinnacle makes no representation or warranty as to the quality, viability, or suitability for purpose of this product."*

Fantasy Grounds and Foundry VTT trademarks also attributed.

---

## 10. Tool Features

| Feature | Status |
|---------|--------|
| 6 core sliders | ✓ |
| 111 weapons across 7 eras | ✓ |
| 41 modifications across 8 categories | ✓ |
| 33 special abilities | ✓ |
| 11 locomotion types | ✓ |
| 3 weapon mount types (Pintle, Fixed, Turret) | ✓ |
| Linked weapons (×2, ×4) | ✓ |
| Custom weapon creation | ✓ |
| DiceForge Class system (A–Z with SFC mapping) | ✓ |
| Vehicle Hangar (save/load/clone/duplicate/delete) | ✓ |
| DF Canon reference builds (47, locked, cloneable) | ✓ |
| 3 export formats (JSON, Stat Block, FG XML) | ✓ |
| Batch export and Print All | ✓ |
| .vfx extension pack system | ✓ |
| Undo/redo (deep stack) | ✓ |
| Vehicle image support (drag-drop) | ✓ |
| Accessibility (text brightness, text size) | ✓ |
| Audio UI feedback (toggleable) | ✓ |
| Welcome banner (first visit) | ✓ |
| Companion Guide PDF (14 pages) | ✓ |
| Cloud sync / account system | ✗ (v2.0 future) |

### Storage Warning

Everything lives in `localStorage`. Cleared cache or new device = lost custom builds. The welcome banner warns users. Batch Export mitigates (export → reimport on new device). A proper cloud backend would elevate the tool but is a v2.0 feature, not a pre-launch blocker.

---

## 11. Assessment

**Overall rating: 9 / 10** (excluding human playtesting)

The missing point is cloud sync. Everything else — the UI, the formulas, the data, the exports, the extensions, the documentation — is production-ready. The 47 core builds are calibrated to ±2 of SWADE canon. The 53 extension packs are verified clean. The manual matches the tool. The legal attribution is correct.

What remains before v1.0 launch:
- Fresh-eyes testing with real users (can't be automated)
- Version bump from v0.8.22 to v1.0 when satisfied
- Optional: OG preview image wired into meta tags (cosmetic)

---

## 12. Changelog

| Date | Commit | Summary |
|------|--------|---------|
| 2026-02-22 | a9acfe7 | Calibrate all 47 core builds against SWADE canon stat lines. Average error: T 0.6, A 0.5. Speed sliders fixed for correct relative ordering. |
| 2026-02-22 | baccd4e | Convert entire 53-pack catalogue from .cvf.json to .vfx extension format. Fix 9 broken weapon/special references. Zero remaining integrity issues. |
| 2026-02-22 | 0074069 | Update Companion Guide PDF: Sherman walkthrough corrected to Size 8 matching SWADE canon and calibrated VFX data. |
| 2026-02-22 | (prior) | VFX rebuild fixing locomotion/specials divergence between .vfx file and database. 47 SWADE core builds with correct schema. |
| 2026-02-22 | (prior) | Product assessment session. Identified slider calibration as priority. Rejected decimal sliders (0.1 steps) — false precision, unnecessary complexity. |
| Earlier | Various | v4→v5 IP independence rewrite. All SFC-derived content removed. New chassis formula, new mod names, new weapon properties. |
| Earlier | Various | v5→v0.8.22 iterative development. Extension pack architecture, Class system, FG XML export, accessibility features, welcome banner. |

---

## 13. Key Design Decisions (Rationale Archive)

### Why sliders, not direct stat entry?
Sliders force proportionate results within size classes. A user can't accidentally create a Size 2 motorcycle with Toughness 50. The system self-balances.

### Why not match SFC mod slot counts?
SFC uses slots for everything including stats. We separate stats (sliders, free) from equipment (slots). Matching their counts would leave dozens of empty slots that serve no purpose in our system. Different accounting, same output.

### Why not 0.1 slider steps for finer control?
Tested and rejected. Current ±2 tolerance is well within Savage Worlds design philosophy. 0.1 steps = 100 positions vs 10 — fiddly UI, invites false precision, engineering cost not justified. Average error of 0.6/0.5 is already negligible at the table.

### Why a single HTML file?
No build tools, no dependencies, no npm. Opens in any browser, works offline, deploys instantly. The entire tool is the file. This matches the Savage Worlds ethos — pick up and play.

### Why localStorage, not a backend?
Keeps the tool free, simple, and privacy-respecting. No accounts means no GDPR concerns, no server costs, no authentication complexity. The tradeoff (data loss on cache clear) is acceptable for a free tool with batch export as mitigation.

### Why abstract Speed ratings, not MPH?
Savage Worlds chase mechanics care about relative speed within locomotion groups, not absolute velocity. A Speed 3 tracked vehicle and a Speed 3 wheeled vehicle have different real-world speeds but behave similarly in pursuit scenes. The abstract rating is mechanically honest.

---

*Up the Irons.*
