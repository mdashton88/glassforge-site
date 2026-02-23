#!/usr/bin/env python3
"""
Vehicle Forge — Sync & Audit Script
====================================
Run before every commit that touches weapon or vehicle data.

Usage:
    python3 sync_and_audit.py              # Full sync + audit
    python3 sync_and_audit.py --audit-only # Audit without syncing
    python3 sync_and_audit.py --sync-only  # Sync without full audit

Exit codes:
    0 = all clear
    1 = Tier 1 failure (hard canon mismatch — must fix before commit)
    2 = Tier 2 warnings (calibration drift — review before commit)
"""

import json, re, glob, os, sys, hashlib
from datetime import datetime

# ================================================================
# CONFIGURATION
# ================================================================

TOOL_FILE = 'vehicle-forge.html'
ROOT_VFX = 'Vehicle_Forge_Core_Reference_Builds.vfx'
PACKS_DIR = 'packs'

# Files that inherit weapon/vehicle data from the source of truth
DOWNSTREAM_FILES = [
    'vehicle-database.json',
    'packs/00_Core_Tool/Vehicle_Forge_Core_Reference_Builds.vfx',
    'packs/00_Core_Tool/Vehicle_Forge_Core_Reference_Builds.cvf.json',
    'packs/00_Core_Tool/Core_Reference_Builds.cvf.json',
    'v5.0/data/canon-vehicles.json',
    'v5.0/data/swade-core-rebuild.json',
]

# ================================================================
# SWADE HARD CANON — Tier 1 (must match exactly)
# Source: Savage Worlds Adventure Edition pp.79-81
# ================================================================

SWADE_CANON_WEAPONS = {
    'mmg':            {'name': 'Medium Machine Gun',  'damage': '2d8+1',  'ap': 2,  'rof': 3, 'range': '30/60/120'},
    'hmg':            {'name': 'Heavy Machine Gun',   'damage': '2d10',   'ap': 4,  'rof': 3, 'range': '50/100/200'},
    'cannon_20mm':    {'name': '20mm Cannon',         'damage': '2d12',   'ap': 4,  'rof': 4, 'range': '50/100/200'},
    'autocannon_25mm':{'name': '25mm Cannon',         'damage': '3d8',    'ap': 4,  'rof': 3, 'range': '50/100/200'},
    'autocannon_30mm':{'name': '30mm Cannon',         'damage': '3d8',    'ap': 6,  'rof': 3, 'range': '50/100/200'},
    'tank_gun_37mm':  {'name': '37mm Tank Gun',       'damage': '4d8',    'ap': 3,  'rof': 1, 'range': '50/100/200'},
    'tank_gun_75mm':  {'name': '75mm Tank Gun',       'damage': '4d10',   'ap': 6,  'rof': 1, 'range': '75/150/300'},
    'tank_gun_76mm':  {'name': '76mm Tank Gun',       'damage': '4d10',   'ap': 10, 'rof': 1, 'range': '75/150/300'},
    'tank_gun_88mm':  {'name': '88mm Tank Gun',       'damage': '4d10+1', 'ap': 16, 'rof': 1, 'range': '100/200/400'},
    'tank_gun_120mm': {'name': '120mm Tank Gun',      'damage': '5d10',   'ap': 31, 'rof': 1, 'range': '100/200/400'},
    'tank_gun_125mm': {'name': '125mm Tank Gun',      'damage': '5d10',   'ap': 30, 'rof': 1, 'range': '100/200/400'},
    'flamethrower_ww':{'name': 'Heavy Flamethrower',  'damage': '3d8',    'ap': 0,  'rof': 1, 'range': 'Cone'},
    'torpedo_ww':     {'name': 'Torpedo',             'damage': '8d10',   'ap': 22, 'rof': 1, 'range': '300/600/1200'},
    'tow_missile':    {'name': 'TOW Launcher',        'damage': '5d10',   'ap': 34, 'rof': 1, 'range': '75/150/300'},
    'hellfire':       {'name': 'Hellfire Missile',     'damage': '5d10',   'ap': 40, 'rof': 1, 'range': '150/300/600'},
    'sidewinder':     {'name': 'Sidewinder Missile',   'damage': '4d8',    'ap': 6,  'rof': 1, 'range': '100/200/400'},
    'sparrow':        {'name': 'Sparrow Missile',      'damage': '5d8',    'ap': 6,  'rof': 1, 'range': '150/300/600'},
    'laser_gat':      {'name': 'Gatling Laser',       'damage': '3d6+4',  'ap': 4,  'rof': 4, 'range': '50/100/200'},
    'laser_heavy':    {'name': 'Heavy Laser',         'damage': '4d10',   'ap': 30, 'rof': 1, 'range': '150/300/600'},
}

# Era variant pairs — must have identical stats
ERA_VARIANTS = [
    ('mmg', 'mmg_modern'),
    ('hmg', 'hmg_modern'),
    ('tank_gun_37mm', 'tank_gun_light'),
    ('tank_gun_75mm', 'tank_gun_med'),
    ('tank_gun_88mm', 'tank_gun_heavy'),
    ('cannon_20mm', 'autocannon_ww'),
    ('tank_gun_125mm', 'cannon_mod'),
    ('tow_missile', 'atgm'),
]

