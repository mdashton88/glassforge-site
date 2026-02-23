#!/usr/bin/env python3
"""Vehicle Forge Companion Guide — PDF Generator. See MANUAL_SPEC.md for requirements."""
import re, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY

GOLD=HexColor('#C4A44A');GOLD_DIM=HexColor('#8A7A3A');DARK=HexColor('#1A1A2E');MEDIUM=HexColor('#3A3540')
WARM_BG=HexColor('#FAFAF5');TABLE_ALT=HexColor('#F5F0E8');BORDER_CLR=HexColor('#D4C8A8')

class GoldRule(Flowable):
    def __init__(s,w,t=0.75):Flowable.__init__(s);s.width=w;s.thickness=t
    def draw(s):s.canv.setStrokeColor(GOLD);s.canv.setLineWidth(s.thickness);s.canv.line(0,0,s.width,0)
    def wrap(s,aw,ah):return(s.width,s.thickness+2)

S=lambda n,**k:ParagraphStyle(n,**k)
title_s=S('T',fontSize=28,leading=34,textColor=GOLD,fontName='Helvetica-Bold',spaceAfter=4)
brand_s=S('Br',fontSize=11,leading=14,textColor=GOLD_DIM,fontName='Helvetica-Bold',spaceAfter=4)
sub_s=S('Su',fontSize=13,leading=17,textColor=MEDIUM,fontName='Helvetica-Oblique',spaceAfter=16)
ver_s=S('V',fontSize=9,leading=12,textColor=MEDIUM,fontName='Helvetica',spaceAfter=4)
h1_s=S('H1',fontSize=18,leading=22,textColor=GOLD,fontName='Helvetica-Bold',spaceBefore=16,spaceAfter=6)
h2_s=S('H2',fontSize=12,leading=16,textColor=GOLD,fontName='Helvetica-Bold',spaceBefore=12,spaceAfter=4)
body_s=S('B',fontSize=9.5,leading=13.5,textColor=DARK,fontName='Helvetica',spaceAfter=7,alignment=TA_JUSTIFY)
note_s=S('N',fontSize=8.5,leading=12,textColor=MEDIUM,fontName='Helvetica-Oblique',spaceAfter=6,leftIndent=10,rightIndent=10,alignment=TA_JUSTIFY)
mono_s=S('M',fontSize=8.5,leading=11,textColor=DARK,fontName='Courier',spaceAfter=4,leftIndent=10,backColor=TABLE_ALT)
legal_s=S('L',fontSize=7,leading=9,textColor=MEDIUM,fontName='Helvetica',spaceAfter=3,alignment=TA_JUSTIFY)
toc_s=S('TOC',fontSize=10.5,leading=18,textColor=DARK,fontName='Helvetica')
bullet_s=S('Bu',fontSize=9.5,leading=13.5,textColor=DARK,fontName='Helvetica',leftIndent=14,bulletIndent=4,spaceBefore=2,spaceAfter=2,alignment=TA_JUSTIFY)
cs_=S('C',fontSize=7.5,leading=10,fontName='Helvetica',textColor=DARK)
cb_=S('CB',fontSize=7.5,leading=10,fontName='Helvetica-Bold',textColor=DARK)
ch_=S('CH',fontSize=7.5,leading=10,fontName='Helvetica-Bold',textColor=white)

def gr():return GoldRule(6.5*inch)
def sb():return[Spacer(1,3),gr(),Spacer(1,6)]

def dt(header,rows,cw):
    ar=[header]+rows
    t=Table([[Paragraph(str(c),ch_ if i==0 else(cb_ if k==0 else cs_))for k,c in enumerate(row)]for i,row in enumerate(ar)],colWidths=cw)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GOLD),('TEXTCOLOR',(0,0),(-1,0),white),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,TABLE_ALT]),('GRID',(0,0),(-1,-1),0.5,BORDER_CLR),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
    return t

sd=os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(sd,'vehicle-forge.html'))as f:html=f.read()
vm=re.search(r'v(0\.\d+\.\d+)',html);VERSION=vm.group(0)if vm else'v0.10'
ws=html.find('var WEAPONS=[');we=html.find('];',ws)+2;wchunk=html[ws:we]
WC=len(set(re.findall(r"id:'([^']+)'",wchunk)))
cs0=html.find('CANON_BUILDS=[');cs1=html.find('];',cs0)+2;BC=len(re.findall(r'name:"',html[cs0:cs1]))
ms0=html.find('var MODS=[');ms1=html.find('];',ms0)+2;mchunk=html[ms0:ms1];MC=len(re.findall(r"id:'",mchunk))

