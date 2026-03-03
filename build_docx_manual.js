const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, ExternalHyperlink,
        TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, PageBreak, TabStopType, PositionalTab,
        PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,
        SectionType } = require('docx');

// ═══════════════════════════════════════════════════
// BRAND COLOURS matching original docx
// ═══════════════════════════════════════════════════
const GOLD = "9A7B2C";
const DARK = "1A1816";
const BODY = "4A4035";
const DIM = "8A7A60";
const TABLE_HEADER_BG = "2A2520";
const TABLE_ALT_BG = "F8F5F0";
const TABLE_BORDER = "D4C8A8";

// ═══════════════════════════════════════════════════
// LOAD LIVE DATA
// ═══════════════════════════════════════════════════
const html = fs.readFileSync('vehicle-forge.html', 'utf-8');
const verMatch = html.match(/v(0\.\d+\.\d+)/);
const VERSION = verMatch ? verMatch[0] : 'v0.10';

// Extract weapons
const wChunkStart = html.indexOf('var WEAPONS=[');
const wChunkEnd = html.indexOf('];', wChunkStart) + 2;
const wChunk = html.slice(wChunkStart, wChunkEnd);
const weaponRe = /\{id:'([^']+)',name:'([^']+)',cat:'([^']+)',era:'([^']+)',range:'([^']+)',damage:'([^']+)',ap:(\d+),rof:(\d+),shots:(\d+),minSize:(-?\d+),mods:(\d+),cost:(\d+),notes:'([^']*)',desc:'([^']*)'/g;
let wm, weapons = [];
while ((wm = weaponRe.exec(wChunk)) !== null) {
    weapons.push({name:wm[2],cat:wm[3],era:wm[4],range:wm[5],damage:wm[6],ap:wm[7],rof:wm[8],mods:wm[11],notes:wm[13]});
}

// Dedup by era
const eraOrder = ['ancient','medieval','blackpowder','industrial','modern','future','advanced'];
const eraNames = {ancient:'Ancient',medieval:'Medieval',blackpowder:'Blackpowder',industrial:'Industrial',modern:'Modern',future:'Future',advanced:'Advanced'};
const eraDescs = {
    ancient:'Pre-gunpowder weapons: siege engines, rams, fire siphons, ranged batteries. Bronze Age through late Roman.',
    medieval:'Improved siege engines, trebuchets, and defensive weapons. Dark Ages through late medieval.',
    blackpowder:'Gunpowder weapons from the Age of Sail through Napoleonic wars. Smoothbore cannon, carronades, mortars.',
    industrial:'Late 19th century through WWII. The transition from muscle to machine. Machine guns, tank guns, autocannons.',
    modern:'Cold War through present day. Guided weapons, electronic warfare, precision strike.',
    future:'Science fiction. The largest catalogue at 39 weapons. Everything from infantry-scale machine guns to capital-ship lasers.',
    advanced:'Far-future and exotic technology. Railguns, particle beams, mass drivers. Twenty-two weapons across seven categories.'
};
let eraWeapons = {};
weapons.forEach(w => {
    if (!eraWeapons[w.era]) eraWeapons[w.era] = [];
    let key = w.name + w.damage;
    if (!eraWeapons[w.era].some(x => x.name + x.damage === key)) eraWeapons[w.era].push(w);
});
const WEAPON_COUNT = new Set(weapons.map(w => w.name + w.era)).size;

// Extract mods - flexible per-field regex (handles variable field order)
const mChunkStart = html.indexOf('var MODS=[');
const mChunkEnd = html.indexOf('];', mChunkStart) + 2;
const mChunk = html.slice(mChunkStart, mChunkEnd);
let mods = [];
const modBlockRe = /\{([^}]+)\}/g;
let mb;
while ((mb = modBlockRe.exec(mChunk)) !== null) {
    const b = mb[1];
    const idM = b.match(/id:'([^']+)'/);
    const nameM = b.match(/name:'([^']+)'/);
    const catM = b.match(/cat:'([^']+)'/);
    const maxM = b.match(/max:([^,]+)/);
    const modsM = b.match(/\bmods:([^,]+)/);
    const descM = b.match(/desc:'([^']*)'/);
    if (idM && nameM && catM) {
        mods.push({
            name: nameM[1], cat: catM[1],
            max: maxM ? maxM[1].replace(/'/g,'') : '1',
            mods: modsM ? modsM[1].replace(/'/g,'') : '0',
            desc: descM ? descM[1] : ''
        });
    }
}
const MOD_COUNT = mods.length;

// Group mods by category  
let modCats = {};
mods.forEach(m => { if (!modCats[m.cat]) modCats[m.cat] = []; modCats[m.cat].push(m); });

// Build count
const bcMatch = html.slice(html.indexOf('CANON_BUILDS=['), html.indexOf('];', html.indexOf('CANON_BUILDS=[')));
const BUILD_COUNT = (bcMatch.match(/name:"/g) || []).length;

console.log(`Data: ${VERSION}, ${WEAPON_COUNT} weapons, ${MOD_COUNT} mods, ${BUILD_COUNT} builds`);

// ═══════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════
const border = { style: BorderStyle.SINGLE, size: 1, color: TABLE_BORDER };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function goldRule() {
    return new Paragraph({ 
        spacing: { before: 60, after: 120 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 1 } },
        children: [] 
    });
}

function body(text, opts = {}) {
    return new Paragraph({
        spacing: { after: 160 },
        ...opts,
        children: [new TextRun({ text, font: "Palatino Linotype", size: 21, color: BODY })]
    });
}

function bodyBold(label, text) {
    return new Paragraph({
        spacing: { after: 160 },
        children: [
            new TextRun({ text: label, font: "Palatino Linotype", size: 21, color: BODY, bold: true }),
            new TextRun({ text, font: "Palatino Linotype", size: 21, color: BODY })
        ]
    });
}

function bodyRuns(runs) {
    return new Paragraph({
        spacing: { after: 160 },
        children: runs.map(r => new TextRun({ font: "Palatino Linotype", size: 21, color: BODY, ...r }))
    });
}

function chapterQuote(text) {
    return new Paragraph({
        spacing: { before: 240, after: 240 },
        alignment: AlignmentType.LEFT,
        children: [new TextRun({ text: `\u201C${text}\u201D`, font: "Palatino Linotype", size: 24, italics: true, color: GOLD })]
    });
}

function subheading(text) {
    return new Paragraph({
        spacing: { before: 300, after: 140 },
        children: [new TextRun({ text, font: "Cinzel", size: 24, bold: true, color: GOLD })]
    });
}

function tip(text) {
    return new Paragraph({
        spacing: { before: 80, after: 160 },
        indent: { left: 360, right: 360 },
        children: [
            new TextRun({ text: "TIP: ", font: "Palatino Linotype", size: 20, bold: true, color: GOLD }),
            new TextRun({ text, font: "Palatino Linotype", size: 20, italics: true, color: DIM })
        ]
    });
}

function statBlock(lines) {
    return lines.map(line => new Paragraph({
        spacing: { after: 40 },
        shading: { fill: TABLE_ALT_BG, type: ShadingType.CLEAR },
        indent: { left: 240, right: 240 },
        children: [new TextRun({ text: line, font: "Consolas", size: 18, color: DARK })]
    }));
}

function makeTable(headers, rows, colWidths) {
    const totalWidth = colWidths.reduce((a, b) => a + b, 0);
    const headerRow = new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
            borders,
            width: { size: colWidths[i], type: WidthType.DXA },
            shading: { fill: TABLE_HEADER_BG, type: ShadingType.CLEAR },
            margins: { top: 60, bottom: 60, left: 80, right: 80 },
            children: [new Paragraph({ children: [new TextRun({ text: h, font: "Palatino Linotype", size: 18, bold: true, color: "FFFFFF" })] })]
        }))
    });
    const dataRows = rows.map((row, ri) => new TableRow({
        children: row.map((cell, ci) => new TableCell({
            borders,
            width: { size: colWidths[ci], type: WidthType.DXA },
            shading: ri % 2 === 1 ? { fill: TABLE_ALT_BG, type: ShadingType.CLEAR } : undefined,
            margins: { top: 40, bottom: 40, left: 80, right: 80 },
            children: [new Paragraph({ children: [new TextRun({ text: String(cell), font: "Palatino Linotype", size: 17, color: BODY })] })]
        }))
    }));
    return new Table({
        width: { size: totalWidth, type: WidthType.DXA },
        columnWidths: colWidths,
        rows: [headerRow, ...dataRows]
    });
}