# Weapon families — damage must increase monotonically
WEAPON_FAMILIES = {
    'Tank Guns':        ['tank_gun_37mm', 'tank_gun_75mm', 'tank_gun_76mm', 'tank_gun_88mm', 'tank_gun_120mm', 'tank_gun_125mm'],
    'Lasers':           ['laser_light', 'laser_med', 'laser_heavy', 'laser_super', 'laser_superheavy', 'laser_mega'],
    'Mass Drivers':     ['md_light', 'md_med', 'md_heavy', 'md_super', 'md_superheavy', 'md_mega'],
    'Particle Beams':   ['pb_light', 'pb_med', 'pb_heavy'],
    'Particle Cannons': ['pc_light', 'pc_med', 'pc_heavy'],
    'Ion Cannons':      ['ion_light', 'ion_med', 'ion_heavy'],
    'Missiles':         ['missile_light', 'missile_med', 'missile_heavy'],
    'Rockets':          ['rocket_light', 'rocket_med', 'rocket_heavy'],
    'Bombs':            ['bomb_light', 'bomb_med', 'bomb_heavy'],
    'BP Cannon':        ['light_cannon_bp', 'med_cannon_bp', 'heavy_cannon_bp'],
    'Autocannons':      ['autocannon_25mm', 'autocannon_30mm', 'autocannon_40mm'],
    'Torpedoes (SFC)':  ['torpedo_light', 'torpedo_med', 'torpedo_heavy'],
}

# ================================================================
# CALIBRATION GRADES — Tier 2
# ================================================================

# Damage grades: (max_avg, grade_label, tolerance)
DAMAGE_GRADES = [
    (7,    'A', 0),   # Light: exact match
    (11,   'B', 1),   # Medium: ±1
    (18,   'C', 2),   # Heavy: ±2
    (28,   'D', 3),   # Very Heavy: ±3
    (9999, 'E', 4),   # Capital: ±4
]

# AP classification bands
# Logic: AP represents penetration capability, not proportional to damage.
#   NONE        = blast, fire, fragmentation (no penetration)
#   LIGHT       = rifle-calibre, bolts, arrows (defeats cover and light skin)
#   MEDIUM      = HMG, autocannon, medium guns (defeats light vehicles)
#   HEAVY       = HVAP, heavy AT, improved penetrators (defeats medium armour)
#   VERY HEAVY  = modern tank guns, shaped charges, torpedoes (defeats heavy armour)
#   CAPITAL     = top-tier guided AT, mega weapons (defeats anything)
AP_BANDS = [
    (0,  0,  'NONE'),
    (1,  2,  'LIGHT'),
    (3,  6,  'MEDIUM'),
    (7,  16, 'HEAVY'),
    (17, 34, 'VERY HEAVY'),
    (35, 99, 'CAPITAL'),
]


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def parse_avg_damage(dmg_str):
    """Calculate average damage from a dice string like '4d10+1'."""
    if not dmg_str or dmg_str in ('—', '', 'Special'):
        return 0
    clean = re.sub(r'Str\+', '', dmg_str)
    avg = 0
    for n, m in re.findall(r'(\d+)d(\d+)', clean):
        avg += int(n) * (int(m) + 1) / 2
    bonus = re.search(r'\+(\d+)', clean)
    if bonus:
        avg += int(bonus.group(1))
    return avg


def get_damage_grade(avg):
    """Return (grade_label, tolerance) for a given average damage."""
    for max_avg, label, tol in DAMAGE_GRADES:
        if avg <= max_avg:
            return label, tol
    return 'E', 4


def get_ap_band(ap):
    """Return the AP band name for a given AP value."""
    for lo, hi, name in AP_BANDS:
        if lo <= ap <= hi:
            return name
    return 'UNKNOWN'


def parse_weapon_catalogue(html):
    """Extract all weapons from var WEAPONS=[] in vehicle-forge.html."""
    ws = html.find('var WEAPONS=')
    we = html.find('];', ws) + 2
    raw = html[ws:we]
    
    weapons = {}
    for wid in re.findall(r"id:\s*'([^']*)'", raw):
        idx = raw.find(f"id:'{wid}'")
        snippet = raw[max(0, idx - 20):idx + 400]
        
        name = re.search(r"name:\s*'([^']*)'", snippet)
        era = re.search(r"era:\s*'([^']*)'", snippet)
        dmg = re.search(r"damage:\s*'([^']*)'", snippet)
        ap = re.search(r"ap:\s*(\d+)", snippet)
        rof = re.search(r"rof:\s*(\d+)", snippet)
        rng = re.search(r"range:\s*'([^']*)'", snippet)
        notes = re.search(r"notes:\s*'([^']*)'", snippet)
        
        weapons[wid] = {
            'name': name.group(1) if name else '?',
            'era': era.group(1) if era else '?',
            'damage': dmg.group(1) if dmg else '',
            'ap': int(ap.group(1)) if ap else 0,
            'rof': int(rof.group(1)) if rof else 0,
            'range': rng.group(1) if rng else '',
            'notes': notes.group(1) if notes else '',
            'avg': parse_avg_damage(dmg.group(1) if dmg else ''),
        }
    return weapons