story=[]
# TITLE
story+=[Spacer(1,1.8*inch),Paragraph("DICEFORGE STUDIOS",brand_s),Spacer(1,6),Paragraph("Vehicle Forge",title_s),Paragraph("Companion Guide",sub_s),gr(),Spacer(1,14),Paragraph(f"{VERSION} \u2014 February 2026",ver_s),Spacer(1,10),Paragraph(f"A complete vehicle construction toolkit for Savage Worlds. Build anything from a bicycle to a battleship in minutes. {BC} reference builds, {WC} weapons across seven eras, {MC} modifications. Free, browser-based, no installation required.",body_s),Spacer(1,30),Paragraph('This game references the Savage Worlds game system, available from Pinnacle Entertainment Group at <a href="https://www.peginc.com" color="#C4A44A">www.peginc.com</a>. Savage Worlds and all associated logos and trademarks are copyrights of Pinnacle Entertainment Group. Used with permission. Pinnacle makes no representation or warranty as to the quality, viability, or suitability for purpose of this product.',legal_s),Spacer(1,4),Paragraph("<b>You will need the Savage Worlds core rules to use this product.</b>",legal_s),Spacer(1,4),Paragraph("Vehicle Forge and all associated content \u00a9 2025\u20132026 DiceForge Studios Ltd. All Rights Reserved.",legal_s),PageBreak()]
# TOC
story+=[Paragraph("Contents",h1_s),Spacer(1,6)]
for n,t2 in[("1.","Getting Started"),("2.","The Six Sliders"),("3.","Weapons"),("4.","Modifications Reference"),("5.","The Class System"),("6.","Locomotion Types"),("7.","Reference Builds"),("8.","Export Formats"),("9.","Extension Packs"),("10.","Building Vehicles: Walkthroughs"),("A.","Weapon Reference Tables"),("B.","Keyboard Shortcuts"),("C.","Licence and Credits")]:story.append(Paragraph(f"<b>{n}</b>  {t2}",toc_s))
story.append(PageBreak())
# CH1
story+=[Paragraph("1. Getting Started",h1_s)]+sb()+[Paragraph("Vehicle Forge is a free, browser-based construction tool for building vehicles compatible with the Savage Worlds roleplaying game. It runs entirely in your browser \u2014 no installation, no account, no subscription. Open the URL and start building.",body_s),Paragraph("The tool is designed around Savage Worlds\u2019 <i>Fast! Furious! Fun!</i> philosophy. Six sliders control the core statistics. Weapons snap into mount points. Modifications add capability. The stat block generates automatically in Pinnacle-standard format, ready for any adventure.",body_s),Paragraph("What You Need",h2_s),Paragraph("A modern web browser and the Savage Worlds core rules. The tool references Savage Worlds mechanics by name but does not reproduce them \u2014 you will need the rulebook to understand what the stats mean at the table.",body_s),Paragraph("Quick Start",h2_s),Paragraph("<b>1.</b> Choose a <b>Size</b> \u2014 sets the frame category and base stats. <b>2.</b> Choose a <b>Locomotion</b> type. <b>3.</b> Adjust the six sliders. <b>4.</b> Add weapons. <b>5.</b> Add modifications. <b>6.</b> Export.",body_s),PageBreak()]
# CH2
story+=[Paragraph("2. The Six Sliders",h1_s)]+sb()+[Paragraph("Every vehicle is defined by six slider values that modify the frame defaults set by Size and locomotion. The stat block updates in real time.",body_s)]
for nm,desc in[("Toughness","How much punishment the vehicle absorbs. Each step adds the frame category\u2019s increment: Normal +2, Large +3, Huge +4, Gargantuan +5."),("Armour","Armoured plating shown in parentheses after Toughness. Each step: Normal +1, Large +2, Huge +3, Gargantuan +4."),("Speed","Top Speed in MPH. Base and increment depend on locomotion type. Use MPH Override for exact values."),("Handling","Manoeuvrability modifier for Driving, Piloting, or Boating rolls. Small vehicles handle better."),("Wounds","Wounds before Wrecked. Reduce for fragile vehicles, increase for rugged designs."),("Crew","Operating crew required. The separate Passengers field sets additional carried personnel.")]:story+=[Paragraph(nm,h2_s),Paragraph(desc,body_s)]
story+=[Paragraph("MPH Override",h2_s),Paragraph("Sets Top Speed directly, bypassing the speed slider. Use for historical vehicles with known performance. All reference builds use this.",body_s),PageBreak()]
# CH3
story+=[Paragraph("3. Weapons",h1_s)]+sb()+[Paragraph(f"{WC} weapons across seven eras: Ancient, Medieval, Blackpowder, Industrial (WWI/WW2), Modern, Future (Sci-Fi), and Advanced (Far-Future). Switch eras to see different catalogues. Each weapon has a minimum Size requirement and occupies modification slots. See Appendix A for complete tables.",body_s)]
for c in["Machine Guns and Slugthrowers \u2014 belt-fed automatics from rifle calibre to .50 cal","Autocannons \u2014 rapid-fire 20-40mm for suppression and anti-armour","Cannons \u2014 tank guns from 37mm through 125mm and beyond","Missiles \u2014 guided munitions from ATGMs to cruise missiles","Rockets \u2014 unguided pods, immune to countermeasures","Lasers, Particle, and Energy Weapons \u2014 directed energy for sci-fi settings","Mass Drivers and Railguns \u2014 electromagnetic kinetics for far-future","Siege Engines \u2014 torsion and counterweight artillery","Blackpowder Guns \u2014 smoothbore cannon, carronades, mortars","Ordnance \u2014 bombs, mines, torpedoes, depth charges"]:story.append(Paragraph(f"<font color='#C4A44A'>\u2022</font>  {c}",bullet_s))
story.append(PageBreak())
# CH4
story+=[Paragraph("4. Modifications Reference",h1_s)]+sb()+[Paragraph(f"{MC} modifications across eight categories, all original DiceForge content. Each occupies one modification slot unless noted. Extension packs can add custom modifications for their genre.",body_s)]
MOD_DESCS={'Drawbacks':[('Unmanned','No crew compartment. Remote or AI controlled. Immune to crew-targeting but vulnerable to signal disruption.'),('Open Crew','Crew exposed. 50% of hits strike crew directly. Chariots, technicals, open-topped vehicles.'),('Temperamental','Unreliable. Critical failure stalls engine \u2014 Repair roll to restart.'),('Gas-Guzzler','Double fuel consumption. Range halved.'),('Low-Tech','No electrical systems. Immune to EMP, cannot mount electronics.'),('Skeleton Crew','Fewer crew than normal. All tasks at -1.'),('Bone Shaker','Rough ride. All actions aboard at -1.'),('Death Trap','Explodes when Wrecked. Crew take 3d6 damage.')],'Core Systems':[('Machine Intelligence','AI-assisted. One independent action per round.'),('Enhanced Sensors','+2 to Notice rolls using vehicle sensors.'),('Tactical Relay','Shares targeting data with allies in range.'),('Signal Rig','Extended radio/signal range.'),('Remote Operator','Remotely controlled. Requires Signal Rig.'),('Detection Grid','Area surveillance. Auto-detects movement in radius.'),('Sensor Array','Multi-spectrum. Halves darkness, smoke, concealment penalties.')],'Defensive Systems':[('Sloped Armour','Angled plate. Front attacks suffer -2 AP.'),('Countermeasure Suite','Jammers, chaff, flares. +2 vs guided weapons.'),('Surge Protection','Hardened electronics. Immune to EMP/ion.'),('Crew Escape','Abandon vehicle as free action when Wrecked.'),('Nanorepair System','Self-repairing. Free Repair roll each round.'),('Deflection Field','+2 Armour vs energy weapons only.'),('Stealth System','-4 to electronic detection.')],'Offensive Systems':[('Gimballed Weapons','Fixed weapons gain 90\u00b0 arc.'),('Fire Control','+1 Shooting with vehicle weapons.')],'Locomotion and Power':[('Amphibious Kit','Sealed hull. Can enter water.'),('Boost Injector','Once per encounter, double Top Speed for one round.'),('Reserve Tanks','Double fuel capacity and range.'),('Off-Road Package','Difficult Ground as 1.5" per inch.'),('Fusion Core','Unlimited fuel.'),('Road Vehicle','+1 Handling on roads, -1 off-road.'),('Submersible','Operates underwater.'),('Variable Form','Switches between two locomotion types.')],'Personnel':[('Berths','Sleeping quarters for extended ops.'),('Comfort Upgrade','No Fatigue from long journeys.'),('Troop Bay','Infantry compartment with deployment ramp.'),('Specialist Workshop','+2 to relevant skill rolls aboard.'),('Environmental Seal','Operates in vacuum, toxics, altitude.')],'Structural':[('Vehicle Bay','Internal hangar for vehicles up to half Size.'),('Compact Engineering','+2 bonus mod slots.')],'Walker Systems':[('Jump Jets','Jump full Pace once per round.'),('Dual Cockpit','Pilot and gunner independent. No multi-action penalty.')]}
for cat,mods in MOD_DESCS.items():story+=[Paragraph(cat,h2_s),dt(['Modification','Effect'],mods,[1.5*inch,4.6*inch]),Spacer(1,6)]
story.append(PageBreak())
# CH5
story+=[Paragraph("5. The Class System",h1_s)]+sb()+[Paragraph("An original DiceForge classification from A (lightest) to G (heaviest) for quick comparison.",body_s),dt(['Class','Size','Frame','Examples'],[['A','-2 to 0','Normal','Bicycles, motorcycles, jet skis'],['B','1 to 3','Normal','Cars, carriages, small boats'],['C','4 to 7','Large','SUVs, APCs, tanks, fighters'],['D','8 to 11','Huge','Semi-trucks, heavy tanks, bombers'],['E','12 to 16','Gargantuan','Galleons, corvettes, locomotives'],['F','17 to 23','Gargantuan','Cruisers, destroyers, transports'],['G','24+','Gargantuan','Battleships, carriers, capital ships']],[0.5*inch,0.8*inch,1*inch,3.8*inch]),PageBreak()]
# CH6
story+=[Paragraph("6. Locomotion Types",h1_s)]+sb()+[Paragraph("Locomotion sets the speed model, movement rules, and terrain capability.",body_s),dt(['Type','Speed Range','Notes'],[['Wheeled','~15\u2013215 MPH','Cars, trucks, motorcycles.'],['Tracked','~15\u201385 MPH','Tanks, APCs. Ignores Difficult Ground.'],['Hover','~30\u2013205 MPH','Hovercraft, grav vehicles. Ignores terrain.'],['VTOL','~90\u2013770 MPH','Helicopters, tiltrotors.'],['Turboprop','~160\u2013770 MPH','Propeller aircraft.'],['Jet','~430\u20132,250 MPH','Fighters, bombers, airliners.'],['Sail','~8\u201356 MPH','Wind-powered watercraft.'],['Turbine (Water)','~17\u2013125 MPH','Motor boats, warships.'],['Jet (Water)','~30\u2013155 MPH','Hydrofoils, fast attack.'],['Biped','~12\u201360 MPH','Walkers, mechs.'],['Quadruped','~12\u201348 MPH','Horses, war beasts.']],[1.2*inch,1.1*inch,3.8*inch]),PageBreak()]
# CH7
story+=[Paragraph("7. Reference Builds",h1_s)]+sb()+[Paragraph(f"Vehicle Forge ships with {BC} locked reference builds covering every major vehicle archetype from bicycles to battleships. These are original DiceForge stat blocks for generic vehicle classes, professionally calibrated to be realistic for their type. Each includes real-world examples and GM notes.",body_s),Paragraph("Reference builds demonstrate the slider system, provide ready-to-use stat blocks, and serve as starting points for custom designs. Load one, unlock it, and adjust to taste.",body_s),Paragraph("The reference builds are accessible within the tool \u2014 select any from the Reference Builds panel.",note_s),PageBreak()]
# CH8
story+=[Paragraph("8. Export Formats",h1_s)]+sb()
for fmt,desc in[("Pinnacle Stat Block","Plain text in the standard format used by every Savage Worlds product."),("Fantasy Grounds XML","Valid db.xml fragment for FG Unity. Paste into any campaign database."),("JSON","Native format for backup, sharing, and batch operations.")]:story+=[Paragraph(fmt,h2_s),Paragraph(desc,body_s)]
story+=[Paragraph("Fantasy Grounds is a trademark of SmiteWorks USA, LLC. Not affiliated with or endorsed by SmiteWorks.",legal_s),PageBreak()]
# CH9
story+=[Paragraph("9. Extension Packs",h1_s)]+sb()+[Paragraph("Extension packs (.vfx files) add themed vehicle collections. Single-click install. The planned catalogue will include packs organised into themed families:",body_s)]
for fam in["Blood and Thunder \u2014 naval warfare from ancient galleys to Napoleonic broadsides","Iron and Steel \u2014 ground warfare from WW2 tanks to modern main battle tanks","Talons and Contrails \u2014 military aviation from biplanes to stealth fighters","Chrome and Fury \u2014 modern and near-future vehicles, spy cars, police interceptors","Star and Void \u2014 science fiction fleets from fighters to dreadnoughts","Rust and Ruin \u2014 post-apocalyptic salvage and wasteland survival","Fang and Claw \u2014 fantasy war beasts, mounts, siege engines","Sails and Gasbags \u2014 fantasy skyships, airships, magical vessels","Cog and Steam \u2014 steampunk and Victorian mechanical wonders","Wire and Current \u2014 cyberpunk and near-future urban vehicles"]:story.append(Paragraph(f"<font color='#C4A44A'>\u2022</font>  {fam}",bullet_s))
story+=[Spacer(1,8),Paragraph("Pack availability, pricing, and release schedule will be confirmed at launch.",note_s),PageBreak()]