// ═══════════════════════════════════════════════════
// BUILD DOCUMENT
// ═══════════════════════════════════════════════════
const children = [];

// ── TITLE PAGE ──
children.push(
    new Paragraph({ spacing: { before: 2400 }, children: [] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "GLASSFORGE GAMES", font: "Cinzel", size: 18, color: DIM })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [new TextRun({ text: "VEHICLE FORGE", font: "Cinzel", size: 60, bold: true, color: GOLD })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "COMPANION GUIDE", font: "Cinzel", size: 40, bold: true, color: DARK })] }),
    goldRule(),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Universal Vehicle Construction for Savage Worlds", font: "Palatino Linotype", size: 26, italics: true, color: DIM })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [new TextRun({ text: "Everything from war chariots to star dreadnoughts. One tool. Any era. Any environment.", font: "Palatino Linotype", size: 21, color: BODY })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: `${VERSION} \u2014 February 2026`, font: "Palatino Linotype", size: 20, color: DIM })] }),
    new Paragraph({ children: [new PageBreak()] })
);

// ── CREDITS & LEGAL ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Credits & Legal")] }),
    goldRule(),
    bodyBold("Writing & Design: ", "Glassforge Games Ltd."),
    bodyBold("Vehicle Forge Tool: ", "Glassforge Games Ltd."),
    subheading("Legal Notice"),
    new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: "This game references the Savage Worlds game system, available from Pinnacle Entertainment Group at www.peginc.com. Savage Worlds and all associated logos and trademarks are copyrights of Pinnacle Entertainment Group. Used with permission. Pinnacle makes no representation or warranty as to the quality, viability, or suitability for purpose of this product.", font: "Palatino Linotype", size: 20, italics: true, color: DIM })]
    }),
    body("You will need the Savage Worlds core rules to use this product. The Science Fiction Companion is recommended for campaigns involving walkers, starships, or advanced technology vehicles."),
    body(`Vehicle Forge and all associated content \u00A9 2026 Glassforge Games Ltd. All Rights Reserved.`),
    body("Fantasy Grounds is a trademark of SmiteWorks USA, LLC. Foundry Virtual Tabletop is a trademark of Foundry Gaming LLC. Neither is affiliated with or endorsed by their respective trademark holders."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── TABLE OF CONTENTS ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Contents")] }),
    goldRule(),
    new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
    new Paragraph({ children: [new PageBreak()] })
);