def parse_canon_builds(html):
    """Extract CANON_BUILDS vehicle data from vehicle-forge.html."""
    builds_start = html.find('var CANON_BUILDS=')
    raw = html[builds_start:]
    
    vehicles = []
    for section in re.split(r'\},\s*\{name:', raw):
        nm = re.search(r'name:"([^"]*)"', section)
        if not nm:
            nm = re.search(r'"([^"]*)"', section)
        if not nm:
            continue
        
        weapons = []
        wmatch = re.search(r'weapons:\[(.*?)\]', section, re.DOTALL)
        if wmatch and wmatch.group(1).strip():
            for wm in re.finditer(
                r'\{[^}]*"weaponId":\s*"([^"]*)"[^}]*"mount":\s*"([^"]*)"[^}]*"linked":\s*(\d+)[^}]*\}',
                wmatch.group(1)
            ):
                weapons.append({
                    'weaponId': wm.group(1),
                    'mount': wm.group(2),
                    'linked': int(wm.group(3)),
                })
        
        vehicles.append({'name': nm.group(1), 'weapons': weapons})
    return vehicles


# ================================================================
# SYNC ENGINE
# ================================================================

def sync_downstream(canon_vfx_path, downstream_files):
    """Propagate corrected vehicle data to all downstream files."""
    with open(canon_vfx_path) as f:
        canon = json.load(f)
    canon_by_name = {v['name']: v for v in canon['vehicles']}
    
    changes = []
    
    for filepath in downstream_files:
        if not os.path.exists(filepath):
            continue
        
        with open(filepath) as f:
            data = json.load(f)
        
        vlist = data.get('vehicles', [])
        file_changes = 0
        
        for v in vlist:
            cv = canon_by_name.get(v.get('name'))
            if not cv:
                continue
            
            old_w = json.dumps(v.get('weapons', []), sort_keys=True)
            new_w = json.dumps(cv.get('weapons', []), sort_keys=True)
            
            if old_w != new_w:
                v['weapons'] = cv['weapons']
                file_changes += 1
        
        if file_changes > 0:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            changes.append(f"  {filepath}: {file_changes} vehicles synced")
        else:
            changes.append(f"  {filepath}: already current")
    
    return changes


# ================================================================
# AUDIT ENGINE
# ================================================================

def audit_tier1(weapons):
    """Tier 1: SWADE Core weapons must match exactly."""
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    for wid, canon in SWADE_CANON_WEAPONS.items():
        ours = weapons.get(wid)
        if not ours:
            results['fail'] += 1
            results['details'].append(f"FAIL  {wid}: missing from catalogue")
            continue
        
        errors = []
        if ours['damage'] != canon['damage']:
            errors.append(f"damage {ours['damage']}≠{canon['damage']}")
        if ours['ap'] != canon['ap']:
            errors.append(f"AP {ours['ap']}≠{canon['ap']}")
        if ours['rof'] != canon['rof']:
            errors.append(f"RoF {ours['rof']}≠{canon['rof']}")
        if ours['range'] != canon['range']:
            errors.append(f"range {ours['range']}≠{canon['range']}")
        
        if errors:
            results['fail'] += 1
            results['details'].append(f"FAIL  {wid}: {', '.join(errors)}")
        else:
            results['pass'] += 1
            results['details'].append(f"PASS  {wid}")
    
    return results


def audit_era_variants(weapons):
    """Check era variant pairs have identical stats."""
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    for id_a, id_b in ERA_VARIANTS:
        wa = weapons.get(id_a)
        wb = weapons.get(id_b)
        if not wa or not wb:
            continue
        
        mismatches = []
        for field in ['damage', 'ap', 'rof', 'range']:
            if wa[field] != wb[field]:
                mismatches.append(f"{field}: {wa[field]}≠{wb[field]}")
        
        if mismatches:
            results['fail'] += 1
            results['details'].append(f"FAIL  {id_a} ↔ {id_b}: {', '.join(mismatches)}")
        else:
            results['pass'] += 1
            results['details'].append(f"PASS  {id_a} ↔ {id_b}")
    
    return results


def audit_family_progression(weapons):
    """Check weapon families have monotonically increasing damage."""
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    for family_name, member_ids in WEAPON_FAMILIES.items():
        members = [(wid, weapons[wid]) for wid in member_ids if wid in weapons]
        members = [(wid, w) for wid, w in members if w['avg'] > 0]
        
        if len(members) < 2:
            continue
        
        prev_avg = -1
        prev_id = None
        family_ok = True
        
        for wid, w in members:
            if w['avg'] < prev_avg:
                results['fail'] += 1
                results['details'].append(
                    f"FAIL  {family_name}: {wid} (avg {w['avg']:.1f}) < {prev_id} (avg {prev_avg:.1f})")
                family_ok = False
                break
            prev_avg = w['avg']
            prev_id = wid
        
        if family_ok:
            avgs = ' → '.join(f"{w['avg']:.0f}" for _, w in members)
            results['pass'] += 1
            results['details'].append(f"PASS  {family_name}: {avgs}")
    
    return results


