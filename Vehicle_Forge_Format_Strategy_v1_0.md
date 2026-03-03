# Vehicle Forge — Format Strategy & Documentation Architecture v1.0

**Glassforge Games Ltd.**
**February 2026**

---

## The Problem We're Solving

A GM buys our Chase Starter pack on DriveThruRPG. They run Fantasy Grounds. If they can't use the vehicles in FG without a separate conversion step, we've wasted their money and their time. They leave a one-star review. They never buy from us again.

The Vehicle Forge must produce output that works *everywhere* Savage Worlds is played — or it fails as a product.

---

## The Format Landscape

There is no universal vehicle exchange format in the Savage Worlds ecosystem. Each platform uses its own structure:

**Fantasy Grounds Unity** stores data as XML inside .mod files (ZIP archives containing db.xml and definition.xml). The SWADE ruleset expects vehicles in specific data paths with typed fields. We have documented this format comprehensively in FG SWADE Module Reference v4.0 (Document 506).

**Foundry VTT** stores actors and items as JSON objects internally. The SWADE system module defines its own schema. The community SWADE Stat Block Importer accepts Pinnacle-format plain text stat blocks pasted from the clipboard.

**Savaged.us** (the main SW character builder) exports JSON that Foundry can import directly.

**Roll20** has no structured import for Savage Worlds vehicles. Manual entry only.

**The universal interchange format** is the Pinnacle-format text stat block — the plain text format used in every printed Savage Worlds product since 2003. Every GM recognises it. Every VTT importer that exists parses it. It's the lingua franca.

---

## Our Format Strategy

### Canonical Data Format: JSON

Our internal data format is JSON. The .cvf.json files and the tool's localStorage both use this format. It is our source of truth. All other formats are generated from it.

### Export Formats (from the Forge tool)

The Vehicle Forge exports to three formats. All three generate from the same canonical JSON data with zero loss.

| Format | Extension | Target | Status |
|--------|-----------|--------|--------|
| Vehicle Forge JSON | .cvf.json | Vehicle Forge tool, developers | Implemented |
| Pinnacle Text Stat Block | .txt | Universal — works everywhere | To build |
| Fantasy Grounds XML | .xml | Fantasy Grounds Unity direct import | To build |

The Pinnacle text stat block is the priority export because it works with *everything* — Foundry's stat block importer, manual entry on Roll20, printing on index cards, pasting into chat. Any GM on any platform can use it immediately.

The Fantasy Grounds XML export generates a complete, valid db.xml fragment that can be pasted into any FG campaign or module. This is a significant competitive advantage — most SWAG publishers sell separate FG conversions at additional cost.

### Product Distribution

Each paid expansion pack ships as a ZIP containing:

```
Blood_Thunder_Naval_Starter/
  Blood_Thunder_Naval_Starter.vfx          ← Installs into Vehicle Forge
  Blood_Thunder_Naval_Starter_FG.xml       ← Paste into FG campaign db.xml
  Blood_Thunder_Naval_Starter_Statblocks.txt  ← Universal text format
  README.txt                                ← Format guide + license notice
  LICENSE.txt                               ← Full license text
```

One purchase. Three formats. Zero conversion required on any platform.

The .vfx file remains the Vehicle Forge installation format — it contains our JSON vehicle data plus any weapon/mod extensions the pack requires. The FG XML and stat block files are generated alongside it automatically.

---

## Licensing & IP Compliance

### What We Are

We are a SWAG-published tool and content ecosystem. We create original vehicle stat blocks compatible with the Savage Worlds rule system. We do not reproduce, restate, or explain Savage Worlds rules.

### What We Must Do

**Every product and the tool itself must display the Pinnacle Fan License notice:**

> This game references the Savage Worlds game system, available from Pinnacle Entertainment Group at www.peginc.com. Savage Worlds and all associated logos and trademarks are copyrights of Pinnacle Entertainment Group. Used with permission. Pinnacle makes no representation or warranty as to the quality, viability, or suitability for purpose of this product.

**The SWAG logo must appear on every paid product cover**, legible at thumbnail size. The logo may be resized but not altered.

**Fantasy Grounds compatibility notice** (on any product including FG XML):

> Fantasy Grounds is a trademark of SmiteWorks USA, LLC. This product is not affiliated with or endorsed by SmiteWorks. Vehicle data is provided in a format compatible with Fantasy Grounds Unity for user convenience.

**Foundry VTT compatibility notice** (on any product referencing Foundry):

> Foundry Virtual Tabletop is a trademark of Foundry Gaming LLC. This product is not affiliated with or endorsed by Foundry Gaming. Stat blocks are provided in standard Pinnacle format compatible with community import tools.

### What We Must Not Do

- Reproduce Savage Worlds rule text verbatim
- Explain mechanics in enough detail to play without the rulebook
- Use the Pinnacle logo without permission (SWAG logo is fine within SWAG)
- Claim official Pinnacle, SmiteWorks, or Foundry Gaming endorsement
- Distribute FG ruleset code, Foundry system code, or any third-party software
- Include content from licensed Pinnacle settings (Deadlands, Rifts, Flash Gordon, etc.)
- Reproduce the Savage Worlds Vehicle Guide's stat tables or text (our stat blocks are original creations using the same public rules framework)

