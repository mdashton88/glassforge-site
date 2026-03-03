# Vehicle Forge v4.0 — Frozen Archive

**Archived:** 2026-02-21
**Status:** Complete, cohesive bundle. Do not modify.

This folder preserves the fully developed v4.0 release of the Glassforge Vehicle Forge
and all associated documentation. Everything in this archive worked together as a
tested, coherent system.

## Contents

### Core Application
- `Vehicle_Forge_v4_0.html` — The complete Vehicle Forge v4.0 single-page application

### Companion Guide
- `Vehicle_Forge_Companion_Guide_v2_0.docx` — Full reference manual covering vehicle
  creation, the weight class system, weapon tables, and genre guidance

### Genre Supplements (12)
Each supplement provides era-specific vehicle catalogues, weapons, modifications,
and Game Master guidance for a specific setting or genre.

| Supplement | Genre | Focus |
|---|---|---|
| Blood & Thunder | Ancient/Medieval | Chariots, war wagons, siege engines |
| Brass & Steam | Steampunk/Victorian | Steam tanks, airships, clockwork |
| Chrome & Fury | Modern Military | Tanks, APCs, jets, helicopters |
| Dread & Ruin | Post-Apocalyptic | Improvised vehicles, wasteland rigs |
| Fang & Claw | Monster Hunting | Beast-hunting vehicles, creature mounts |
| Iron & Steel | World War II | WW2 tanks, fighters, warships |
| Rust & Ruin | Cyberpunk/Near-Future | Hover vehicles, drones, cyber-rigs |
| Saddle & Fang | Weird West | Steam wagons, cavalry, fantastical mounts |
| Sails & Gasbags | Naval/Airship | Age of Sail, zeppelins, flying ships |
| Star & Void | Space Opera | Starfighters, capital ships, space stations |
| Talons & Contrails | Aviation | WW1 to modern air combat |
| Wire & Chrome | Cyberpunk Vehicles | Street racing, corporate transports |

### Vehicle Presets (.vfx files)
Pre-built vehicle configurations for each genre supplement, importable directly
into Vehicle Forge v4.0.

### Reference
- `warhammer-40k-titans-warhound-legio-mortis.jpg` — Titan reference image

## Formula (v4.0)
```
Base Toughness = ceil((5 + Size + locoMod) × frameMult)
Total Toughness = Base + Armour

frameMult: civilian = 1.0, rugged = 1.25, military = 1.5
locoMod:   ground/hover = 0, air = -1, water = -2
```

## Notes
- v4.0 used the original weight class system (Roman numerals I-VII)
- v5.x introduced the Threat Grade system (A-F letters) and recalibrated
  the Toughness formula against SWADE canon vehicles
- All twelve supplements and the Companion Guide were written for the v4.0 formula
- The .vfx preset files are JSON format with a .vfx extension