// ── INTRODUCTION ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Introduction")] }),
    goldRule(),
    chapterQuote("The difference between a good GM and a great one is preparation. The difference between a great GM and a legendary one is knowing when to stop preparing and start playing."),
    body(`Welcome to the Vehicle Forge Companion Guide \u2014 your complete reference for building vehicles, war machines, and fighting craft for the Savage Worlds roleplaying game. Whether you need a WWII medium tank for tonight\u2019s session, a pirate frigate for a swashbuckling campaign, or a capital ship for a far-future war, the Forge builds it in minutes.`),
    body(`The Vehicle Forge is a standalone HTML tool that runs in any modern browser. It ships with ${WEAPON_COUNT} weapons across seven technological eras, ${MOD_COUNT} modifications across eight categories, and ${BUILD_COUNT} reference builds covering everything from bicycles to battleships. All content is original Glassforge material \u2014 the tool references Savage Worlds mechanics by name but does not reproduce them.`),
    body("This guide covers everything you need to get the most from the Forge. The opening chapters walk you through the interface and construction sequence. The reference chapters document every modification, weapon, and special ability. The walkthroughs build three complete vehicles step by step, explaining every choice. The closing chapters discuss design philosophy and the supplement ecosystem."),
    subheading("Design Philosophy"),
    new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "Fast, Furious, Fun", font: "Cinzel", size: 24, bold: true, color: GOLD })] }),
    body("Savage Worlds lives by those three words, and so does the Vehicle Forge. Every design decision prioritised speed of play over simulation depth. Six sliders. Real-time stat block. One-click export. You can build a vehicle in two minutes and have it in play in three."),
    new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "Build What You Need", font: "Cinzel", size: 24, bold: true, color: GOLD })] }),
    body(`You will never use all ${WEAPON_COUNT} weapons in a single campaign. Nor should you. Build vehicles that serve your story. A WWII one-sheet needs three or four vehicles at most. A pirate campaign might use a dozen ships over its entire run. The reference builds exist to give you a starting point \u2014 load one, adjust it, and move on.`),
    new Paragraph({ spacing: { before: 240, after: 120 }, children: [new TextRun({ text: "Show, Don\u2019t Stat", font: "Cinzel", size: 24, bold: true, color: GOLD })] }),
    body("A stat block is a skeleton. The vehicle comes alive through description, through the way the GM narrates its guns firing and its armour ringing, through the players\u2019 choices under fire. The Forge gives you the numbers. You give them meaning."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── GETTING STARTED ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Getting Started")] }),
    goldRule(),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Opening the Forge")] }),
    body("The Vehicle Forge runs in any modern web browser \u2014 Chrome, Firefox, Safari, Edge. Open the URL and start building. No installation, no account, no subscription. The interface is divided into panels: the left sidebar handles vehicle identity, Size selection, and locomotion. The main panel contains tabs for modifications, weapons, special abilities, and the live stat block output."),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("The Construction Sequence")] }),
    body("Vehicle construction follows a natural sequence, though you can jump between tabs at any time."),
    bodyBold("1. Name and Concept. ", "Start with what the vehicle is. A scout car. A patrol frigate. A heavy bomber. Type a name and write a one-line description that captures its purpose."),
    bodyBold("2. Size. ", "Slide the Size picker to set your vehicle\u2019s scale. Size determines the frame category (Normal, Large, Huge, Gargantuan), which sets base Toughness, Wounds, crew capacity, and mod slots."),
    bodyBold("3. Locomotion. ", "Choose how the vehicle moves. The Forge offers eleven locomotion types spanning ground, water, air, and walker categories. Locomotion sets base speed and determines which terrain rules apply."),
    bodyBold("4. Sliders. ", "Adjust Toughness, Armour, Speed, Handling, Wounds, and Crew. Each slider modifies the frame defaults. The stat block updates in real time as you drag."),
    bodyBold("5. Modifications. ", "Install mods from the catalogue. Each mod consumes mod slots. Drawbacks give slots back at a cost. The mod counter tracks your budget."),
    bodyBold("6. Weapons. ", "Mount weapons from the era-filtered catalogue. Choose Pintle (standard cost), Fixed (half cost, forward arc only), or Turret (double cost, 360\u00B0 arc). Each weapon has a minimum Size requirement."),
    bodyBold("7. Special Abilities. ", "Toggle Special Abilities to add narrative and mechanical flavour. These cost no mod slots \u2014 they describe what the vehicle is, not what it has."),
    bodyBold("8. Export. ", "Copy the stat block to clipboard in Pinnacle format, export as Fantasy Grounds XML, or save as JSON for backup and sharing."),
    tip("Export your vehicles regularly. Browser storage is convenient but not permanent \u2014 clearing your cache will delete your builds."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── VEHICLE FRAMES ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Vehicle Frames")] }),
    goldRule(),
    body("Every vehicle starts with a frame determined by its Size. The frame sets baseline statistics that modifications, weapons, and special abilities build upon."),
    makeTable(
        ['Size','Frame','Toughness','Wounds','Crew','Mods','Handling'],
        [
            ['-2 to 0','Normal','3\u20137','3','1','3\u20135','+1'],
            ['1 to 3','Normal','6\u20138','3','1','3\u20137','+1'],
            ['4 to 7','Large','9\u201312','4','1+','10\u201317','0'],
            ['8 to 11','Huge','13\u201316','5','5+','20\u201327','-1'],
            ['12 to 16','Gargantuan','17\u201321','6','20+','30\u201340','-2'],
            ['17 to 23','Gargantuan','22\u201328','7','100+','42\u201357','-3'],
            ['24+','Gargantuan','29+','8','500+','60+','-4'],
        ],
        [900,1200,1400,900,900,900,1100]
    ),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Vehicle Class")] }),
    body("The Forge assigns a Vehicle Class from A (lightest) to G (heaviest) based on Size, for quick comparison across eras and genres."),
    makeTable(
        ['Class','Size','Frame','Examples'],
        [
            ['A','-2 to 0','Normal','Bicycles, motorcycles, jet skis'],
            ['B','1 to 3','Normal','Cars, carriages, small boats'],
            ['C','4 to 7','Large','SUVs, APCs, tanks, fighters'],
            ['D','8 to 11','Huge','Semi-trucks, heavy tanks, bombers'],
            ['E','12 to 16','Gargantuan','Galleons, corvettes, locomotives'],
            ['F','17 to 23','Gargantuan','Cruisers, destroyers, transports'],
            ['G','24+','Gargantuan','Battleships, carriers, capital ships'],
        ],
        [600,1100,1400,4200]
    ),
    new Paragraph({ children: [new PageBreak()] })
);