def audit_calibration(weapons):
    """Tier 2: Check all weapons against calibration grades and AP bands."""
    results = {'pass': 0, 'warn': 0, 'details': []}
    
    for wid, w in weapons.items():
        if w['avg'] == 0:
            continue
        
        grade, tol = get_damage_grade(w['avg'])
        ap_band = get_ap_band(w['ap'])
        
        # Check: does this weapon have a SWADE canon equivalent?
        canon = SWADE_CANON_WEAPONS.get(wid)
        if canon:
            # Tier 1 weapons checked separately — skip here
            continue
        
        # For non-canon weapons, just record their classification
        results['pass'] += 1
        results['details'].append(
            f"OK    {wid:25s}  Grade {grade}  AP [{ap_band:11s}]  "
            f"avg {w['avg']:5.1f}  AP {w['ap']:2d}  {w['name']}")
    
    return results


def audit_pack_integrity(weapons):
    """Check all pack files for broken refs and stale embedded weapon DBs."""
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    total_files = 0
    total_vehicles = 0
    total_mounts = 0
    
    for filepath in sorted(glob.glob(f'{PACKS_DIR}/**/*.vfx', recursive=True)):
        total_files += 1
        
        with open(filepath) as f:
            data = json.load(f)
        
        vlist = data.get('vehicles', [])
        pack_weapons = {}
        for w in data.get('weapons', []):
            if isinstance(w, dict):
                pw_id = w.get('id', w.get('weaponId', ''))
                if pw_id:
                    pack_weapons[pw_id] = w
        
        total_vehicles += len(vlist)
        file_ok = True
        
        # Check embedded weapon stats match canonical
        for pw_id, pw in pack_weapons.items():
            if pw_id in weapons:
                cw = weapons[pw_id]
                for field in ['damage', 'ap', 'rof']:
                    if pw.get(field) is not None and str(pw[field]) != str(cw[field]):
                        results['fail'] += 1
                        results['details'].append(
                            f"FAIL  {os.path.basename(filepath)}: "
                            f"embedded '{pw_id}' {field} {pw[field]}≠{cw[field]}")
                        file_ok = False
        
        # Check vehicle weapon references resolve
        for v in vlist:
            for w in v.get('weapons', []):
                wid = w.get('weaponId', w.get('id', ''))
                total_mounts += 1
                if wid and wid not in weapons and wid not in pack_weapons:
                    results['fail'] += 1
                    results['details'].append(
                        f"FAIL  {os.path.basename(filepath)}: "
                        f"'{v.get('name','?')}' refs '{wid}' — NOT IN CATALOGUE")
                    file_ok = False
        
        if file_ok:
            results['pass'] += 1
    
    results['summary'] = {
        'files': total_files,
        'vehicles': total_vehicles,
        'mounts': total_mounts,
    }
    return results


def audit_downstream_sync(canon_vfx_path, downstream_files):
    """Check if all downstream files are in sync with canon."""
    with open(canon_vfx_path) as f:
        canon = json.load(f)
    canon_by_name = {v['name']: v for v in canon['vehicles']}
    
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    for filepath in downstream_files:
        if not os.path.exists(filepath):
            continue
        
        with open(filepath) as f:
            data = json.load(f)
        
        stale = []
        for v in data.get('vehicles', []):
            cv = canon_by_name.get(v.get('name'))
            if not cv:
                continue
            old_w = json.dumps(v.get('weapons', []), sort_keys=True)
            new_w = json.dumps(cv.get('weapons', []), sort_keys=True)
            if old_w != new_w:
                stale.append(v['name'])
        
        if stale:
            results['fail'] += 1
            results['details'].append(f"STALE {filepath}: {len(stale)} vehicles out of sync")
        else:
            results['pass'] += 1
            results['details'].append(f"SYNC  {filepath}")
    
    return results


# ================================================================
# DESCRIPTION-vs-LOADOUT CONSISTENCY
# ================================================================

