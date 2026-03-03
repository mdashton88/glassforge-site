# Vehicle Forge v5.1 — IP Independence Edition

## CHANGELOG from v4.0

### Breaking Changes
- **New Chassis Formula:** `Toughness = 5 + Size`, `Mod Slots = Size × 2.5`
- **Wound Bands** aligned to SWADE canon: Light (1–3) = 3W, Medium (4–7) = 4W, Heavy (8–11) = 5W, Super-Heavy (12–20) = 6W, Capital (21–25) = 7W, Titan (26+) = 8W
- **Weight Class** replaces Vehicle Class: L/M/H/S/C/T instead of I–VII
- **6-tier Armour Technology** replaces 4-tier system: Primitive (+1), Forged (+2), Industrial (+3), Composite (+4), Nanoweave (+6), Exotic (+8)
- **All locomotion speeds shifted down by 1** (motorised types)
- **All mod names and mechanics reworked** — zero SFC-derived content remains

### Mods Renamed/Reworked (51 total)
**Drawbacks** (was "Negative Qualities"):
War-Worn, Unmanned, Open Crew (3 tiers w/ core cover rules), Temperamental, Weak Frame, Gas-Guzzler, Low-Tech, Skeleton Crew, Sluggish, Underpowered, Bone Shaker, Death Trap, Lightweight Build

**Core Systems:**
Machine Intelligence, Enhanced Sensors, Tactical Relay, Signal Rig, Remote Operator, Detection Grid, Sensor Array

**Defensive Systems:**
Hull Plating, Composite Layering, Sloped Armour, Reinforced Frame, Countermeasure Suite, Surge Protection, Crew Escape, Nanorepair System, Deflection Field, Stealth System

**Offensive Systems:**
Gimballed Weapons, Fire Control

**Locomotion & Power:**
Amphibious Kit, Boost Injector, Reserve Tanks, Off-Road Package, Improved Handling, Improved Speed, Fusion Core, High-Performance Engine, Road Vehicle, Submersible, Variable Form

**Personnel:**
Berths, Comfort Upgrade (3 tiers), Troop Bay, Specialist Workshop, Environmental Seal

**Structural & Walker:**
Vehicle Bay, Jump Jets, Dual Cockpit

### Mods Dropped
- Anti-Teleportation (too niche)
- Quantum Link (reserved for Star & Void supplement)

### Weapon Properties
- **Overcharge** — removed entirely
- **Cauterize** → **Clean Burn**
- **Reaction Fire** → **Defensive Fire**
- **Point Defense** — kept (standard military term)
- Roman numeral damage class notation removed

### Canon Validation (v5.1)
Tested against all 44 SWADE core rulebook stock vehicles:
- **Wounds:** 44/44 exact match
- **Handling:** 36/44 within ±1 (82%)
- **Base Toughness:** avg Δ = -0.9 (military vehicles intentionally start lower, armour added via mods)

### IP Compliance
- Zero SFC mod names, descriptions, or mechanics reproduced
- Uses original Glassforge Chassis Formula (not SFC frame table)
- All weapon properties original or generic military terminology
- SWAG attribution notice included
- Tool designed to complement SFC, not replace it

### Known Issues / Next Steps
- Military vehicles need Hull Plating + Reinforced Frame to match canon Toughness (by design)
- Comfort Upgrade tiered cost needs UI testing
- ~~12 supplement .vfx files need updating to v5.1 mod IDs~~ **RESOLVED** 2026-02-23: all packs verified clean
- Companion Guide manual needs rewrite
- ~~300 test vehicle validation pass pending~~ **RESOLVED** 2026-02-23: 594 vehicles audited, 0 broken refs, 0 stat mismatches. See DATA_GOVERNANCE.md audit log.