// ── LOCOMOTION ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Locomotion")] }),
    goldRule(),
    body("Locomotion type defines how the vehicle moves, its base speed range, and how it interacts with terrain and environment. The Forge offers eleven types across four categories."),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Ground Vehicles")] }),
    makeTable(['Type','Speed Range','Notes'],
        [['Wheeled','~15\u2013215 MPH','Cars, trucks, motorcycles. Most common ground type.'],
         ['Tracked','~15\u201385 MPH','Tanks, APCs. Ignores Difficult Ground.'],
         ['Hover','~30\u2013205 MPH','Hovercraft, grav vehicles. Ignores most terrain.']],
        [1800,1800,3700]),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Water Vehicles")] }),
    makeTable(['Type','Speed Range','Notes'],
        [['Sail','~8\u201356 MPH','Wind-powered. Unlimited range, weather-dependent.'],
         ['Turbine (Water)','~17\u2013125 MPH','Motor boats, warships.'],
         ['Jet (Water)','~30\u2013155 MPH','Hydrofoils, fast attack craft.']],
        [1800,1800,3700]),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Aircraft")] }),
    makeTable(['Type','Speed Range','Notes'],
        [['VTOL','~90\u2013770 MPH','Helicopters, tiltrotors. Vertical takeoff.'],
         ['Turboprop','~160\u2013770 MPH','Propeller aircraft, transports.'],
         ['Jet','~430\u20132,250 MPH','Fighters, bombers, airliners.']],
        [1800,1800,3700]),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Walkers")] }),
    makeTable(['Type','Speed Range','Notes'],
        [['Biped','~12\u201360 MPH','Walkers, mechs. Piloting skill. Fighting + Stomp.'],
         ['Multileg','~12\u201348 MPH','Quadrupeds, war beasts. Reroll failed Piloting vs Out of Control.']],
        [1800,1800,3700]),
    tip("Don\u2019t overthink locomotion. If it has wheels, it\u2019s Wheeled. If it has tracks, it\u2019s Tracked. If it walks on two legs, it\u2019s Biped. The Forge handles the rest."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── MODIFICATIONS REFERENCE ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Modifications Reference")] }),
    goldRule(),
    body(`The Forge provides ${MOD_COUNT} modifications across eight categories. Each modification has a maximum number of takes, a mod slot cost, and a description of its effect. Drawbacks have negative costs \u2014 they give slots back at a price.`)
);