# Specific search patterns — each distinctive enough that finding it in
# description text strongly implies the author is referencing THAT weapon.
# Format: (regex_pattern, implied_weapon_family, label)
DESC_WEAPON_PATTERNS = [
    # Calibre-specific guns
    (r'\b37\s*mm\b', ['tank_gun_37mm', 'tank_gun_light'], '37mm gun'),
    (r'\b75\s*mm\b', ['tank_gun_75mm', 'tank_gun_med'], '75mm gun'),
    (r'\b76\s*mm\b', ['tank_gun_76mm'], '76mm gun'),
    (r'\b88\s*mm\b', ['tank_gun_88mm', 'tank_gun_heavy'], '88mm gun'),
    (r'\b120\s*mm\b', ['tank_gun_120mm', 'cannon_mod'], '120mm gun'),
    (r'\b125\s*mm\b', ['tank_gun_125mm', 'cannon_mod'], '125mm gun'),
    (r'\b20\s*mm\b', ['cannon_20mm', 'autocannon_ww', 'autocannon_light', 'autocannon_light_future'], '20mm cannon'),
    (r'\b25\s*mm\b', ['autocannon_25mm', 'autocannon_light', 'autocannon_light_future'], '25mm cannon'),
    (r'\b30\s*mm\b', ['autocannon_30mm', 'autocannon_med', 'autocannon_light', 'autocannon_light_future'], '30mm cannon'),
    (r'\b40\s*mm\b', ['autocannon_40mm', 'autocannon_med', 'autocannon_light_future'], '40mm cannon'),
    # Named missiles
    (r'\bhellfire\b', ['hellfire', 'atgm', 'missile_heavy'], 'Hellfire'),
    (r'\bsidewinder\b', ['sidewinder', 'sam'], 'Sidewinder'),
    (r'\bsparrow\b', ['sparrow', 'sam'], 'Sparrow'),
    (r'\btow\s+(?:missile|launcher)\b', ['tow_missile', 'atgm'], 'TOW'),
    # Specific weapon types
    (r'\btrebuchet\b', ['trebuchet'], 'trebuchet'),
    (r'\bballista[e]?\b', ['ballista'], 'ballista'),
    (r'\bcatapult\b', ['catapult'], 'catapult'),
    (r'\bscorpion\b', ['scorpion'], 'scorpion'),
    (r'\bgreek\s+fire\b', ['greek_fire_s'], 'Greek fire'),
    (r'\bgatling\s+laser\b', ['laser_gat'], 'Gatling Laser'),
    (r'\bheavy\s+laser\b', ['laser_heavy'], 'Heavy Laser'),
    (r'\bmedium\s+laser\b', ['laser_med'], 'Medium Laser'),
    (r'\brailgun\b', ['railgun'], 'Railgun'),
    (r'\bflamethrower\b', ['flamethrower_ww', 'flamethrower_mod', 'flamethrower_future'], 'Flamethrower'),
    (r'\bplasma\s+cannon\b', ['plasma_cannon'], 'Plasma Cannon'),
    (r'\bmass\s+driver\b', ['md_light', 'md_med', 'md_heavy', 'md_super', 'md_superheavy', 'md_mega'], 'Mass Driver'),
    (r'\bparticle\s+beam\b', ['pb_light', 'pb_med', 'pb_heavy'], 'Particle Beam'),
    (r'\bparticle\s+cannon\b', ['pc_light', 'pc_med', 'pc_heavy'], 'Particle Cannon'),
    (r'\bion\s+cannon\b', ['ion_light', 'ion_med', 'ion_heavy'], 'Ion Cannon'),
]


def audit_desc_vs_loadout(weapons):
    """Check vehicle descriptions don't reference weapons missing from loadout."""
    results = {'pass': 0, 'warn': 0, 'details': []}
    
    for vfx in sorted(glob.glob(f'{PACKS_DIR}/**/*.vfx', recursive=True)):
        with open(vfx) as f:
            data = json.load(f)
        pack_name = os.path.basename(vfx)
        
        for v in data.get('vehicles', []):
            loadout_ids = set(w.get('weaponId', '') for w in v.get('weapons', []))
            if not loadout_ids:
                continue
            
            text = (v.get('desc', '') + ' ' + v.get('notes', '')).lower()
            if not text.strip():
                continue
            
            vehicle_ok = True
            for pattern, valid_ids, label in DESC_WEAPON_PATTERNS:
                if re.search(pattern, text):
                    if not set(valid_ids).intersection(loadout_ids):
                        loadout_names = [weapons.get(w, {}).get('name', w) for w in sorted(loadout_ids)]
                        results['warn'] += 1
                        results['details'].append(
                            f"WARN  {pack_name}: {v.get('name', '?')} — "
                            f"text mentions '{label}' but loadout is: "
                            f"{', '.join(loadout_names)}")
                        vehicle_ok = False
            
            if vehicle_ok:
                results['pass'] += 1
    
    return results


def audit_canonical_backup(weapons):
    """Verify canonical-weapons.json matches source of truth."""
    backup_path = 'canonical-weapons.json'
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    if not os.path.exists(backup_path):
        results['fail'] += 1
        results['details'].append(f"MISSING  {backup_path} does not exist — run full sync to generate")
        return results
    
    with open(backup_path) as f:
        backup = json.load(f)
    
    backup_by_id = {w['id']: w for w in backup.get('weapons', [])}
    
    # Count check
    if len(backup_by_id) != len(weapons):
        results['fail'] += 1
        results['details'].append(
            f"COUNT   backup has {len(backup_by_id)} weapons, source has {len(weapons)}")
    
    # Stat check
    mismatches = 0
    for wid, w in weapons.items():
        bw = backup_by_id.get(wid)
        if not bw:
            mismatches += 1
            results['details'].append(f"MISSING  {wid} not in backup")
            continue
        for field in ['damage', 'ap', 'rof']:
            if str(w.get(field, '')) != str(bw.get(field, '')):
                mismatches += 1
                results['details'].append(
                    f"DRIFT   {wid}.{field}: source={w.get(field)} backup={bw.get(field)}")
    
    if mismatches == 0:
        results['pass'] = 1
        results['details'].append(f"MATCH   {len(weapons)} weapons verified against backup")
    else:
        results['fail'] = 1
    
    return results


