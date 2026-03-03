# Vehicle Forge — Expansion Pack Catalogue

**Publisher:** Glassforge Games Ltd.
**System:** Savage Worlds Adventure Edition
**Tool:** Vehicle Forge (free)
**Format:** .cvf.json batch import files

---

## Overview

This directory contains the complete Vehicle Forge expansion pack catalogue — ~510 vehicles across 54 products covering every genre from ancient war chariots to capital ships of the void. Each .cvf.json file is a self-contained batch import that loads directly into the Vehicle Forge tool.

## Release Waves

| Wave | Products | Vehicles | Timeline | Status |
|------|----------|----------|----------|--------|
| **Wave 1: Launch** | 20 | ~264 | Month 1-2 | Ready — zero .vfx work |
| **Wave 2: Ancient/BP** | 5 | 50 | Month 3-4 | Needs ~15 weapon definitions |
| **Wave 3: Naval + Sups** | 4 | 19 | Month 5-6 | Needs naval .vfx |
| **Wave 4+: Deep Packs** | 12+ | 150+ | Month 7+ | Ships with parent supplements |

## Folder Structure

| Folder | Supplement Family | Starter | Expansion Packs | Total Vehicles |
|--------|------------------|---------|-----------------|----------------|
| 00_Core_Tool | — | — | Core Reference Builds | 64 |
| 01_Blood_and_Thunder | Naval warfare across history | Naval Starter | Age of Sail, Viking Raiders, Napoleonic Navy, WWII Naval | 53 |
| 02_Iron_and_Steel | Armoured ground war | — | Ancient, Medieval, WWI, WWII×2, Cold War, Modern | 73 |
| 03_Talons_and_Contrails | Air combat across history | — | WWI Aces, WWII Air, Vietnam, Modern Air | 43 |
| 04_Star_and_Void | Spacecraft and fleet ops | Sci-Fi Starter | Patrol Fleet, Battle Fleet, Capital Ships | 43 |
| 05_Fang_and_Claw | Walkers and mechs | Mech Starter | Light Lance, Heavy Lance, Kaiju Defence | 43 |
| 06_Sails_and_Gasbags | Fantasy airships | Skyship Starter | Fantasy Skyfleet | 23 |
| 07_Chrome_and_Fury | Chases and pursuit | Chase Starter | Wasteland Fleet, Spy Vehicles | 33 |
| 08_Dread_and_Ruin | Horror vehicles | Horror Starter | Haunted Vehicles | 23 |
| 09_Saddle_and_Fang | Mounts and beasts | Mount Starter | Fantasy Mounts, Dinosaur Mounts | 33 |
| 10_Rust_and_Ruin | Post-apocalyptic | Wasteland Starter | Wasteland Survivors | 23 |
| 11_Brass_and_Steam | Steampunk | Steampunk Starter | Victorian Arsenal | 23 |
| 12_Wire_and_Chrome | Cyberpunk | Cyberpunk Starter | Cyberpunk Fleet | 23 |

## Starter Pack Model

Genre Starter packs use existing core tool weapons only — no .vfx extensions required. They provide basic stat blocks that let GMs run sessions immediately. When the full parent supplement ships, it adds genre-specific mechanics (crew stations, pilot bonding, possession rules, etc.) and the deep expansion packs deliver vehicles built to use those mechanics.

Each Starter validates demand for its parent supplement before that supplement is written.

## File Format

Each .cvf.json file contains:
- `formatVersion`: Schema version (currently "1.0")
- `packName`: Human-readable product name
- `packId`: Internal identifier
- `price`: Retail price
- `vehicleCount`: Number of vehicles in the pack
- `publisher`: Glassforge Games Ltd.
- `note`: (Starters only) Upgrade path description
- `vehicles[]`: Array of vehicle definitions

## Pricing

- **Core Tool:** Free
- **Starter Packs:** $2.99 each
- **Expansion Packs:** $2.99-$3.99 each
- **Theatre Supplements:** $4.99-$7.99 each (includes rules + .vfx + 3 pre-built vehicles)

## One-Sheet Adventures

Each expansion pack includes a free one-sheet adventure PDF that showcases 3-5 vehicles from the pack. See individual folder READMEs for adventure outlines.

---

*Vehicle Forge Release Schedule v2.0 — February 2026*
*Glassforge Games Ltd.*