const modCatOrder = ['Drawbacks','Core Systems','Defensive Systems','Offensive Systems','Locomotion & Power','Personnel','Structural','Walker Systems'];
modCatOrder.forEach(cat => {
    if (!modCats[cat]) return;
    children.push(
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(cat)] }),
        makeTable(['Modification','Max','Mods','Effect'],
            modCats[cat].map(m => [m.name, String(m.max).replace(/'/g,''), m.mods, m.desc]),
            [1800,600,600,4300])
    );
});
children.push(
    tip("Drawbacks make vehicles interesting. A Temperamental engine and a Bone Shaker suspension tell a story before the first shot is fired."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── WEAPONS REFERENCE ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Weapons Reference")] }),
    goldRule(),
    body(`The Forge provides ${WEAPON_COUNT} weapons across seven technological eras. Weapons are grouped by era and category. Each weapon lists its range, damage, AP, rate of fire, mod slot cost, and notes.`)
);

eraOrder.forEach(era => {
    if (!eraWeapons[era]) return;
    children.push(
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(`${eraNames[era]} Era (${eraWeapons[era].length})`)] }),
        body(eraDescs[era]),
        makeTable(['Weapon','Range','Damage','AP','RoF','Mods','Notes'],
            eraWeapons[era].map(w => [w.name, w.range, w.damage, w.ap, w.rof, w.mods, w.notes]),
            [1700,1100,800,500,500,500,2200])
    );
});
children.push(new Paragraph({ children: [new PageBreak()] }));