# CH10 — WALKTHROUGHS (iterative design vignettes)
story+=[Paragraph("10. Building Vehicles: Walkthroughs",h1_s)]+sb()
story.append(Paragraph("The best way to learn Vehicle Forge is to build something. These two walkthroughs take you through the design process step by step, explaining not just <i>what</i> to click but <i>why</i> each choice makes sense \u2014 including the false starts and revisions that are part of every real design. The first builds a historical vehicle against known specifications. The second builds a science-fiction war machine from genre conventions and tactical requirements.",body_s))

# ── VIGNETTE 1: WW2 MEDIUM TANK ──
story.append(Paragraph("Walkthrough 1: \u201cSomething That Can Take a Hit\u201d",h2_s))
story.append(Paragraph("It\u2019s late 1943 and the Ordnance Department needs another medium tank. Not the best tank \u2014 the best tank is the one that\u2019s available, and what\u2019s available is a thirty-tonne hull, a cast turret ring, and whatever gun the factory can fit through the mantlet. The colonel doesn\u2019t want perfection. He wants something that keeps up with the infantry advance, takes a hit from a field gun without brewing up, and puts a 75mm shell through anything it meets that isn\u2019t a heavy. Let\u2019s build it.",body_s))

story.append(Paragraph("Starting Point: How Big Is a Medium Tank?",h2_s))
story.append(Paragraph("First question: what Size? A WW2 medium tank weighs 25\u201335 tonnes and stretches about 20\u201325 feet hull to hull. The Class System table tells us that\u2019s the Large frame (Size 4\u20137). Our first instinct is <b>Size 6</b>: a respectable armoured vehicle, 15 mod slots, base Toughness 11. We set Locomotion to <b>Tracked</b>, because she\u2019s a tank \u2014 steel tracks, Difficult Ground ignored, and the Tracked vehicle note in the stat block.",body_s))
story.append(Paragraph("Now the guns. The 75mm Tank Gun needs minimum Size 5 \u2014 no problem at Size 6. But it costs 3 mod slots. Two Medium Machine Guns at 1 slot each. That\u2019s 5 slots on weapons alone, leaving 10 for everything else. So far so good.",body_s))