def audit_vehicle_backup():
    """Verify canonical-vehicles.json matches source of truth."""
    backup_path = 'canonical-vehicles.json'
    canon_path = ROOT_VFX
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    if not os.path.exists(backup_path):
        results['fail'] += 1
        results['details'].append(f"MISSING  {backup_path} does not exist")
        return results
    
    if not os.path.exists(canon_path):
        results['fail'] += 1
        results['details'].append(f"MISSING  {canon_path} does not exist")
        return results
    
    with open(backup_path) as f:
        backup = json.load(f)
    with open(canon_path) as f:
        canon = json.load(f)
    
    backup_by_name = {v['name']: v for v in backup.get('vehicles', [])}
    canon_by_name = {v['name']: v for v in canon.get('vehicles', [])}
    
    if len(backup_by_name) != len(canon_by_name):
        results['fail'] += 1
        results['details'].append(
            f"COUNT   backup has {len(backup_by_name)} vehicles, canon has {len(canon_by_name)}")
        return results
    
    mismatches = 0
    for name, cv in canon_by_name.items():
        bv = backup_by_name.get(name)
        if not bv:
            mismatches += 1
            results['details'].append(f"MISSING  '{name}' not in backup")
            continue
        cw = json.dumps(cv.get('weapons', []), sort_keys=True)
        bw = json.dumps(bv.get('weapons', []), sort_keys=True)
        if cw != bw:
            mismatches += 1
            results['details'].append(f"DRIFT   '{name}' weapon loadout differs")
    
    if mismatches == 0:
        results['pass'] = 1
        results['details'].append(f"MATCH   {len(canon_by_name)} vehicles verified against backup")
    else:
        results['fail'] = 1
    
    return results


def audit_specials_backup(html):
    """Verify canonical-specials.json matches source of truth."""
    backup_path = 'canonical-specials.json'
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    if not os.path.exists(backup_path):
        results['fail'] += 1
        results['details'].append(f"MISSING  {backup_path}")
        return results
    
    # Parse specials from HTML
    ss = html.find('var SPECIALS=[')
    se = html.find('];', ss) + 2
    raw = html[ss:se]
    source_ids = set(re.findall(r"id:\s*'([^']*)'", raw))
    
    with open(backup_path) as f:
        backup = json.load(f)
    backup_ids = set(s['id'] for s in backup.get('specials', []))
    
    if source_ids == backup_ids:
        results['pass'] = 1
        results['details'].append(f"MATCH   {len(source_ids)} specials verified")
    else:
        results['fail'] = 1
        for sid in source_ids - backup_ids:
            results['details'].append(f"MISSING  {sid} not in backup")
        for sid in backup_ids - source_ids:
            results['details'].append(f"EXTRA   {sid} in backup but not source")
    
    return results


def audit_mods_backup(html):
    """Verify canonical-mods.json matches source of truth."""
    backup_path = 'canonical-mods.json'
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    if not os.path.exists(backup_path):
        results['fail'] += 1
        results['details'].append(f"MISSING  {backup_path}")
        return results
    
    ms = html.find('var MODS=[')
    me = html.find('];', ms) + 2
    raw = html[ms:me]
    source_ids = set(re.findall(r"id:\s*'([^']*)'", raw))
    
    with open(backup_path) as f:
        backup = json.load(f)
    backup_ids = set(m['id'] for m in backup.get('mods', []))
    
    if source_ids == backup_ids:
        results['pass'] = 1
        results['details'].append(f"MATCH   {len(source_ids)} mods verified")
    else:
        results['fail'] = 1
        for mid in source_ids - backup_ids:
            results['details'].append(f"MISSING  {mid} not in backup")
        for mid in backup_ids - source_ids:
            results['details'].append(f"EXTRA   {mid} in backup but not source")
    
    return results


# ================================================================
# SPECIALS CROSS-REFERENCE
# ================================================================

SPECIAL_PATTERNS = [
    (r'\bheavy\s+armou?r\b', 'heavy_armor', 'Heavy Armor'),
    (r'\bshallow\s+draft\b', 'shallow_draft', 'Shallow Draft'),
    (r'\bamphibious\b', 'amphibious', 'Amphibious'),
    (r'\bfour[\s-]wheel\s+drive\b', 'four_wd', 'Four Wheel Drive'),
    (r'\b4wd\b', 'four_wd', 'Four Wheel Drive'),
    (r'\ball[\s-]terrain\b', 'all_terrain', 'All-Terrain'),
    (r'\bstealth\b', 'stealth', 'Stealth'),
    (r'\bejection\s+(seat|system)\b', 'ejection', 'Ejection System'),
    (r'\bsmoke\s+screen\b', 'smoke_screen', 'Smoke Screen'),
    (r'\bflares\b', 'flares', 'Flares / Chaff'),
    (r'\bchaff\b', 'flares', 'Flares / Chaff'),
    (r'\bfireproof\b', 'fireproof', 'Fireproof'),
    (r'\bsealed\b', 'sealed', 'Sealed'),
    (r'\bpressuri[sz]ed\b', 'pressurised', 'Pressurised'),
    (r'\bhaunted\b', 'haunted', 'Haunted'),
    (r'\bsentient\b', 'sentient', 'Sentient'),
    (r'\bcursed\b', 'cursed', 'Cursed'),
    (r'\btemperamental\b', 'temperamental', 'Temperamental'),
    (r'\bunreliable\b', 'unreliable', 'Unreliable System'),
    (r'\bprototype\b', 'prototype', 'Prototype'),
    (r'\bram\s+plate\b', 'ram_plate', 'Ram Plate'),
    (r'\bopen[\s-]top\b', 'open_top', 'Open Top'),
]