// ── WEAPON MOUNTING ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Weapon Mounting")] }),
    goldRule(),
    body("Every weapon must be mounted. The mount type determines the weapon\u2019s firing arc and its mod slot cost."),
    subheading("Pintle Mount"),
    body("The standard mount. A pintle-mounted weapon has a limited firing arc (typically 180\u00B0) and costs the weapon\u2019s listed mod slots. Most vehicle weapons use pintle mounts."),
    subheading("Fixed Mount"),
    body("A weapon bolted to the hull, firing only in the vehicle\u2019s forward arc. Fixed weapons cost half the weapon\u2019s listed mod slots (rounded up). The restriction in arc is compensated by the savings in space."),
    subheading("Turret Mount"),
    body("A weapon in a rotating mount with 360\u00B0 firing arc. Turret weapons cost double the weapon\u2019s listed mod slots. The flexibility is worth the premium \u2014 a turret-mounted main gun can engage threats from any direction."),
    tip("Mount your primary weapon in a turret and secondary weapons fixed or pintle. This concentrates your mod budget on the weapon that matters most."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── WALKTHROUGH 1: M4 SHERMAN ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Walkthrough: M4 Sherman")] }),
    goldRule(),
    chapterQuote("The Sherman wasn\u2019t the best tank in the war. It was the best tank for winning the war. Reliable, mass-produced, and everywhere it needed to be."),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Concept")] }),
    body("An American WWII medium tank \u2014 the backbone of Allied armoured forces from North Africa to Berlin. Not the heaviest or the fastest, but reliable, well-armed for its class, and available in numbers that no other nation could match. We\u2019re building the definitive mid-war Sherman, the kind rolling off the Detroit production lines in 1943."),
    subheading("Starting Point: How Big Is a Medium Tank?"),
    body("A Sherman weighs 33 tonnes and stretches about 20 feet from bow plate to engine deck. The Class System table says that\u2019s solidly Large frame (Size 4\u20137). We start with Size 6 \u2014 set the Size slider and click Tracked in the Locomotion panel. The stat block updates: base Toughness 11, Handling +0, Wounds 4, and 15 mod slots. The mod counter sits in the top right \u2014 we\u2019ll be watching that number."),
    body("We check the weapon panel, filtered to Industrial era. The 75mm Tank Gun shows minimum Size 5 \u2014 fine at Size 6 \u2014 and costs 3 mod slots. Two Medium Machine Guns at 1 slot each. Five slots on weapons. The mod counter drops from 15 to 10."),
    subheading("The Problem: Armour Isn\u2019t Thick Enough"),
    body("We slide Armour up two notches and watch the stat block recalculate. Toughness reads 22(8). We know from the core rules what those numbers mean at the table, and we know from the weapon panel that a 75mm anti-tank gun does 4d10 with AP 6. That\u2019s a coin-flip \u2014 and the colonel building this tank doesn\u2019t bet his crew\u2019s lives on coin-flips."),
    body("We bump the Size slider to 7. Still Large frame \u2014 no category change \u2014 but the stat block shifts. Base Toughness climbs from 11 to 12. With the same Toughness +1 and Armour +2 settings, the display now reads Toughness 23(8). One point higher. The mod counter jumps to 12 remaining \u2014 Size 7 gives 17 total slots instead of 15. Better odds, more room to grow."),
    subheading("Finalising the Design"),
    body("We type 30 into the MPH Override field. The speed slider greys out and Top Speed locks to 30 MPH \u2014 the Sherman\u2019s road speed, confirmed by every reference source. Handling drops one notch to -1, because WW2 tanks were not agile. Crew set to 5: commander, gunner, loader, driver, bow gunner."),
    body("The 75mm Tank Gun goes into the turret mount \u2014 360\u00B0 traverse, 3 slots. One Medium Machine Gun co-axial (Fixed, 1 slot), one in the hull (Fixed Front, 1 slot). Heavy Armour ticked in the modifications list. We click Export:"),
    ...statBlock([
        "M4 SHERMAN",
        "WWII medium tank, reliable and mass-produced.",
        "Size 7 (Large) \u2022 Handling -1 \u2022 Top Speed 30 MPH",
        "Toughness 23(8) \u2022 Crew 5 \u2022 Wounds 4",
        "Weapons: 75mm Tank Gun (Turret), 2\u00D7 Medium MG (Fixed)",
        "Notes: Heavy Armour, Tracked"
    ]),
    body("Load the WW2 Medium Tank (Allied) reference build and compare. The numbers land in the same neighbourhood, because the tool produces realistic results when you feed it realistic inputs."),
    tip("The Sherman had dozens of variants \u2014 the M4A3E8 \"Easy Eight\" with a 76mm gun, the M4A3R3 flamethrower, the M4A1(76)W with wet stowage. Build the base, then adjust. That\u2019s how the real factories did it."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── WALKTHROUGH 2: 32-GUN FRIGATE ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Walkthrough: 32-Gun Frigate")] }),
    goldRule(),
    chapterQuote("A frigate was the eyes of the fleet and the terror of the merchant lanes. Fast enough to catch anything she could fight, and fast enough to run from anything she couldn\u2019t."),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Concept")] }),
    body("An 18th-century naval frigate \u2014 the workhorse of any blue-water navy. Not a lumbering ship of the line, but a fast, manoeuvrable warship carrying her guns on a single covered deck. The kind of vessel that hunted privateers, escorted convoys, and carried dispatches across oceans."),
    subheading("Starting Point: How Big Is a Frigate?"),
    body("A fifth-rate frigate displaces 700\u2013900 tonnes and measures about 130 feet on the gun deck. That\u2019s Huge frame territory \u2014 bigger than most land vehicles, smaller than a ship of the line. We start at Size 9, set Locomotion to Sail, and see: base Toughness 14, Handling -1, Wounds 5, 22 mod slots. Wind-powered means no fuel costs and unlimited range."),
    body("But a frigate is defined by her guns. We check the Blackpowder era weapons. Medium Cannon costs 2 mod slots each in Pintle mounts. We need eight of them for the main battery \u2014 that\u2019s 16 slots. At Size 9 with 22 total, that leaves only 6 for everything else. Tight."),
    subheading("The Problem: Not Enough Slots"),
    body("We bump to Size 10 \u2014 still Huge, but 25 mod slots. Nine more than the guns need. That\u2019s room for armour, rigging upgrades, and crew quarters. Size 10 also bumps base Toughness to 15, which better represents the thick oak hull of a proper warship."),
    subheading("Finalising the Design"),
    body("Armour +2 for the reinforced hull planking. MPH Override to 12 \u2014 a well-handled frigate managed 10\u201312 knots in fair weather. Handling stays at -1. Crew set to the frame default plus additional hands \u2014 a frigate carried 200\u2013300 souls between gun crews, topmen, marines, and officers."),
    body("The main battery: 8\u00D7 Medium Cannon in Pintle mounts (16 slots). Two Carronades for close-range devastation (2 slots). That\u2019s 18 on weapons. Remaining slots go to crew quarters and rigging. We click Export:"),
    ...statBlock([
        "32-GUN FRIGATE",
        "Fifth-rate warship, fast and weatherly.",
        "Size 10 (Huge) \u2022 Sail \u2022 Handling -1 \u2022 Top Speed 12 MPH",
        "Toughness 27(12) \u2022 Wounds 5 \u2022 Crew 5+200",
        "Weapons: 8\u00D7 Medium Cannon (Pintle), 2\u00D7 Carronade (Pintle)",
        "Notes: Enclosed, Heavy Armour"
    ]),
    tip("Only one broadside fires per round. Eight guns sounds impressive until you remember half of them point the wrong way. That\u2019s why frigate captains spent their careers practising the art of the turn."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── WALKTHROUGH 3: ASSAULT WALKER ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Walkthrough: Assault Walker")] }),
    goldRule(),
    chapterQuote("In the void between stars, there are places where wheels sink, tracks jam, and hover fields fail. That\u2019s where you send something with legs."),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Concept")] }),
    body("A far-future assault walker \u2014 a bipedal war machine designed for mountain warfare on a hostile colony world. The terrain defeats conventional armour: tracked vehicles can\u2019t climb the passes, hover tanks can\u2019t hold position in the updrafts, and air support keeps getting swatted by emplaced particle batteries. The general needs something that walks, shoots, and terrifies."),
    subheading("Starting Point: How Tall Is a War Machine?"),
    body("The engineer sets Locomotion to Biped and starts with Size 8 \u2014 the absolute floor, because the Heavy Laser needs minimum Size 8. The stat block reads: Huge frame, Handling -1, Wounds 5, 20 mod slots. The walker-specific Strength stat appears automatically."),
    body("He drags weapons into mount points. Heavy Laser into the Turret \u2014 5 slots, counter drops to 15. Two Medium Lasers into Fixed mounts at 3 each \u2014 counter to 9. Light Missiles \u00D78 at 0 slots. Then modifications: Jump Jets (1), Dual Cockpit (-1), Sensor Array (1), Environmental Seal (1). Mod counter reads 7 remaining out of 20."),
    subheading("The Problem: It\u2019s Not Big Enough"),
    body("The general looks at the projected height \u2014 36 feet at Size 8 \u2014 and shakes her head. She needs to fire over ridgelines, and she wants the enemy to see this thing from three valleys away. She wants psychological impact as much as firepower."),
    body("The engineer tries Size 10. Sixty-three feet tall, 125 tonnes, 25 mod slots. Base Toughness jumps to 15. The extra slots are insurance for field refits. And the silhouette, towering over the tree line, is exactly the weapon the general actually wants."),
    subheading("Dialling In the Stats"),
    body("Toughness +2 and Armour +3. Huge increments give +8 Toughness and +9 Armour. Result: Toughness 38(15). Autocannon fire bounces. MPH Override to 40 \u2014 a brisk stride for something this size. Handling -2, because 125 tonnes of walking metal does not dodge. Crew 2: pilot and gunner in the Dual Cockpit."),
    ...statBlock([
        "ASSAULT WALKER",
        "Heavy bipedal war machine, mountain warfare specialist.",
        "Size 10 (Huge) \u2022 Biped \u2022 Handling -2 \u2022 Top Speed 40 MPH",
        "Toughness 38(15) \u2022 Crew 2 \u2022 Wounds 5 \u2022 Strength d12+10",
        "Weapons: Heavy Laser (Turret), 2\u00D7 Medium Laser (Fixed), Light Missiles \u00D78 (Fixed)",
        "Notes: Heavy Armour, Jump Jets, Dual Cockpit, Sensor Array, Environmental Seal"
    ]),
    body("There\u2019s no reference build for a walker this size \u2014 and that\u2019s the point. The reference builds cover common archetypes. The slider system handles everything else. The general gets her mountain-killer. The enemy gets a sixty-three-foot reminder that some problems can\u2019t be solved by digging in."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── DESIGN NOTES & TIPS ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Design Notes & Tips")] }),
    goldRule(),
    subheading("Don\u2019t Fill Every Slot"),
    body("The temptation is to spend every available mod slot. Resist it. Real vehicles carry spare capacity, redundant systems, and empty mounting points for future refits. A vehicle with slots remaining is a vehicle with story potential \u2014 the crew might upgrade it mid-campaign, or a patron might offer a weapons refit as a reward."),
    subheading("Weapons: Less Is More"),
    body("Every weapon on a vehicle is a weapon the GM has to track in combat. A tank with one main gun and two machine guns is Fast, Furious, Fun. A tank with eight weapon systems is a spreadsheet. Build for the table, not for the spec sheet."),
    subheading("Turrets Cost Double for a Reason"),
    body("A turret-mounted weapon can fire in any direction. That flexibility is worth the premium. Mount your main weapon in a turret and everything else fixed or pintle. This concentrates your mod budget on the weapon that matters most."),
    subheading("Drawbacks Are Your Friend"),
    body("Drawbacks give mod slots back. They also make vehicles interesting. A Temperamental tank with a Bone Shaker suspension is more memorable than a statistically perfect one. Players remember the vehicle that stalled at the worst possible moment."),
    subheading("Special Abilities Tell Stories"),
    body("A vehicle with Haunted, Cursed, and Sentient is three adventures waiting to happen. A vehicle with Prototype and Unreliable is a bomb with a steering wheel. Use Special Abilities to give vehicles personality, not just statistics."),
    subheading("Scale Matters"),
    body("A Size 2 car and a Size 18 dreadnought exist in completely different tactical realities. The car is fighting infantry and dodging between buildings. The dreadnought is exchanging broadsides with other capital ships at extreme range. Build for the encounters your campaign will actually have."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── EXTENSION PACKS ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("The Extension System")] }),
    goldRule(),
    chapterQuote("The Forge is a platform, not a destination."),
    body("The Vehicle Forge ships with a comprehensive core catalogue, but no single tool can cover every genre\u2019s specific needs. The extension system (.vfx files) adds themed content packs that expand the Forge\u2019s capabilities for specific genres and campaigns."),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Planned Extension Families")] }),
    body("The planned catalogue will include packs organised into themed families, each addressing a specific genre or tactical experience:"),
    bodyBold("Blood & Thunder \u2014 ", "Naval warfare from ancient galleys to Napoleonic broadsides."),
    bodyBold("Iron & Steel \u2014 ", "Ground warfare from WW2 tanks to modern main battle tanks."),
    bodyBold("Talons & Contrails \u2014 ", "Military aviation from biplanes to stealth fighters."),
    bodyBold("Chrome & Fury \u2014 ", "Modern and near-future vehicles, spy cars, and police interceptors."),
    bodyBold("Star & Void \u2014 ", "Science fiction fleets from fighters to dreadnoughts."),
    bodyBold("Rust & Ruin \u2014 ", "Post-apocalyptic salvage and wasteland survival."),
    bodyBold("Fang & Claw \u2014 ", "Fantasy war beasts, mounts, and siege engines."),
    bodyBold("Sails & Gasbags \u2014 ", "Fantasy skyships, airships, and magical vessels."),
    bodyBold("Cog & Steam \u2014 ", "Steampunk and Victorian-era mechanical wonders."),
    bodyBold("Wire & Current \u2014 ", "Cyberpunk and near-future urban vehicles."),
    body("Pack availability, pricing, and release schedule will be confirmed at launch. Check the Glassforge Games website for the latest catalogue."),
    new Paragraph({ children: [new PageBreak()] })
);

// ── WHAT COMES NEXT ──
children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("What Comes Next")] }),
    goldRule(),
    body("The Vehicle Forge is a living tool. Future updates will expand the core weapon catalogue, add new locomotion types, and refine the construction system based on community feedback."),
    body(`Vehicle bundles \u2014 pre-built fleets for specific genres and campaigns \u2014 will provide ready-to-play vehicle collections that snap into the Forge alongside the extension packs. The ${BUILD_COUNT} reference builds are just the beginning.`),
    body("For the latest products, updates, and community content, visit Glassforge Games on DriveThruRPG."),
    new Paragraph({ spacing: { before: 600 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Now go build something.", font: "Cinzel", size: 28, bold: true, color: GOLD })] }),
    new Paragraph({ children: [new PageBreak()] })
);

// ── BACK COVER ──
children.push(
    new Paragraph({ spacing: { before: 4000 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "VEHICLE FORGE COMPANION GUIDE", font: "Cinzel", size: 22, color: DIM })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: VERSION, font: "Palatino Linotype", size: 20, color: DIM })] }),
    goldRule(),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [new TextRun({ text: "Glassforge Games Ltd.", font: "Cinzel", size: 18, color: DIM })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new ExternalHyperlink({ link: "https://glassforge.pages.dev/vehicle-forge.html",
            children: [new TextRun({ text: "glassforge.pages.dev/vehicle-forge.html", font: "Palatino Linotype", size: 18, color: GOLD, underline: {} })] })
    ]})
);