story.append(Paragraph("The Problem: Armour Isn\u2019t Thick Enough",h2_s))
story.append(Paragraph("We slide Armour up to +2. At Size 6, base Armour is 4 with a Large step of +2 per level, so two steps give us Armour 8. One step of Toughness adds +3. Total: Toughness 22(8). The colonel squints at the numbers. \u201cWhat\u2019s the standard enemy anti-tank gun do?\u201d We check the weapon tables. A 75mm anti-tank gun does 4d10 with AP 6. Average damage: 22. That means a direct hit has a coin-flip chance of penetrating our hull. The colonel wants better odds than that.",body_s))
story.append(Paragraph("We bump to <b>Size 7</b>. Still Large frame, still the same category, but base Toughness climbs from 11 to 12. With the same slider positions \u2014 Toughness +1, Armour +2 \u2014 we get Toughness 23(8). One point doesn\u2019t sound like much, but it means the standard AT gun now needs an above-average roll to penetrate. More importantly, Size 7 gives us 17 mod slots instead of 15. Those two extra slots are insurance if the weapons fit changes during production. The colonel nods. Size 7 it is.",body_s))

story.append(Paragraph("Finalising the Design",h2_s))
story.append(Paragraph("<b>MPH Override: 30.</b> Medium tanks of this era managed 25\u201335 MPH on roads. The M4 Sherman did 30, the Cromwell managed 32, the Panzer IV hit 26. We set 30 using MPH Override, which bypasses the speed slider entirely \u2014 we\u2019re telling the tool exactly what our research says this vehicle class does.",body_s))
story.append(Paragraph("<b>Handling -1.</b> The Large frame default is +0, but tanks of this era were not nimble. One step down. She turns slowly, stops slowly, and threading through a village is an adventure in itself. The driver earns his pay.",body_s))
story.append(Paragraph("<b>Crew 5.</b> Commander, gunner, loader, driver, bow gunner. The classic medium tank crew. Some designs ran four if they dropped the hull gun \u2014 adjust to suit the specific mark.",body_s))
story.append(Paragraph("<b>Weapons.</b> Select the Industrial era. The 75mm Tank Gun goes in a Turret \u2014 3 slots, 360\u00b0 traverse, the main armament. One Medium Machine Gun co-axial with the turret (Fixed, 1 slot) and one in the hull (Fixed Front, 1 slot). Five slots total on weapons. Twelve slots remaining for future modifications if the design evolves \u2014 and WW2 tank designs always evolved.",body_s))
story.append(Paragraph("<b>Heavy Armour</b> means only Heavy Weapons can damage her. Rifle fire and pistol rounds bounce off the hull, which is exactly what 50mm of welded steel is for. The colonel\u2019s requirement met.",body_s))
story.append(Spacer(1,4))
story.append(Paragraph("Size 7 (Large) \u2022 Handling -1 \u2022 Top Speed 30 MPH \u2022 Toughness 23(8) \u2022 Crew 5 \u2022 Wounds 4",mono_s))
story.append(Paragraph("Weapons: 75mm Tank Gun (Turret), 2\u00d7 Medium MG (Fixed)",mono_s))
story.append(Paragraph("Notes: Heavy Armour, Tracked",mono_s))
story.append(Spacer(1,4))
story.append(Paragraph("Load the WW2 Medium Tank (Allied) reference build and compare. The numbers will land in the same neighbourhood, because the tool produces realistic results when you feed it realistic inputs. The reference build exists to confirm your instincts, not replace them.",body_s))

