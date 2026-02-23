#!/usr/bin/env python3
"""Vehicle Forge Companion Guide — PDF Generator
Version is pulled from combat-vehicle-forge.html automatically."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, re


class BookmarkAnchor(Flowable):
    """Zero-height flowable that registers a named destination (bookmark)."""
    def __init__(self, name, level=0, title=None):
        Flowable.__init__(self)
        self.name = name
        self.level = level
        self.title = title or name
        self.width = 0
        self.height = 0

    def draw(self):
        self.canv.bookmarkPage(self.name)
        self.canv.addOutlineEntry(self.title, self.name, level=self.level)

# Pull version from the tool HTML
TOOL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
    "diceforge-site", "combat-vehicle-forge.html")
if not os.path.exists(TOOL_PATH):
    TOOL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "combat-vehicle-forge.html")
try:
    with open(TOOL_PATH, 'r') as f:
        html = f.read()
    m = re.search(r'Vehicle Forge.*?v([\d.]+)', html)
    VERSION = m.group(1) if m else "8.2"
except:
    VERSION = "8.2"
print(f"Building Companion Guide for Vehicle Forge v{VERSION}")

# Colours matching the tool's dark gold theme
GOLD = HexColor('#C4A44A')
DARK_BG = HexColor('#1A1816')
WARM_TEXT = HexColor('#3A3530')
GREY = HexColor('#666666')
RED = HexColor('#C44444')
GREEN = HexColor('#4A8C4A')
LIGHT_BG = HexColor('#F5F0E8')
RULE_LINE = HexColor('#C4A44A')

# Styles
styles = {}

styles['Title'] = ParagraphStyle(
    'Title', fontSize=28, leading=34, alignment=TA_CENTER,
    textColor=WARM_TEXT, spaceAfter=6, fontName='Helvetica-Bold')

styles['Subtitle'] = ParagraphStyle(
    'Subtitle', fontSize=14, leading=18, alignment=TA_CENTER,
    textColor=GOLD, spaceAfter=24, fontName='Helvetica')

styles['H1'] = ParagraphStyle(
    'H1', fontSize=18, leading=22, textColor=WARM_TEXT,
    spaceBefore=24, spaceAfter=8, fontName='Helvetica-Bold')

styles['H2'] = ParagraphStyle(
    'H2', fontSize=14, leading=18, textColor=GOLD,
    spaceBefore=16, spaceAfter=6, fontName='Helvetica-Bold')

styles['H3'] = ParagraphStyle(
    'H3', fontSize=11, leading=14, textColor=WARM_TEXT,
    spaceBefore=12, spaceAfter=4, fontName='Helvetica-Bold')

styles['Body'] = ParagraphStyle(
    'Body', fontSize=10, leading=14, textColor=WARM_TEXT,
    spaceAfter=8, fontName='Helvetica', alignment=TA_JUSTIFY)

styles['BodySmall'] = ParagraphStyle(
    'BodySmall', fontSize=9, leading=12, textColor=GREY,
    spaceAfter=6, fontName='Helvetica')

styles['Callout'] = ParagraphStyle(
    'Callout', fontSize=10, leading=14, textColor=WARM_TEXT,
    spaceAfter=8, fontName='Helvetica-Oblique',
    leftIndent=18, rightIndent=18)

styles['Legal'] = ParagraphStyle(
    'Legal', fontSize=7.5, leading=10, textColor=GREY,
    spaceAfter=4, fontName='Helvetica', alignment=TA_CENTER)

styles['TOCEntry'] = ParagraphStyle(
    'TOCEntry', fontSize=12, leading=20, textColor=GOLD,
    fontName='Helvetica', spaceAfter=2)

styles['TableHead'] = ParagraphStyle(
    'TableHead', fontSize=9, leading=12, textColor=HexColor('#FFFFFF'),
    fontName='Helvetica-Bold', alignment=TA_CENTER)

styles['TableCell'] = ParagraphStyle(
    'TableCell', fontSize=9, leading=12, textColor=WARM_TEXT,
    fontName='Helvetica')

styles['TableCellCenter'] = ParagraphStyle(
    'TableCellCenter', fontSize=9, leading=12, textColor=WARM_TEXT,
    fontName='Helvetica', alignment=TA_CENTER)


def gold_rule():
    return HRFlowable(width="100%", thickness=1, color=RULE_LINE, spaceAfter=8, spaceBefore=4)

def section_break():
    return Spacer(1, 12)

def make_table(headers, rows, col_widths=None):
    """Create a styled table."""
    data = [[Paragraph(h, styles['TableHead']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles['TableCellCenter']) for c in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FAFAF5')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FAFAF5'), HexColor('#F0EDE5')]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


def build_guide():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "vehicle-forge-manual.pdf")

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
        title="Vehicle Forge Companion Guide",
        author="DiceForge Studios Ltd",
        subject="Vehicle construction toolkit for Savage Worlds"
    )

    story = []
    B = styles['Body']
    BS = styles['BodySmall']
    CO = styles['Callout']

    # ═══════════════════════════════════════════
    # TITLE PAGE
    # ═══════════════════════════════════════════
    story.append(Spacer(1, 120))
    story.append(Paragraph("DICEFORGE STUDIOS", styles['Subtitle']))
    story.append(Paragraph("Vehicle Forge", styles['Title']))
    story.append(Paragraph("Companion Guide", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"v{VERSION} \u2014 February 2026", styles['Subtitle']))
    story.append(Spacer(1, 36))
    story.append(gold_rule())
    story.append(Paragraph(
        "A complete vehicle construction toolkit for Savage Worlds. "
        "Build anything from a bicycle to a battleship in minutes.",
        CO))
    story.append(gold_rule())
    story.append(Spacer(1, 48))
    story.append(Paragraph(
        "This game references the Savage Worlds game system, available from "
        "Pinnacle Entertainment Group at www.peginc.com. Savage Worlds and all "
        "associated logos and trademarks are copyrights of Pinnacle Entertainment Group. "
        "Used with permission. Pinnacle makes no representation or warranty as to the "
        "quality, viability, or suitability for purpose of this product.",
        styles['Legal']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "\u00a9 2026 DiceForge Studios Ltd. All rights reserved.",
        styles['Legal']))
    story.append(Paragraph(
        "Fantasy Grounds is a trademark of SmiteWorks USA, LLC. "
        "Foundry VTT is a trademark of Foundry Gaming LLC.",
        styles['Legal']))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════
    story.append(Paragraph("Contents", styles['H1']))
    story.append(gold_rule())
    toc_items = [
        ("ch1", "1. Getting Started"),
        ("ch2", "2. The Six Sliders"),
        ("ch3", "3. Weapons and Modifications"),
        ("ch4", "4. The Class System"),
        ("ch5", "5. The Vehicle Hangar"),
        ("ch6", "6. Export Formats"),
        ("ch7", "7. Extension Packs"),
        ("ch8", "8. Building Vehicles: A Walkthrough"),
        ("ch9", "9. SFC Compatibility"),
        ("appA", "Appendix A: Product Catalogue"),
        ("appB", "Appendix B: Keyboard Shortcuts"),
        ("appC", "Appendix C: Licence and Credits"),
    ]
    for anchor, title in toc_items:
        story.append(Paragraph(
            f'<a href="#{anchor}" color="#C4A44A">{title}</a>',
            styles['TOCEntry']))
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 1. GETTING STARTED
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch1', level=0, title='1. Getting Started'))
    story.append(Paragraph("1. Getting Started", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "Vehicle Forge is a free, browser-based construction tool for building "
        "vehicles compatible with the Savage Worlds roleplaying game. It runs "
        "entirely in your browser \u2014 no installation, no account, no subscription. "
        "Open the URL and start building.", B))
    story.append(Paragraph(
        "The tool is designed around Savage Worlds\u2019 Fast! Furious! Fun! philosophy. "
        'Six sliders control the core statistics (see <a href="#ch2" color="#C4A44A">Chapter 2</a>). '
        "Weapons snap into mount points. "
        "Modifications add capability. The stat block generates automatically in "
        "real time as you make changes. A vehicle that would take thirty minutes "
        "to build from reference tables takes three minutes in the Forge.", B))

    story.append(Paragraph("What You Need", styles['H2']))
    story.append(Paragraph(
        "A modern web browser (Chrome, Firefox, Safari, Edge). The Savage Worlds "
        "core rules \u2014 the Forge builds vehicles compatible with the system but does "
        "not reproduce its rules. That\u2019s it.", B))

    story.append(Paragraph("The Interface", styles['H2']))
    story.append(Paragraph(
        "The screen is divided into three columns. The left sidebar contains the "
        "vehicle identity fields (name, description, notes, image), the locomotion "
        "grid, the six stat sliders, the statistics panel, and the Vehicle Hangar. "
        "The centre area holds four tabs: Modifications, Weapons, Special, and "
        "Stat Block. The right area shows the live stat block output with export "
        "buttons.", B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 2. THE SIX SLIDERS
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch2', level=0, title='2. The Six Sliders'))
    story.append(Paragraph("2. The Six Sliders", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "Every vehicle in the Forge is defined by six core statistics, each "
        "controlled by a slider. The sliders set relative values within the "
        "vehicle\u2019s size class \u2014 a \u201cstandard\u201d Toughness for a Size 8 tank is "
        "very different from \u201cstandard\u201d for a Size 2 motorcycle.", B))

    slider_data = [
        ["Size", "1\u201320", "Physical scale. Determines base Toughness, Crew, Wounds, Mod slots, and cost."],
        ["Tough", "-5 to +5", "Relative toughness adjustment within size class."],
        ["Armour", "-5 to +5", "Armour bonus. +4 or higher grants Heavy Armor."],
        ["Speed", "-5 to +5", "Top Speed adjustment. Affects chase positioning."],
        ["Handling", "-5 to +5", "Manoeuvrability. Applied to Driving/Piloting/Boating rolls."],
        ["Wounds", "-5 to +5", "Wound capacity adjustment. More wounds = harder to destroy."],
    ]
    story.append(make_table(
        ["Slider", "Range", "Effect"],
        slider_data,
        col_widths=[1.2*inch, 1*inch, 4.8*inch]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The descriptive labels beside each slider (\"Sturdy,\" \"Reinforced,\" "
        "\"Very Slow,\" \"Clumsy\") are flavour text to help you calibrate your "
        "design intent. They have no mechanical effect beyond the stat adjustment.", B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 3. WEAPONS AND MODIFICATIONS
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch3', level=0, title='3. Weapons and Modifications'))
    story.append(Paragraph("3. Weapons and Modifications", styles['H1']))
    story.append(gold_rule())

    story.append(Paragraph("Weapons", styles['H2']))
    story.append(Paragraph(
        "The Forge includes 127 weapons across seven technology eras: Ancient, "
        "Black Powder, Industrial, Modern, Future, Advanced, and Stun. Each "
        "weapon has a minimum size requirement \u2014 you can\u2019t mount a Super Heavy "
        "Cannon on a motorcycle.", B))
    story.append(Paragraph(
        "Weapons are installed in one of three mount types: Fixed Front "
        "(cheapest, fires in a forward arc only), Turret (full 360-degree "
        "rotation, costs more mod slots), or Pintle (crew-operated, exposed "
        "gunner). Weapons can be Linked in pairs or quads for increased "
        "damage at the cost of additional mod slots.", B))

    story.append(Paragraph("Modifications", styles['H2']))
    story.append(Paragraph(
        "Modifications consume mod slots and add capability: Smoke Screen, "
        "Targeting System, Shields, Fusion Core, Amphibious, Submersible, "
        "Ejection Seats, and many more. Each vehicle\u2019s available mod slots "
        "are determined by its Size. Larger vehicles have more room for "
        "systems. Some modifications can be taken multiple times (stacking "
        "armour, for instance), while others are one-off installations.", B))

    story.append(Paragraph("Custom Weapons", styles['H2']))
    story.append(Paragraph(
        "The \u201cAdd Custom Weapon\u201d button lets you define entirely new weapons "
        "with your own damage, AP, range, RoF, and notes. Custom weapons are "
        "stored in your browser alongside your saved vehicles and appear in the "
        'weapon catalogue for all future builds. See <a href="#ch5" color="#C4A44A">'
        'Chapter 5: The Vehicle Hangar</a> for details on how vehicles and '
        'weapons are stored.', B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 4. THE CLASS SYSTEM
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch4', level=0, title='4. The Class System'))
    story.append(Paragraph("4. The Class System", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "The DiceForge Class system uses the same A\u2013Z scale for both vehicles "
        "and weapons. A vehicle\u2019s Class is derived from its total Toughness "
        "(base plus Armour). A weapon\u2019s Class is derived from its average damage "
        "plus its Armour Piercing value. Because both use the same scale, a "
        "Game Master can compare them at a glance to assess combat viability.", B))

    class_data = [
        ["A", "0\u201315", "I", "Motorcycle, car, light boat"],
        ["B", "16\u201325", "II", "APC, WWII medium tank, fighter aircraft"],
        ["C", "26\u201335", "III", "Modern MBT, heavy tank, corvette"],
        ["D", "36\u201345", "IV", "Frigate, destroyer, armoured cruiser"],
        ["E", "46\u201355", "V", "Battleship, titan, dreadnought"],
        ["F", "56\u201365", "VI", "Star base, mega-titan"],
        ["G", "66\u201375", "VII", "Orbital platform, super-dreadnought"],
        ["H+", "76+", "\u2014", "Space stations, colony ships, and beyond"],
    ]
    story.append(make_table(
        ["Class", "Value", "SFC", "Examples"],
        class_data,
        col_widths=[0.7*inch, 0.9*inch, 0.7*inch, 4.7*inch]
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("The +/- Modifier", styles['H2']))
    story.append(Paragraph(
        "Each class band is subdivided with +/\u2212 modifiers to show position "
        "within the range. C+ sits at the top of Class C, almost breaking into D. "
        "C\u2212 is barely into C territory and vulnerable to strong B-class weapons. "
        "The plain letter (C) indicates a solid middle position.", B))

    story.append(Paragraph("Quick Strike Guide", styles['H2']))
    story.append(Paragraph(
        "When a weapon\u2019s class matches a vehicle\u2019s class, it\u2019s an effective "
        "engagement \u2014 standard Savage Worlds damage rules apply. One class "
        "below is outmatched but not hopeless. Two below is desperate. Three "
        "or more below is wasted ammunition. One class above is dominant. Two "
        "or more above is overkill. The class tells you what you can hurt, not "
        "what you\u2019re supposed to fight.", B))

    strike_data = [
        ["Same class", "EFFECTIVE", "Fair fight. Standard damage rules."],
        ["One below", "OUTMATCHED", "Hard going. Need lucky shots."],
        ["Two below", "DESPERATE", "Near hopeless. Only crits matter."],
        ["Three+ below", "NO EFFECT", "Find a bigger gun."],
        ["One above", "DOMINANT", "Clear advantage."],
        ["Two+ above", "OVERKILL", "Target is outclassed entirely."],
    ]
    story.append(make_table(
        ["Matchup", "Result", "Meaning"],
        strike_data,
        col_widths=[1.5*inch, 1.5*inch, 4*inch]
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 5. THE VEHICLE HANGAR
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch5', level=0, title='5. The Vehicle Hangar'))
    story.append(Paragraph("5. The Vehicle Hangar", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "The Vehicle Hangar is where all your vehicles live \u2014 both the "
        "professionally-built DF Canon vehicles from expansion packs and "
        "your own custom creations.", B))

    story.append(Paragraph("Three Tabs", styles['H2']))
    story.append(Paragraph(
        "<b>All</b> shows every vehicle in your Hangar. <b>DF Canon</b> shows "
        "only vehicles installed from official DiceForge expansion packs. "
        "<b>My Vehicles</b> shows only vehicles you\u2019ve built or cloned yourself. "
        "The search bar filters across all visible vehicles by name, "
        "description, pack, or locomotion type.", B))

    story.append(Paragraph("DF Canon vs My Vehicles", styles['H2']))
    story.append(Paragraph(
        "Canon vehicles are marked with a gold border, a lock icon, and a "
        "gold DF badge. They cannot be modified, overwritten, or deleted. "
        "They represent tested, balanced stat blocks released by DiceForge "
        "Studios. To create a variant, click the green Clone button \u2014 this "
        "copies the vehicle to My Vehicles where it becomes fully editable. "
        "The original canon vehicle remains untouched.", B))
    story.append(Paragraph(
        "Your own vehicles are marked with a green border and a MINE badge. "
        "They can be freely edited, renamed, and deleted. Vehicles are grouped "
        "by their source pack (for canon) or under \u201cMy Vehicles\u201d (for custom "
        "builds). Groups are collapsible.", B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 6. EXPORT FORMATS
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch6', level=0, title='6. Export Formats'))
    story.append(Paragraph("6. Export Formats", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "Vehicle Forge exports to three formats from a single source of truth. "
        'Build once, export everywhere. Extension packs '
        '(<a href="#ch7" color="#C4A44A">Chapter 7</a>) add new content '
        'that integrates seamlessly with all export formats.', B))

    export_data = [
        ["JSON (.json)", "Vehicle Forge native format. Batch import/export, backup.", "Vehicle Forge"],
        ["Stat Block (.txt)", "Pinnacle-format plain text. Universal.", "Foundry VTT, Roll20, index cards, any VTT"],
        ["FG XML (.xml)", "Fantasy Grounds Unity db.xml fragments.", "Fantasy Grounds Unity"],
    ]
    story.append(make_table(
        ["Format", "Purpose", "Compatible With"],
        export_data,
        col_widths=[1.5*inch, 2.5*inch, 3*inch]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The Pinnacle text stat block is the lingua franca of Savage Worlds. "
        "Every GM recognises the format. Every VTT importer that exists can "
        "parse it. When in doubt, export as text \u2014 it works everywhere.", B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 7. EXTENSION PACKS
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch7', level=0, title='7. Extension Packs'))
    story.append(Paragraph("7. Extension Packs (.vfx)", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "Extension packs are .vfx files that add new content to the Forge: "
        "weapons, modifications, special abilities, and pre-built vehicles. "
        "Install them via the Extensions button in the Vehicle Hangar. "
        "Uninstalling a pack removes all its content cleanly.", B))
    story.append(Paragraph(
        "Each .vfx pack may contain any combination of: new weapons that "
        "appear in the weapon catalogue, new modifications for the mod bay, "
        "new special abilities, and pre-built vehicles that appear as DF Canon "
        "entries in the Vehicle Hangar. Weapons and modifications from extension "
        "packs are tagged with the pack name so you always know where they "
        "came from.", B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 8. BUILDING VEHICLES: A WALKTHROUGH
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch8', level=0, title='8. Building Vehicles: A Walkthrough'))
    story.append(Paragraph("8. Building Vehicles: A Walkthrough", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "Let\u2019s build a WWII Sherman tank from scratch.", B))

    steps = [
        ("<b>Name it.</b> Type \u201cM4 Sherman\u201d in the Name field. Add a description: "
         "\u201cThe workhorse of the Allied armoured forces.\u201d"),
        ("<b>Set the frame.</b> Select Tracked locomotion. Set Size to 7 "
         "(medium tank, ~32 tons)."),
        ("<b>Adjust the sliders.</b> Toughness: Standard (0). Armour: +1 "
         "(decent for its era but not exceptional). Speed: Standard (0). "
         "Handling: -1 (not nimble). Wounds: Standard (0)."),
        ("<b>Add weapons.</b> Switch to the Weapons tab. Find the Medium Cannon "
         "in the Modern era. Install it in a Turret mount. Add a Heavy Machine "
         "Gun on a Pintle mount for the commander."),
        ("<b>Add modifications.</b> Switch to Modifications. Add Smoke Screen "
         "(2 charges). Check your remaining mod slots."),
        ("<b>Review the stat block.</b> Switch to the Stat Block tab. You should "
         "see something like: Class C (III) \u2014 Size 7, Tracked, Handling -1, "
         "Toughness in the high 20s. Does it feel right? Adjust if needed."),
        ("<b>Save it.</b> Click Save. Your Sherman now lives in the Vehicle "
         "Hangar under My Vehicles."),
        ("<b>Export it.</b> Click Stat Block .txt to generate a Pinnacle-format "
         "stat block. Click FG XML for Fantasy Grounds. Click Export .json for "
         "backup or sharing."),
    ]
    for i, step in enumerate(steps):
        story.append(Paragraph(f"{i+1}. {step}", B))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The entire process takes three to five minutes. Building the same "
        "vehicle from reference tables would take twenty to thirty.", B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # 9. SFC COMPATIBILITY
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('ch9', level=0, title='9. SFC Compatibility'))
    story.append(Paragraph("9. SFC Compatibility", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "The DiceForge Class system is fully compatible with the Science "
        "Fiction Companion\u2019s Heavy Metal setting rule. Classes A through G "
        "map directly to SFC Classes I through VII using the same mathematical "
        "formula: average damage plus Armour Piercing for weapons, total "
        "Toughness for vehicles.", B))

    sfc_data = [
        ["A", "I"], ["B", "II"], ["C", "III"], ["D", "IV"],
        ["E", "V"], ["F", "VI"], ["G", "VII"], ["H+", "\u2014 (beyond SFC)"],
    ]
    story.append(make_table(
        ["DiceForge", "SFC Equivalent"],
        sfc_data,
        col_widths=[2*inch, 2*inch]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "GMs using the SFC Heavy Metal rules can apply them directly to any "
        "Vehicle Forge stat block without conversion. The parenthetical roman "
        "numeral shown in every stat block \u2014 for example, Class C+ (III) \u2014 "
        "is the SFC equivalent provided for convenience.", B))
    story.append(Paragraph(
        "DiceForge classes beyond G represent vehicles and weapons that exceed "
        "the SFC\u2019s Class VII ceiling. The system scales to Z (and theoretically "
        "beyond), accommodating everything from orbital battle stations to "
        "generation ships. The SFC was designed for one book\u2019s worth of "
        'vehicles. The DiceForge system was designed for all of them. '
        'See <a href="#ch9" color="#C4A44A">Chapter 9: SFC Compatibility</a> '
        'for the full mapping table.', B))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # APPENDIX A: PRODUCT CATALOGUE
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('appA', level=0, title='Appendix A: Product Catalogue'))
    story.append(Paragraph("Appendix A: Product Catalogue", styles['H1']))
    story.append(gold_rule())
    story.append(Paragraph(
        "The Vehicle Forge content ecosystem includes the following product types. "
        "Visit diceforgestudios.pages.dev for the current catalogue.", B))

    cat_data = [
        ["Vehicle Forge Tool", "FREE", "Complete construction system, 47 canon reference builds"],
        ["Vehicle Packs", "$2.99", "10 DF Canon vehicles per pack, .vfx format"],
        ["One-Sheet Adventures", "$1.99", "4\u20136 page adventures using pack vehicles"],
        ["NPC Crew Packs", "$1.99", "6\u20138 named NPCs with stat blocks"],
        ["Theatre Supplements", "$5.99\u2013$7.99", "Deep-dive rules, weapons, adventures"],
        ["Genre Collections", "$9.99\u2013$49.99", "Bundled sets at 25\u201335% discount"],
    ]
    story.append(make_table(
        ["Product", "Price", "Contents"],
        cat_data,
        col_widths=[2*inch, 1.2*inch, 3.8*inch]
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # APPENDIX B: KEYBOARD SHORTCUTS
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('appB', level=0, title='Appendix B: Keyboard Shortcuts'))
    story.append(Paragraph("Appendix B: Keyboard Shortcuts", styles['H1']))
    story.append(gold_rule())
    key_data = [
        ["Ctrl+Z", "Undo last change"],
        ["Ctrl+Y", "Redo"],
        ["Ctrl+S", "Save current vehicle"],
    ]
    story.append(make_table(
        ["Key", "Action"],
        key_data,
        col_widths=[2*inch, 5*inch]
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # APPENDIX C: LICENCE AND CREDITS
    # ═══════════════════════════════════════════
    story.append(BookmarkAnchor('appC', level=0, title='Appendix C: Licence and Credits'))
    story.append(Paragraph("Appendix C: Licence and Credits", styles['H1']))
    story.append(gold_rule())

    story.append(Paragraph("Pinnacle Fan Licence", styles['H2']))
    story.append(Paragraph(
        "This game references the Savage Worlds game system, available from "
        "Pinnacle Entertainment Group at www.peginc.com. Savage Worlds and all "
        "associated logos and trademarks are copyrights of Pinnacle Entertainment "
        "Group. Used with permission. Pinnacle makes no representation or warranty "
        "as to the quality, viability, or suitability for purpose of this product.", B))

    story.append(Paragraph("Trademark Notices", styles['H2']))
    story.append(Paragraph(
        "Fantasy Grounds is a trademark of SmiteWorks USA, LLC. "
        "Foundry VTT is a trademark of Foundry Gaming LLC. "
        "Use of these trademarks does not imply endorsement.", B))

    story.append(Paragraph("Credits", styles['H2']))
    story.append(Paragraph(
        "Vehicle Forge designed and developed by DiceForge Studios Ltd. "
        "All original content, code, and design \u00a9 2026 DiceForge Studios Ltd. "
        "All rights reserved.", B))
    story.append(Spacer(1, 24))
    story.append(gold_rule())
    story.append(Paragraph(
        "<i>Up the Irons.</i>", ParagraphStyle(
            'Closer', fontSize=12, leading=16, alignment=TA_CENTER,
            textColor=GOLD, fontName='Helvetica-Oblique')))

    # Build
    doc.build(story)
    return output_path


if __name__ == "__main__":
    path = build_guide()
    print(f"Built: {path}")