def audit_specials_vs_desc():
    """Check vehicle descriptions don't reference specials the vehicle lacks."""
    results = {'pass': 0, 'warn': 0, 'details': []}
    
    for vfx in sorted(glob.glob(f'{PACKS_DIR}/**/*.vfx', recursive=True)):
        with open(vfx) as f:
            data = json.load(f)
        pack_name = os.path.basename(vfx)
        
        for v in data.get('vehicles', []):
            text = (v.get('desc', '') + ' ' + v.get('notes', '')).lower()
            if not text.strip():
                continue
            
            vehicle_specials = set(v.get('specials', []))
            vehicle_ok = True
            
            for pattern, special_id, label in SPECIAL_PATTERNS:
                if re.search(pattern, text) and special_id not in vehicle_specials:
                    results['warn'] += 1
                    results['details'].append(
                        f"WARN  {pack_name}: {v.get('name', '?')} — "
                        f"text mentions '{label}' but special not assigned")
                    vehicle_ok = False
            
            if vehicle_ok:
                results['pass'] += 1
    
    return results


# ================================================================
# IP COMPLIANCE
# ================================================================

IP_RED_FLAGS = [
    (r'\bClass\s+(I|II|III|IV|V|VI|VII)\b', 'SFC Class numeral'),
    (r'\bStar[Ff]inder\b', 'Starfinder reference'),
    (r'\bFan\s+Companion\b', 'Fan Companion reference'),
    (r'\bMedium\s+Maser\b', 'SFC weapon name'),
    (r'\bHeavy\s+Maser\b', 'SFC weapon name'),
    (r'\bSuper\s+Maser\b', 'SFC weapon name'),
    (r'\bMedium\s+Torpedo\s+Tube\b', 'SFC weapon name'),
    (r'Toughness:\s*\d+\s*\(\d+\)', 'Possible reproduced stat block'),
]


def audit_ip_compliance():
    """Scan pack descriptions for potential IP violations."""
    results = {'pass': 0, 'warn': 0, 'details': []}
    
    for vfx in sorted(glob.glob(f'{PACKS_DIR}/**/*.vfx', recursive=True)):
        with open(vfx) as f:
            data = json.load(f)
        pack_name = os.path.basename(vfx)
        pack_clean = True
        
        for v in data.get('vehicles', []):
            for field in ['desc', 'notes']:
                text = v.get(field, '')
                if not text:
                    continue
                for pattern, label in IP_RED_FLAGS:
                    m = re.search(pattern, text)
                    if m:
                        results['warn'] += 1
                        results['details'].append(
                            f"WARN  {pack_name}: {v.get('name', '?')}.{field} — "
                            f"'{m.group(0)}' ({label})")
                        pack_clean = False
        
        if pack_clean:
            results['pass'] += 1
    
    return results


# ================================================================
# MAIN
# ================================================================