# ── VIGNETTE 2: SCI-FI ASSAULT WALKER ──
story.append(Paragraph("Walkthrough 2: \u201cPut Legs on It\u201d",h2_s))
story.append(Paragraph("The general has a problem. The colony on Kessler IV is dug into a mountain range that makes conventional armour useless \u2014 tracked vehicles can\u2019t climb the passes, hover tanks can\u2019t hold position in the updrafts, and air support keeps getting swatted by emplaced particle batteries. She needs something that walks. Something tall enough to fire over the ridgeline, armoured enough to survive the return fire, and carrying enough firepower to crack a hardened firebase. Her chief engineer grins. He\u2019s been waiting for this requisition.",body_s))

story.append(Paragraph("Starting Point: How Tall Is a War Machine?",h2_s))
story.append(Paragraph("The engineer\u2019s first question isn\u2019t about weapons or armour \u2014 it\u2019s about height. The ridgelines on Kessler IV average 35 metres. The general needs to fire over them, which means the weapons platform needs to stand at least 15\u201320 metres tall to get line of sight from the valley floor. He sets Locomotion to <b>Biped</b> and starts with <b>Size 8</b> \u2014 the absolute floor, because the Heavy Laser the general wants requires minimum Size 8. That gives him Huge frame: base Handling -1, 5 Wounds, 20 mod slots.",body_s))
story.append(Paragraph("He starts fitting weapons. The Heavy Laser costs 5 mod slots \u2014 it\u2019s a capital-grade directed energy weapon and it takes up space. Two Medium Lasers for suppression at 3 slots each. A pod of eight Light Missiles for fast movers and bunkers at 0 slots (self-contained launcher, minimal integration). That\u2019s 11 of 20 slots on weapons alone. Jump Jets for obstacle clearance: 1 slot. Dual Cockpit so pilot and gunner work independently: -1 slot (it actually frees space by removing the fire control integration). Sensor Array for smoke and darkness: 1 slot. Environmental Seal for the toxic atmosphere: 1 slot. Total: 13 of 20 slots. Plenty of headroom.",body_s))

