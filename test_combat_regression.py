#!/usr/bin/env python3
"""
Vehicle Forge — Combat Regression Tests

Validates that weapon stats produce sensible combat outcomes using
Savage Worlds dice mechanics. This is NOT a random simulation — it
tests deterministic properties of the damage/toughness relationship.

Run: python3 test_combat_regression.py
Exit: 0 = all pass, 1 = failures found
"""

import json, re, sys, os


def parse_weapons():
    """Parse weapon catalogue from vehicle-forge.html."""
    with open('vehicle-forge.html') as f:
        html = f.read()
    ws = html.find('var WEAPONS=[')
    we = html.find('];', ws) + 2
    raw = html[ws:we]
    
    weapons = {}
    for wid in re.findall(r"id:\s*'([^']*)'", raw):
        idx = raw.find(f"id:'{wid}'")
        snippet = raw[idx:idx+500]
        w = {'id': wid}
        for field in ['name', 'damage', 'range', 'notes']:
            m = re.search(rf"{field}:\s*'([^']*)'", snippet)
            if m: w[field] = m.group(1)
        for field in ['ap', 'rof', 'shots']:
            m = re.search(rf"{field}:\s*(\d+)", snippet)
            if m: w[field] = int(m.group(1))
        
        # Calculate average damage
        dmg = w.get('damage', '0')
        total = 0
        for term in dmg.replace('-', '+-').split('+'):
            term = term.strip()
            if not term: continue
            m = re.match(r'(\d+)d(\d+)', term)
            if m:
                total += int(m.group(1)) * (int(m.group(2)) + 1) / 2
            else:
                try: total += int(term)
                except: pass
        w['avg'] = total
        weapons[wid] = w
    
    return weapons


