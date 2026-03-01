# Vehicle Forge Armour v2 — Design Specification
## Updated: v0.10.17 — Armour tables recalibrated to Pinnacle civilian baselines (March 2026)

---

## OVERVIEW

Replace the current Armour Technology buttons + Hull Plating/Composite Layering/Reinforced Frame
mods with two intuitive sliders plus overflow buttons.

**Design Philosophy:** Match the weapon UX — see it, adjust it, done. No material descriptions,
no tech tiers. Labels describe relative protection, not construction. The fiction is the GM's.

---

## TWO SLIDERS

### 1. Toughness Slider
- Controls structural mass/solidity (the non-armour portion of total Toughness)
- Range: -5 to +5 with overflow +/- buttons
- Base (position 0) = Size + 5 (universal across domains)
- Step size = max(1, round(Size / 4) + 1)
- Labels: Fragile / Flimsy / Lightweight / Light / Slightly Light / **Standard** / Sturdy / Robust / Very Tough / Extremely Tough / Ironclad
- Overflow: "Ironclad +1", "Ironclad +2" etc.

### 2. Armour Slider
- Controls protective plating (the parenthetical value, what AP reduces)
- Range: -5 to +5 with overflow +/- buttons
- Base and step are DOMAIN-AWARE (keyed off locomotion group)
- Labels: Unprotected / Minimal / Bare Frame / Light Skin / Thin Shell / **Civilian** / Light Military / Medium Military / Heavy Military / Advanced / Top-Tier
- Overflow: "Maximum +1", "Maximum +2" etc. (like d12+X)

---

## DOMAIN-AWARE ARMOUR BASELINES

### Ground / Walker
Base = civilian standard from Vehicle Guide. Slider 0 = civilian, +1-2 = WW2 military, +4-5 = modern MBT.

| Size | Base | Step | -5 | 0 | +5 | Notes |
|------|------|------|----|---|-----|-------|
| ≤3 | 1 | 1 | 0 | 1 | 6 | Bikes, carriages |
| 4 | 2 | 1 | 0 | 2 | 7 | Cars, light trucks |
| 5 | 2 | 2 | 0 | 2 | 12 | SUVs |
| 6 | 2 | 3 | 0 | 2 | 17 | APCs at +1 |
| 7 | 2 | 4 | 0 | 2 | 22 | WW2 tanks at +1-2 |
| 8 | 3 | 6 | 0 | 3 | 33 | Sherman +1, Tiger +2 |
| 9 | 3 | 7 | 0 | 3 | 38 | Abrams at +5 |
| 10 | 3 | 8 | 0 | 3 | 43 | |
| 11 | 3 | 9 | 0 | 3 | 48 | |
| 12-14 | 4 | 10-12 | 0 | 4 | 54-64 | |

Full table:
```
Base: sz<=3: 1, sz<=7: 2, sz<=11: 3, sz>=12: 4
Step: sz<=4: 1, sz=5: 2, sz=6: 3, sz=7: 4, sz=8: 6, sz=9: 7,
      sz=10: 8, sz=11: 9, sz=12: 10, sz=13: 11, sz>=14: 12
```

### Water
Base = civilian standard from Vehicle Guide. Slider 0 = civilian, +1-2 = military patrol, +3 = belt-armoured warship.

| Size | Base | Step | -5 | 0 | +5 | Notes |
|------|------|------|----|---|-----|-------|
| ≤3 | 1 | 1 | 0 | 1 | 6 | Kayaks, dinghies |
| 4-11 | 2 | 1 | 0 | 2 | 7 | Boats, yachts |
| 12-16 | 3 | 1 | 0 | 3 | 8 | Trawlers, frigates |
| 17 | 3 | 5 | 0 | 3 | 28 | Belt armour ships |
| 20 | 3 | 11 | 0 | 3 | 58 | Cruisers |
| 25 | 3 | 14 | 0 | 3 | 73 | Super carriers |

Full table:
```
Base: sz<=3: 1, sz<=11: 2, sz>=12: 3
Step: sz<=16: 1, sz=17: 5, sz=18: 6, sz=19: 8, sz=20: 11,
      sz=21: 12, sz=22: 12, sz=23: 13, sz=24: 14, sz=25: 14
```

### Space
| Size | Base | Step |
|------|------|------|
| 16 | 10 | 2 |
| 17-25 | 20-50 | 4 |

Full table:
```
{16:10, 17:20, 18:24, 19:32, 20:40, 21:42, 22:44, 23:46, 24:48, 25:50}
Step: sz<=16: 2, sz>16: 4
```

---

## TOUGHNESS DISPLAY FORMAT

**Savage Worlds canonical format:** Total (Armour)
- "Toughness: 32 (16)" = total 32, of which 16 is Armour
- Total = Structural + Armour
- Structural = struct_base + (t_pos × struct_step)
- Armour = arm_base + (a_pos × arm_step)
- AP reduces Armour only, never structural

**Current tool is BACKWARDS** — displays base (total). Must fix.

---

## CANON VALIDATION

94.1% accuracy within 2 points across 102 canon vehicles.
Only 6 vehicles need overflow beyond ±5 (max overflow: +10 for SFC Battleship).

Key mappings:
- Car → Toughness Standard, Armour Modest
- Sherman → Toughness Sturdy, Armour Standard
- Abrams → Toughness Robust, Armour Maximum
- SFC MBT → Toughness Robust, Armour Heavy
- SFC Destroyer → Toughness Sturdy, Armour Maximum +3
- SFC Battleship → Toughness Standard, Armour Maximum +5
- Future MBT → Toughness Robust, Armour Maximum

---

## WHAT TO REMOVE

- Armour Technology buttons (Primitive/Forged/Industrial/Composite/Nanoweave/Exotic)
- AT_INFO data structure
- Hull Plating mod
- Composite Layering mod
- Reinforced Frame mod
- All armourTech references in state/save/load/export/undo/redo

---

## WHAT TO ADD

- Toughness slider (HTML range input -5 to +5)
- Toughness +/- overflow buttons
- Armour slider (HTML range input -5 to +5)
- Armour +/- overflow buttons
- Label display for each slider (updates live)
- Description display for each slider (contextual guidance)
- Armour bonus display showing actual value
- Domain-aware base/step calculation functions
- Updated calcArmor() using new system
- Updated calcTough() using new system (or new calcStructural)
- Fixed display format: Total (Armour) not Base (Total)

---

## STATE CHANGES

Replace `S.armourTech` (integer 0-5) with:
- `S.toughLevel` (integer, default 0, no min/max — overflow allowed)
- `S.armourLevel` (integer, default 0, no min/max — overflow allowed)

---

## OPEN QUESTION (Next Session)

Does overflow beyond +5 consume mod slots? Options:
1. All slider positions are free, overflow costs mods
2. Everything is free (simplest)
3. Positions beyond 0 cost progressively more mods
4. Only extreme overflow (beyond +7?) costs mods

---

## COST SCALING (To Design)

How does armour level affect vehicle cost? Options:
1. Cost multiplier per position (current AT system approach)
2. Flat cost per step
3. Escalating cost (each additional step costs more)
4. Free within slider, cost only on overflow

---

## FILES TO MODIFY

- combat-vehicle-forge.html (main tool)
- VF-Companion-Guide (manual — needs v7 update)