story.append(Paragraph("The Problem: It\u2019s Not Big Enough",h2_s))
story.append(Paragraph("The engineer presents the Size 8 design. The general looks at the projected height \u2014 about 36 feet \u2014 and shakes her head. \u201cI said <i>over</i> the ridgeline, not peering around it like a nervous infantryman. And I want the enemy to see this thing coming from three valleys away. I want them thinking about surrender before it fires a shot.\u201d",body_s))
story.append(Paragraph("Back to the drawing board. Size 9 \u2014 50 feet tall, 64 tonnes, 22 mod slots. Better height, but the general isn\u2019t thinking about mod budgets. She\u2019s thinking about battlefield psychology. The engineer tries <b>Size 10</b>. Sixty-three feet tall, 125 tonnes, 25 mod slots. Base Toughness jumps to 15 before any slider adjustments. The extra 5 mod slots over the Size 8 prototype are insurance for field refits \u2014 every combat vehicle accumulates modifications once it enters service. And the silhouette, towering over the tree line like something out of a nightmare, is exactly the psychological weapon the general wants. She approves the design.",body_s))

story.append(Paragraph("Dialling In the Stats",h2_s))
story.append(Paragraph("<b>Toughness +2, Armour +3.</b> The Huge frame increments are +4 Toughness and +3 Armour per step. Two Toughness steps add +8. Three Armour steps push the plating to 15 points. Final result: Toughness 38(15). Autocannon fire bounces. Medium lasers splash harmlessly across the glacis. You need a dedicated heavy weapon or a very large gun to make this thing flinch \u2014 and by then, its Heavy Laser has already replied.",body_s))
story.append(Paragraph("<b>MPH Override: 40.</b> Walkers and mechs in fiction move at a deliberate pace that still covers ground faster than infantry. 40 MPH is a brisk stride for something with legs this size \u2014 faster than a WW2 tank, slower than a modern MBT. She closes distance across broken terrain that would stop anything on wheels or tracks. The mountain passes on Kessler IV are exactly the terrain walkers were designed to own.",body_s))
story.append(Paragraph("<b>Handling -2.</b> The Huge frame default is -1, and we drop another step. She doesn\u2019t dodge \u2014 she absorbs. The pilot compensates with sensor data and overwhelming firepower. Handling -2 is the price of 125 tonnes of walking metal, and everyone involved considers it a bargain.",body_s))
story.append(Paragraph("<b>Crew 2.</b> Pilot and gunner in a Dual Cockpit. They operate independently \u2014 no multi-action penalties between manoeuvring and firing. No passengers: she\u2019s a weapons platform, not a troop carrier. Her value is measured in what she destroys, not what she delivers.",body_s))
story.append(Paragraph("<b>Modifications: Heavy Armour, Jump Jets, Dual Cockpit, Sensor Array, Environmental Seal.</b> Heavy Armour is non-negotiable at this weight class. Jump Jets let her clear canyons and drop into firebases \u2014 the general specifically requested this after watching a conventional assault vehicle get stuck in a ravine during the first campaign. Sensor Array halves penalties from smoke, darkness, and concealment \u2014 the mountain passes on Kessler IV are full of all three. Environmental Seal because the planet\u2019s atmosphere will kill an exposed crew in minutes.",body_s))
story.append(Spacer(1,4))
story.append(Paragraph("Size 10 (Huge) \u2022 Handling -2 \u2022 Top Speed 40 MPH \u2022 Toughness 38(15) \u2022 Crew 2 \u2022 Wounds 5",mono_s))
story.append(Paragraph("Weapons: Heavy Laser (Turret), 2\u00d7 Medium Laser (Fixed), Light Missiles \u00d78 (Fixed)",mono_s))
story.append(Paragraph("Notes: Heavy Armour, Jump Jets, Dual Cockpit, Sensor Array, Environmental Seal",mono_s))
story.append(Spacer(1,4))
story.append(Paragraph("There\u2019s no reference build for a walker this size \u2014 and that\u2019s the point. The reference builds cover common archetypes. The slider system handles everything else. Feed it sensible inputs based on what you know about the genre, and the numbers come out right. The general gets her mountain-killer. The engineer gets his dream project. The enemy gets a sixty-three-foot reminder that some problems can\u2019t be solved by digging in.",body_s))
story.append(PageBreak())