def test_sanity_checks(weapons):
    """Core combat-feel validation — these must NEVER change."""
    tests = []
    
    # Test 1: MMG cannot penetrate modern MBT
    mmg = weapons.get('mmg', {})
    # M1A1 Abrams: Toughness ~24(8) → effective Tough = 24 - mmg AP 2 = 22
    # MMG avg damage = 10. Can't reach 22 without multiple raises.
    eff_tough_abrams = 24 - mmg.get('ap', 0)
    tests.append({
        'name': 'MMG bounces off Abrams',
        'pass': mmg.get('avg', 0) < eff_tough_abrams,
        'detail': f"MMG avg {mmg.get('avg',0)} vs eff Tough {eff_tough_abrams}"
    })
    
    # Test 2: 120mm tank gun penetrates T-72
    gun_120 = weapons.get('tank_gun_120mm', {})
    # T-72: Toughness ~20(6) → effective Tough = 20 - 120mm AP
    eff_tough_t72 = 20 - gun_120.get('ap', 0)
    tests.append({
        'name': '120mm penetrates T-72',
        'pass': gun_120.get('avg', 0) > eff_tough_t72,
        'detail': f"120mm avg {gun_120.get('avg',0)} AP {gun_120.get('ap',0)} vs eff Tough {eff_tough_t72}"
    })
    
    # Test 3: Hellfire devastating against T-72
    hellfire = weapons.get('hellfire', {})
    eff_tough_t72_hf = 20 - hellfire.get('ap', 0)
    tests.append({
        'name': 'Hellfire devastates T-72',
        'pass': hellfire.get('avg', 0) > eff_tough_t72_hf + 4,  # At least a raise
        'detail': f"Hellfire avg {hellfire.get('avg',0)} AP {hellfire.get('ap',0)} vs eff Tough {eff_tough_t72_hf}"
    })
    
    # Test 4: Scorpion (ancient) bounces off capital ship
    scorpion = weapons.get('scorpion', {})
    # Dreadnought: Toughness ~54(18)
    eff_tough_dread = 54 - scorpion.get('ap', 0)
    tests.append({
        'name': 'Scorpion bounces off Dreadnought',
        'pass': scorpion.get('avg', 0) < eff_tough_dread,
        'detail': f"Scorpion avg {scorpion.get('avg',0)} vs eff Tough {eff_tough_dread}"
    })
    
    # Test 5: Mega Mass Driver vaporises Age of Sail
    md_mega = weapons.get('md_mega', {})
    # Galleon: Toughness ~16(4)
    eff_tough_galleon = 16 - md_mega.get('ap', 0)
    tests.append({
        'name': 'Mega Mass Driver vaporises Galleon',
        'pass': md_mega.get('avg', 0) > max(eff_tough_galleon + 12, 0),
        'detail': f"MD avg {md_mega.get('avg',0)} vs eff Tough {eff_tough_galleon}"
    })
    
    # Test 6: Light Laser is better than HMG
    laser_light = weapons.get('laser_light', {})
    hmg = weapons.get('hmg', {})
    tests.append({
        'name': 'Light Laser outperforms HMG',
        'pass': laser_light.get('avg', 0) >= hmg.get('avg', 0),
        'detail': f"Light Laser avg {laser_light.get('avg',0)} vs HMG avg {hmg.get('avg',0)}"
    })
    
    # Test 7: Heavy Laser matches SWADE published value (4d10 = avg 22)
    laser_heavy = weapons.get('laser_heavy', {})
    tests.append({
        'name': 'Heavy Laser matches SWADE (4d10, avg ~22)',
        'pass': 20 <= laser_heavy.get('avg', 0) <= 24,
        'detail': f"Heavy Laser avg {laser_heavy.get('avg',0)}"
    })
    
    # Test 8: Weapon families are strictly ordered
    family_tests = [
        ('Lasers', ['laser_light', 'laser_med', 'laser_heavy', 'laser_super', 'laser_sheavy']),
        ('Mass Drivers', ['md_light', 'md_med', 'md_heavy', 'md_super', 'md_superheavy', 'md_mega']),
        ('Particle Beams', ['pb_light', 'pb_med', 'pb_heavy']),
    ]
    
    for family_name, ids in family_tests:
        avgs = [weapons.get(wid, {}).get('avg', 0) for wid in ids if wid in weapons]
        monotonic = all(avgs[i] <= avgs[i+1] for i in range(len(avgs)-1))
        tests.append({
            'name': f'{family_name} family monotonically increasing',
            'pass': monotonic,
            'detail': f"{' → '.join(str(int(a)) for a in avgs)}"
        })
    
    # Test 9: AP increases with weapon tier within families
    ap_families = [
        ('Lasers AP', ['laser_light', 'laser_med', 'laser_heavy', 'laser_super', 'laser_sheavy']),
        ('Mass Drivers AP', ['md_light', 'md_med', 'md_heavy', 'md_super', 'md_superheavy', 'md_mega']),
    ]
    
    for family_name, ids in ap_families:
        aps = [weapons.get(wid, {}).get('ap', 0) for wid in ids if wid in weapons]
        monotonic = all(aps[i] <= aps[i+1] for i in range(len(aps)-1))
        tests.append({
            'name': f'{family_name} monotonically increasing',
            'pass': monotonic,
            'detail': f"{' → '.join(str(a) for a in aps)}"
        })
    
    return tests


def main():
    if not os.path.exists('vehicle-forge.html'):
        print("ERROR: vehicle-forge.html not found. Run from repo root.")
        return 1
    
    weapons = parse_weapons()
    print(f"Loaded {len(weapons)} weapons")
    print()
    
    tests = test_sanity_checks(weapons)
    
    failures = 0
    for t in tests:
        status = "PASS" if t['pass'] else "FAIL"
        if not t['pass']:
            failures += 1
        print(f"  {status}  {t['name']}")
        print(f"         {t['detail']}")
    
    print()
    print(f"Results: {len(tests) - failures}/{len(tests)} passed")
    
    if failures > 0:
        print(f"FAILURES: {failures}")
        return 1
    else:
        print("ALL PASS")
        return 0


if __name__ == '__main__':
    sys.exit(main())
