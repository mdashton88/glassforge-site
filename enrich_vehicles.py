#!/usr/bin/env python3
"""Enrich vehicle descriptions and GM notes in .vfx and .cvf.json packs."""
import json, os, sys

# Each entry: vehicle name -> (new_desc, gm_notes)
# Descriptions: 2-3 sentences, atmospheric, tactical character
# Notes: Adventure hooks, tactical tips, NPC seeds

ENRICHMENTS = {

# ═══ WWI IRON HARVEST ═══

"Mark I (Male)": (
    "The first tank to see combat, lumbering across no man's land at Flers-Courcelette in September 1916. Two 6-pounder naval guns in sponson mounts give it genuine anti-fortification punch, but the crew of eight work in a deafening, fume-choked steel coffin that regularly exceeds 50 degrees inside.",
    "Crew morale is the real enemy. Vigour rolls against Heat every 30 minutes of operation or suffer Fatigue. The shock value against troops who've never seen a tank is enormous — enemies must make Spirit rolls or break. First contact scenarios are pure gold."
),

"Mark I (Female)": (
    "The anti-infantry variant trades its sponson cannons for Vickers machine guns, designed to sweep trenches and suppress defenders during an assault. Crews call them 'Females' with genuine affection — they're marginally less hellish to operate than the gun-armed Males, though the distinction is academic when you're boiling alive at walking pace.",
    "Pairs beautifully with a Male for combined arms. The Female suppresses the trench line while the Male knocks out strongpoints. NPC seed: a Female crew who refuse to be reassigned to Males because 'our girl keeps us alive.'"
),

"Mark IV": (
    "The workhorse of Cambrai and the most-produced British heavy tank of the war. Thicker armour defeats the German K-bullet that made earlier Marks vulnerable, and an external fuel tank reduces the catastrophic fire risk that haunted the Mark I. Still murderously slow, still a crew of eight, still an oven on tracks.",
    "The Mark IV is what most people mean when they say 'WWI tank.' Perfect as the default vehicle for any Great War armoured scenario. At Cambrai, 476 went forward on the first day. NPC seed: a veteran driver who survived Flers in a Mark I and considers the IV 'luxury.'"
),

"Medium Mark A Whippet": (
    "Built for exploitation and pursuit, the Whippet is everything the heavy Marks are not — fast, relatively agile, and designed to pour through gaps in the enemy line. Four machine guns give it fearsome anti-infantry firepower, and at 8 mph it can actually keep pace with advancing troops. Crews love them. Infantry love them more.",
    "The Whippet is the cavalry arm. Use it for pursuit scenarios after a breakthrough, flanking actions, or raids behind the lines. The most famous Whippet, 'Musical Box,' fought alone behind German lines for nine hours. That's an entire session right there."
),

"A7V Sturmpanzerwagen": (
    "Germany's answer to the British tank, and a terrifying one. A 57mm Maxim-Nordenfelt cannon in the front, six machine guns covering every arc, and a crew of eighteen crammed into a riveted steel box the size of a small house. Only twenty were ever built, making each one a precious and prestigious command. Top-heavy, mechanically fragile, and utterly lethal when it works.",
    "The A7V is a boss encounter. It's rare, it's imposing, and it carries enough crew to populate a small adventure. NPC seed: the commander is an aristocratic cavalry officer who considers tank warfare beneath him but knows it's the future. The first tank-versus-tank battle in history (Villers-Bretonneux, 1918) was A7Vs against Mark IVs."
),

"Renault FT-17": (
    "The tank that invented the modern tank. First vehicle with a fully rotating turret, first to separate the crew from the engine, first to put the armament in a turret rather than the hull. Small, cheap, and produced in their thousands, the FT-17 gave commanders something the heavy tanks couldn't: mass. Two-man crew means it's intimate, cramped, and utterly dependent on the commander doing everything except drive.",
    "The FT-17 works best in swarms. A single one is vulnerable; five of them are terrifying. Perfect for scenarios where quantity matters more than quality. NPC seed: a commander-gunner who's been in the same FT with the same driver for six months and they communicate entirely in hand signals because you can't hear anything inside."
),

"Mark V": (
    "The final evolution of the British rhomboid tank, and the first a single driver can actually control without the help of two gearsmen. Wilson's epicyclic gearing is a genuine revolution — the Mark V handles like a vehicle rather than a committee decision. Thicker armour, a more powerful engine, and slightly less chance of cooking the crew alive.",
    "The Mark V is the 'premium' British tank for late-war scenarios. Use it when the PCs have earned better equipment or when the scenario demands reliability. NPC seed: a gearsman made redundant by the new transmission who's been retrained as a gunner and resents the machine that took his old job."
),

"Saint-Chamond": (
    "A French assault tank built around a 75mm field gun mounted in the hull front. Electrically driven, which makes it quieter than its petrol-driven rivals but gives it a distinctive whine that experienced troops learn to dread. The hull overhangs the tracks badly, making it prone to ditching on rough ground — and the Western Front is nothing but rough ground.",
    "The Saint-Chamond is the glass cannon of WWI. That 75mm gun hits hard but the vehicle itself gets stuck constantly. Driving rolls at -2 in shell-cratered terrain. NPC seed: the electrician who keeps the drive system running is the most important person in the crew and knows it."
),

"Schneider CA1": (
    "The first French tank, and it shows. Essentially an armoured box bolted onto a Holt tractor chassis, with a short 75mm gun in a limited-traverse mount and two machine guns. The fuel tanks are poorly positioned and the armour is just thick enough to stop rifle rounds but not much else. Brave crews call them 'moving coffins' and mean it as a compliment.",
    "The Schneider is the 'early war desperate measure' tank. Use it when the situation is bad enough that command is sending everything they have. Fire risk is the defining characteristic — any Wound has a 1-in-4 chance of igniting the fuel. NPC seed: a crew who've survived two Schneiders burning out from under them and are starting their third."
),

"Rolls-Royce Armoured Car": (
    "An elegant Silver Ghost chassis wrapped in armour plate and topped with a rotating turret mounting a Vickers machine gun. Fast on roads, useless in mud, and beloved by officers who appreciate that it still handles like a Rolls-Royce. Lawrence of Arabia used them to devastating effect in the desert, where the flat terrain let them do what trenches never could.",
    "The armoured car is the mobility option. Useless in trench warfare, lethal in the open. Perfect for Middle Eastern campaigns, pursuit actions on roads, or rear-area security. NPC seed: the driver is a former chauffeur who treats the vehicle with the same care he gave his employer's touring car, and woe betide anyone who scratches the paintwork."
),

}


def enrich_file(filepath):
    """Update descriptions and notes in a .vfx or .cvf.json file."""
    with open(filepath) as f:
        data = json.load(f)
    
    # Determine vehicle list location
    vehicles = data.get('vehicles', data if isinstance(data, list) else [])
    is_vfx = 'vehicles' in data
    
    updated = 0
    for v in vehicles:
        name = v.get('name', '')
        if name in ENRICHMENTS:
            new_desc, new_notes = ENRICHMENTS[name]
            v['desc'] = new_desc
            v['notes'] = new_notes
            updated += 1
    
    if updated:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  Updated {updated} vehicles in {os.path.basename(filepath)}")
    return updated


def main():
    pack_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            "glassforge-site", "packs")
    if not os.path.exists(pack_dir):
        pack_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "packs")
    
    total = 0
    for root, dirs, files in os.walk(pack_dir):
        for fn in sorted(files):
            if fn.endswith('.vfx') or fn.endswith('.cvf.json'):
                path = os.path.join(root, fn)
                total += enrich_file(path)
    
    print(f"\nTotal: {total} vehicles enriched across all packs.")


if __name__ == "__main__":
    main()