# APPENDIX A
story+=[Paragraph("Appendix A: Weapon Reference Tables",h1_s)]+sb()
ERA_L={'ancient':'Ancient','medieval':'Medieval','blackpowder':'Blackpowder','industrial':'Industrial','modern':'Modern','future':'Future','advanced':'Advanced'}
wbe={}
for m in re.finditer(r"\{id:'([^']+)',name:'([^']+)',cat:'([^']+)',era:'([^']+)',range:'([^']+)',damage:'([^']+)',ap:(\d+),rof:(\d+)",wchunk):
    _,name,cat,era,rng,dmg,ap,rof=m.groups();wbe.setdefault(era,[]).append({'name':name,'range':rng,'damage':dmg,'ap':ap,'rof':rof})
for era in['ancient','medieval','blackpowder','industrial','modern','future','advanced']:
    if era not in wbe:continue
    seen=set();dd=[]
    for w in wbe[era]:
        k=w['name']+w['damage']
        if k not in seen:seen.add(k);dd.append(w)
    story+=[Paragraph(f"{ERA_L[era]} ({len(dd)})",h2_s),dt(['Weapon','Range','Damage','AP','RoF'],[[w['name'],w['range'],w['damage'],w['ap'],w['rof']]for w in dd],[2.1*inch,1.1*inch,0.9*inch,0.4*inch,0.4*inch]),Spacer(1,6)]
