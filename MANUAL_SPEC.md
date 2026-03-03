# Vehicle Forge Companion Guide — Build Specification
# ══════════════════════════════════════════════════════
# This file is the SINGLE SOURCE OF TRUTH for what the PDF manual must contain.
# Read this BEFORE regenerating the manual. Every requirement listed here
# must survive into the next build. If you're adding a feature, add it here first.

## BRAND & STYLING

- **Colour scheme**: Match vehicle-forge.html :root variables
  - Accent gold: #C4A44A (headings, rules, bullets, table headers)
  - Text: #E4D8B8 (warm parchment for body copy)
  - Text dim: #A89868 (notes, legal, footer)
  - Text bright: #F5EDD8 (emphasis, mono blocks)
- **Background**: PRINT-FRIENDLY — use white/off-white (#FAFAF5) background
  with dark text. Gold accents on headings, rules, and table headers.
  Dark backgrounds look great on screen but nobody prints them.
- **Fonts**: Helvetica family (always available in ReportLab).
  Headings: Helvetica-Bold. Body: Helvetica. Notes: Helvetica-Oblique.
- **Page footer**: Gold rule, version string, page number, "GLASSFORGE GAMES" centred
- **Gold horizontal rules** between chapter title and content

## HYPERLINKS — CRITICAL

All URLs must be clickable hyperlinks, not just styled text:
- Glassforge website URL on title page and final page
- www.peginc.com in Savage Worlds licence text
- Any other URLs referenced

ReportLab example:
```python
from reportlab.lib.colors import HexColor
# In a Paragraph:
'<a href="https://url" color="#C4A44A">display text</a>'
# Or on canvas:
canvas.linkURL("https://url", (x1, y1, x2, y2))
```

## CONTENT REQUIREMENTS

### Title Page
- "GLASSFORGE GAMES" brand line
- "Vehicle Forge" title in gold
- "Companion Guide" subtitle
- Version string (pull from vehicle-forge.html header)
- Summary: tool description, reference build count, weapon count
- DO NOT claim pack counts or vehicle counts for unreleased content
- Savage Worlds licence text
- "You will need the Savage Worlds core rules" in bold
- Glassforge copyright

### Table of Contents
1. Getting Started
2. The Six Sliders
3. Weapons
4. Modifications Reference
5. The Class System
6. Locomotion Types
7. Reference Builds
8. Export Formats
9. Extension Packs
10. Building Vehicles: Walkthroughs
A. Weapon Reference Tables
B. Keyboard Shortcuts
C. Licence and Credits

### Ch 1: Getting Started
- What the tool is, Fast! Furious! Fun! philosophy
- What you need (browser + SWADE rules)
- Quick start (6 steps)

### Ch 2: The Six Sliders
- Each slider: name, what it does, frame increments
- MPH Override explanation

### Ch 3: Weapons
- Count, era list, filtering
- Category overview (bullets with gold accent)
- Reference to Appendix A

### Ch 4: Modifications Reference
- Full table of all 41 mods across 8 categories
- Each mod: name and effect description
- Categories: Drawbacks, Core Systems, Defensive, Offensive,
  Locomotion & Power, Personnel, Structural, Walker Systems
- This is 100% original Glassforge content

### Ch 5: Class System
- A-G classification table
- Size ranges, frame categories, examples

### Ch 6: Locomotion Types
- All 11 types with speed ranges and notes

### Ch 7: Reference Builds
- What they are, how to use them
- DO NOT reproduce stat lines in the manual (IP risk)
- Direct users to the tool itself

### Ch 8: Export Formats
- Pinnacle Stat Block, Fantasy Grounds XML, JSON
- FG trademark notice

### Ch 9: Extension Packs
- HEDGE as planned/future content
- Pack family names and themes
- "Availability confirmed at launch" disclaimer

### Ch 10: Building Vehicles — Walkthroughs
TWO VIGNETTES, each told as a narrative of someone designing/building:

**Vignette 1: WW2 Medium Tank**
- Character: A wartime engineer or commander specifying requirements
- Explain WHY each choice is made:
  - Size 7 because a 30-tonne tank is Large frame
  - Tracked because it's a tank
  - Toughness/Armour choices reference real 50-80mm armour plates
  - Speed: "She needs to keep up with the infantry advance — 30 MPH"
  - 75mm gun because that was the standard Allied medium calibre
  - Heavy Armour because small arms bounce off tanks
- Show the resulting stat block
- Compare to reference build

**Vignette 2: Sci-fi recognisable archetype**
- Build something everyone knows: an Imperial walker, light freighter,
  or combat mech — but described generically
- Character: A sponsor, commander, or engineer commissioning the vehicle
- Walk through EVERY choice with reasoning
- Show how the tool handles sci-fi weapons and mods
- Final stat block

Both vignettes should:
- Be written as narrative prose, not dry instructions
- Show the character USING VEHICLE FORGE — sliders moving, stat block
  updating, mod counter ticking down, weapon panel filtering, Export button
- Explain the REASONING behind every slider position
- Reference real-world knowledge or genre conventions
- Show iteration: start at one Size, discover a problem, adjust
- End with a complete stat block via the Export button

IP/LICENCE BOUNDARY (CRITICAL):
- SHOW: Vehicle Forge's UI outputs (Toughness 23, mod slots remaining, etc.)
- SHOW: Characters referencing their knowledge of the rules ("he knows
  from the core rules what that means")
- SHOW: Weapon stats from our tool's weapon panel (these are our data)
- NEVER TEACH: How Savage Worlds mechanics work at the table
- NEVER EXPLAIN: What Toughness does, how damage rolls resolve, how AP
  reduces armour, what Wounds mean mechanically
- PRINCIPLE: "Show outputs, reference capabilities, never teach mechanics"
- The reader who owns Savage Worlds nods in recognition
- The reader who doesn't thinks "I need those rules" — which is exactly
  what Pinnacle's licence is designed to achieve

### Appendix A: Weapon Reference Tables
- All weapons grouped by era
- Deduplicated (some IDs share stats)
- Columns: Weapon, Range, Damage, AP, RoF

### Appendix B: Keyboard Shortcuts
- Standard shortcut table

### Appendix C: Licence and Credits
- Savage Worlds licence (full Pinnacle text)
- Fantasy Grounds trademark
- Foundry VTT trademark
- Glassforge copyright with IP compliance statement
- Clickable URL to the tool

## THINGS THE MANUAL MUST NOT DO

- Reproduce vehicle stat lines in tabular form (IP risk)
- Claim unreleased content exists
- Reproduce rules text from Savage Worlds
- Use dark/black background (print hostile)
- Lose hyperlinks between rebuilds
- Use manufacturer-specific vehicle names

## AUTO-GENERATION

The manual should be regeneratable from `build_manual.py` at any time.
It pulls live data from vehicle-forge.html for:
- Weapon tables (WEAPONS array)
- Modification tables (MODS array)
- Version string
- Reference build count (CANON_BUILDS length)