def main():
    mode = 'full'
    if '--audit-only' in sys.argv:
        mode = 'audit'
    elif '--sync-only' in sys.argv:
        mode = 'sync'
    
    print("=" * 80)
    print("VEHICLE FORGE — SYNC & AUDIT")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {mode}")
    print("=" * 80)
    
    # Load source of truth
    with open(TOOL_FILE) as f:
        html = f.read()
    
    weapons = parse_weapon_catalogue(html)
    print(f"\nSource of truth: {len(weapons)} weapons in catalogue")
    
    exit_code = 0
    
    # ── SYNC ──
    if mode in ('full', 'sync'):
        print(f"\n{'─' * 80}")
        print("SYNC: Propagating canon data to downstream files")
        print(f"{'─' * 80}")
        
        if os.path.exists(ROOT_VFX):
            changes = sync_downstream(ROOT_VFX, DOWNSTREAM_FILES)
            for c in changes:
                print(c)
        else:
            print(f"  ⚠ {ROOT_VFX} not found — skipping sync")
    
    # ── AUDIT ──
    if mode in ('full', 'audit'):
        
        # Tier 1: Hard Canon
        print(f"\n{'─' * 80}")
        print("TIER 1: SWADE Core Weapons (must match exactly)")
        print(f"{'─' * 80}")
        
        t1 = audit_tier1(weapons)
        for d in t1['details']:
            print(f"  {d}")
        print(f"\n  Result: {t1['pass']}/{t1['pass'] + t1['fail']}")
        if t1['fail'] > 0:
            exit_code = 1
        
        # Era Variants
        print(f"\n{'─' * 80}")
        print("ERA VARIANTS: Paired weapons must have identical stats")
        print(f"{'─' * 80}")
        
        ev = audit_era_variants(weapons)
        for d in ev['details']:
            print(f"  {d}")
        print(f"\n  Result: {ev['pass']}/{ev['pass'] + ev['fail']}")
        if ev['fail'] > 0:
            exit_code = max(exit_code, 1)
        
        # Family Progression
        print(f"\n{'─' * 80}")
        print("FAMILY PROGRESSION: Damage must increase within weapon families")
        print(f"{'─' * 80}")
        
        fp = audit_family_progression(weapons)
        for d in fp['details']:
            print(f"  {d}")
        print(f"\n  Result: {fp['pass']}/{fp['pass'] + fp['fail']}")
        if fp['fail'] > 0:
            exit_code = max(exit_code, 2)
        
        # Pack Integrity
        print(f"\n{'─' * 80}")
        print("PACK INTEGRITY: All weapon refs resolve, embedded DBs match")
        print(f"{'─' * 80}")
        
        pi = audit_pack_integrity(weapons)
        for d in pi['details']:
            if 'FAIL' in d:
                print(f"  {d}")
        s = pi.get('summary', {})
        print(f"\n  Files: {s.get('files', 0)}, Vehicles: {s.get('vehicles', 0)}, "
              f"Mounts: {s.get('mounts', 0)}")
        print(f"  Result: {pi['pass']} packs clean, {pi['fail']} issues")
        if pi['fail'] > 0:
            exit_code = max(exit_code, 1)
        
        # Downstream Sync
        print(f"\n{'─' * 80}")
        print("DOWNSTREAM SYNC: Secondary files match canon")
        print(f"{'─' * 80}")
        
        if os.path.exists(ROOT_VFX):
            ds = audit_downstream_sync(ROOT_VFX, DOWNSTREAM_FILES)
            for d in ds['details']:
                print(f"  {d}")
            print(f"\n  Result: {ds['pass']}/{ds['pass'] + ds['fail']}")
            if ds['fail'] > 0:
                exit_code = max(exit_code, 1)
        
        # Tier 2: Calibration Summary
        print(f"\n{'─' * 80}")
        print("TIER 2: Calibration Classification")
        print(f"{'─' * 80}")
        print(f"""
  Damage Grades:
    A (avg ≤7):   ±0 exact    B (avg 7-11):  ±1
    C (avg 11-18): ±2         D (avg 18-28): ±3
    E (avg 28+):   ±4

  AP Bands:
    NONE (0)       LIGHT (1-2)     MEDIUM (3-6)
    HEAVY (7-16)   VERY HEAVY (17-34)   CAPITAL (35+)""")
        
        # Count weapons per grade and band
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        band_counts = {b[2]: 0 for b in AP_BANDS}
        
        for wid, w in weapons.items():
            if w['avg'] > 0:
                grade, _ = get_damage_grade(w['avg'])
                grade_counts[grade] += 1
                band = get_ap_band(w['ap'])
                band_counts[band] += 1
        
        print(f"\n  By Grade: {', '.join(f'{k}={v}' for k, v in grade_counts.items())}")
        print(f"  By AP Band: {', '.join(f'{k}={v}' for k, v in band_counts.items())}")
        
        # Content Integrity: Description vs Loadout
        print(f"\n{'─' * 80}")
        print("CONTENT INTEGRITY: Description text matches weapon loadout")
        print(f"{'─' * 80}")
        
        dl = audit_desc_vs_loadout(weapons)
        for d in dl['details']:
            print(f"  {d}")
        print(f"\n  Result: {dl['pass']} vehicles clean, {dl['warn']} warnings")
        if dl['warn'] > 0:
            exit_code = max(exit_code, 2)
        
        # Content Integrity: Specials vs Description
        print(f"\n{'─' * 80}")
        print("CONTENT INTEGRITY: Description text matches specials loadout")
        print(f"{'─' * 80}")
        
        sp = audit_specials_vs_desc()
        for d in sp['details']:
            print(f"  {d}")
        print(f"\n  Result: {sp['pass']} vehicles clean, {sp['warn']} warnings")
        if sp['warn'] > 0:
            exit_code = max(exit_code, 2)
        
        # IP Compliance
        print(f"\n{'─' * 80}")
        print("IP COMPLIANCE: No SFC or Pinnacle content in descriptions")
        print(f"{'─' * 80}")
        
        ip = audit_ip_compliance()
        for d in ip['details']:
            print(f"  {d}")
        if ip['warn'] == 0:
            print(f"  ✓ {ip['pass']} packs clean — no IP issues found")
        else:
            print(f"\n  Result: {ip['warn']} warnings")
            exit_code = max(exit_code, 2)
        
        # Canonical Backups
        print(f"\n{'─' * 80}")
        print("CANONICAL BACKUPS: All backups match source of truth")
        print(f"{'─' * 80}")
        
        cb = audit_canonical_backup(weapons)
        for d in cb['details']:
            print(f"  {d}")
        if cb['fail'] > 0:
            exit_code = max(exit_code, 2)
        
        vb = audit_vehicle_backup()
        for d in vb['details']:
            print(f"  {d}")
        if vb['fail'] > 0:
            exit_code = max(exit_code, 2)
        
        sb = audit_specials_backup(html)
        for d in sb['details']:
            print(f"  {d}")
        if sb['fail'] > 0:
            exit_code = max(exit_code, 2)
        
        mb = audit_mods_backup(html)
        for d in mb['details']:
            print(f"  {d}")
        if mb['fail'] > 0:
            exit_code = max(exit_code, 2)
    
    # ── SUMMARY ──
    print(f"\n{'=' * 80}")
    if exit_code == 0:
        print("ALL CLEAR — safe to commit")
    elif exit_code == 1:
        print("TIER 1 FAILURE — fix before committing")
    elif exit_code == 2:
        print("TIER 2 WARNINGS — review before committing")
    print(f"{'=' * 80}")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