story.append(PageBreak())

# APPENDIX B
story+=[Paragraph("Appendix B: Keyboard Shortcuts",h1_s)]+sb()+[dt(['Shortcut','Action'],[['Ctrl+S','Save current vehicle'],['Ctrl+E','Export stat block to clipboard'],['Ctrl+N','New vehicle'],['Ctrl+P','Print stat block'],['Ctrl+Z','Undo'],['Ctrl+Shift+Z','Redo'],['Tab','Next slider'],['Shift+Tab','Previous slider'],['Arrow Keys','Adjust selected slider \u00b11']],[1.3*inch,4.8*inch]),PageBreak()]

# APPENDIX C
story+=[Paragraph("Appendix C: Licence and Credits",h1_s)]+sb()+[Paragraph("Savage Worlds Licence",h2_s),Paragraph('This game references the Savage Worlds game system, available from Pinnacle Entertainment Group at <a href="https://www.peginc.com" color="#C4A44A">www.peginc.com</a>. Savage Worlds and all associated logos and trademarks are copyrights of Pinnacle Entertainment Group. Used with permission.',body_s),Paragraph("<b>You will need the Savage Worlds core rules to use this product.</b>",body_s),Paragraph("Fantasy Grounds",h2_s),Paragraph("Fantasy Grounds is a trademark of SmiteWorks USA, LLC. Not affiliated with or endorsed by SmiteWorks.",body_s),Paragraph("Foundry VTT",h2_s),Paragraph("Foundry Virtual Tabletop is a trademark of Foundry Gaming LLC. Not affiliated with or endorsed by Foundry Gaming.",body_s),Paragraph("DiceForge Studios",h2_s),Paragraph(f"Vehicle Forge and all associated content \u00a9 2025\u20132026 DiceForge Studios Ltd. All Rights Reserved. The tool, all {BC} reference builds, all {WC} weapon definitions, all {MC} modifications, and all descriptive text are original DiceForge content. Reference builds are generic vehicle archetypes \u2014 they do not reproduce specific stat lines from any published source.",body_s),Spacer(1,20),Paragraph('<a href="https://diceforgestudios.pages.dev/vehicle-forge.html" color="#C4A44A">https://diceforgestudios.pages.dev/vehicle-forge.html</a>',S('URL',fontSize=9,textColor=GOLD,fontName='Courier',spaceAfter=4))]

# BUILD
out=os.path.join(sd,"vehicle-forge-manual.pdf")
doc=SimpleDocTemplate(out,pagesize=letter,leftMargin=0.7*inch,rightMargin=0.7*inch,topMargin=0.7*inch,bottomMargin=0.7*inch,title="Vehicle Forge Companion Guide",author="DiceForge Studios Ltd.")
def pg(canvas,doc):
    canvas.saveState();canvas.setFillColor(WARM_BG);canvas.rect(0,0,letter[0],letter[1],fill=1,stroke=0)
    canvas.setStrokeColor(GOLD);canvas.setLineWidth(0.5);canvas.line(0.7*inch,0.55*inch,7.8*inch,0.55*inch)
    canvas.setFont('Helvetica',7);canvas.setFillColor(MEDIUM);canvas.drawString(0.7*inch,0.4*inch,f"Vehicle Forge Companion Guide \u2014 {VERSION}")
    canvas.drawRightString(7.8*inch,0.4*inch,f"Page {doc.page}");canvas.setFont('Helvetica',6);canvas.setFillColor(GOLD_DIM)
    canvas.drawCentredString(letter[0]/2,0.4*inch,"DICEFORGE STUDIOS");canvas.restoreState()
doc.build(story,onFirstPage=pg,onLaterPages=pg)
sz=os.path.getsize(out)
from pypdf import PdfReader;r=PdfReader(out);print(f"Vehicle Forge Companion Guide: {sz:,} bytes, {len(r.pages)} pages")