### The Test

Before publishing any product, ask:

*"Does this product make Pinnacle money or cost them money?"*

If a GM buys our Chase Starter and thinks "I need Savage Worlds to use these vehicles" — we've done it right.

If a GM buys our Chase Starter and thinks "I don't need Savage Worlds, these stat blocks are self-explanatory" — we've done it wrong.

### Format-Specific Compliance

**Vehicle Forge JSON (.cvf.json / .vfx):** Contains only our original vehicle definitions. No rules text. No explanations of how stats work. The tool's help panel references rules by name but never reproduces them. Compliant.

**Pinnacle Text Stat Blocks (.txt):** Uses the exact same format as every published Savage Worlds product. We are generating stat blocks for our original vehicles — this is explicitly what SWAG permits. Compliant.

**Fantasy Grounds XML (.xml):** Contains our original vehicle data structured to match FG's expected XML schema. We are not distributing FG's code, ruleset, or copyrighted content — only our own data in a compatible structure. This is identical to what every SWAG publisher with FG support does. Compliant.

---

## Documentation Architecture

### The One-Truth Principle

One document. One URL. One source of truth.

**The Vehicle Forge Companion Guide** is the single authoritative document for the entire product ecosystem. It is hosted as a PDF at a permanent URL that never changes. It updates with every release.

### What Lives Where

| Content | Location | Purpose |
|---------|----------|---------|
| Slider tooltips, "what does this do?" | Built-in help panel | Instant answers mid-session |
| Full manual, tutorials, examples | Companion Guide PDF | Complete reference |
| Product catalogue, pricing | Companion Guide Appendix | Always current |
| Release notes, changelog | Companion Guide Appendix | Version history |
| License notices | Both | Legal compliance |
| Format compatibility matrix | Companion Guide | Export guidance |

### Built-In Help Panel

Stays lightweight. Quick reference only. Every section ends with a link to the relevant Companion Guide section. Contains:

- Slider explanations (one sentence each)
- Weapon category descriptions
- Mod descriptions
- Keyboard shortcuts
- The Pinnacle Fan License notice
- A prominent "Full Manual" button linking to the Companion Guide PDF URL

The help panel **never** duplicates content that belongs in the Companion Guide. If a GM needs more than two paragraphs of explanation, they need the Companion Guide.

### Companion Guide PDF

Hosted at: `https://glassforge.pages.dev/vehicle-forge-manual.pdf`

This URL never changes. The file at this URL updates with every release. The tool links to it. The DTRPG listing links to it. The GitHub README links to it.

**Contents:**

1. Getting Started — tool overview, installation, first build
2. The Six Sliders — complete explanation of every control
3. Weapons & Modifications — full weapon catalogue, mod descriptions
4. Building Vehicles — tutorials by genre (tank, fighter, spaceship, mount)
5. Extensions & Packs — installing .vfx files, managing extensions
6. Export Formats — JSON, FG XML, Pinnacle stat blocks, format matrix
7. Expansion Pack Guide — what each pack contains, upgrade paths
8. One-Sheet Adventures — adventure outlines for each pack
9. License & Credits — Pinnacle notice, FG notice, Foundry notice, Glassforge credits

**Appendix A: Product Catalogue** — auto-updating list of all available packs with prices, vehicle counts, wave status, and DTRPG links

**Appendix B: Release Notes** — version history with dates

**Appendix C: Stat Block Format Reference** — Pinnacle format specification for anyone wanting to create their own vehicles outside the tool

### Update Cadence

The Companion Guide updates whenever:
- A new expansion pack ships
- A new export format is added
- A tool feature changes
- A bug is fixed that affects documented behaviour

The product catalogue appendix updates with every new product release. Because the PDF is hosted at a permanent URL, existing customers always see the latest version.

---

## Implementation Priority

| Priority | Task | Effort |
|----------|------|--------|
| 1 | Add Pinnacle stat block export to tool | 2 hours |
| 2 | Add FG XML export to tool | 4 hours |
| 3 | Add "Full Manual" link to tool header | 15 minutes |
| 4 | Restructure built-in help as quick reference | 1 hour |
| 5 | Build Companion Guide PDF structure | 3 hours |
| 6 | Generate multi-format pack bundles | 2 hours |
| 7 | Update all README files | 1 hour |

Total: approximately 13 hours across multiple sessions.

---

## Summary

The Vehicle Forge ships vehicles in three formats because GMs play on different platforms. We respect Pinnacle's IP by creating original content within their licensing framework. We respect SmiteWorks' and Foundry Gaming's trademarks by providing compatibility without claiming endorsement. We respect our customers' time by eliminating format conversion entirely.

One tool. Three formats. Every platform. Zero friction.

---

*Glassforge Games Ltd.*
*February 2026*