// ═══════════════════════════════════════════════════
// ASSEMBLE DOCUMENT
// ═══════════════════════════════════════════════════
const doc = new Document({
    styles: {
        default: {
            document: { run: { font: "Palatino Linotype", size: 21, color: BODY } }
        },
        paragraphStyles: [
            {
                id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 36, bold: true, font: "Cinzel", color: DARK },
                paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 }
            },
            {
                id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 28, bold: true, font: "Cinzel", color: GOLD },
                paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 }
            }
        ]
    },
    sections: [{
        properties: {
            page: {
                size: { width: 12240, height: 15840 },
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [new TextRun({ text: "Vehicle Forge Companion Guide", font: "Cinzel", size: 16, color: DIM })]
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    border: { top: { style: BorderStyle.SINGLE, size: 3, color: GOLD, space: 4 } },
                    tabStops: [{ type: TabStopType.RIGHT, position: 9360 }],
                    children: [
                        new TextRun({ text: "GLASSFORGE GAMES", font: "Cinzel", size: 14, color: DIM }),
                        new TextRun({ text: "\t", font: "Palatino Linotype", size: 16 }),
                        new TextRun({ text: "Page ", font: "Palatino Linotype", size: 16, color: DIM }),
                        new TextRun({ children: [PageNumber.CURRENT], font: "Palatino Linotype", size: 16, color: DIM })
                    ]
                })]
            })
        },
        children
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('vehicle-forge-manual.docx', buffer);
    console.log(`DOCX written: ${buffer.length.toLocaleString()} bytes`);
});
