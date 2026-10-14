"""Platinum encounter tables from the decomp, with friendly location/sub-area names and special daily slots."""
import sys, re, collections
sys.path.insert(0, '/home/claude/scripts')
from decomp import ALL, USED, GM_PRE, GM_POST, TG, sid
import json
LBL = json.load(open('/home/claude/ext/pokeplatinum/include/data/map_headers.h' and '/home/claude/work/match.json'))

def words(s): return ' '.join(w.upper() if re.fullmatch(r'[0-9]+f|b[0-9]+f', w) else w.capitalize() for w in s.split('_'))
CUSTOM = {
    'pokemon_league': ('Pokémon League', ''),
    'valley_windworks_outside': ('Valley Windworks', ''), 'fuego_ironworks_outside': ('Fuego Ironworks', ''),
    'mt_coronet_1f_south': ('Mt. Coronet', '1F south (Routes 207/208)'), 'mt_coronet_1f_tunnel_room': ('Mt. Coronet', '1F back room (to the snowy path)'),
    'mt_coronet_1f_north_room_1': ('Mt. Coronet', '1F Route 211 tunnel'), 'mt_coronet_1f_north_room_2': ('Mt. Coronet', '1F Route 216 entrance'),
    'mt_coronet_4f_rooms_1_and_2': ('Mt. Coronet', '4F'), 'mt_coronet_4f_room_3': ('Mt. Coronet', '4F small room'),
    'mt_coronet_b1f': ('Mt. Coronet', 'B1F (Feebas lake)'), 'mt_coronet_outside_north': ('Mt. Coronet', 'Outside (snowy summit path)'),
    'mt_coronet_outside_south': ('Mt. Coronet', 'Outside (snowy summit path)'),
    'victory_road_1f_room_1': ('Victory Road', 'Back section'), 'victory_road_1f_room_2': ('Victory Road', 'Back section'),
    'victory_road_1f_room_3': ('Victory Road', 'Back section'),
    'stark_mountain_outside': ('Stark Mountain', 'Outside'), 'stark_mountain_room_1': ('Stark Mountain', 'Entrance cave'), 'stark_mountain_room_2': ('Stark Mountain', 'Inner cave'),
    'ruin_maniac_cave_short': ('Ruin Maniac Cave', 'while under 10 Unown forms are seen'), 'ruin_maniac_cave_long': ('Ruin Maniac Cave', 'at 10–25 Unown forms seen'),
    'maniac_tunnel': ('Maniac Tunnel', 'at all 26 Unown forms seen'),
    'iron_island': ('Iron Island', 'Outside'),
    'old_chateau': ('Old Chateau', 'Entrance hall'), 'old_chateau_dining_area': ('Old Chateau', 'Dining room'),
    'lake_verity_low_water': ('Lake Verity', 'early game'), 'lake_verity': ('Lake Verity', 'later'),
    'route_220': ('Sea Route 220', ''), 'route_223': ('Sea Route 223', ''), 'route_226': ('Sea Route 226', ''), 'route_230': ('Sea Route 230', ''),
}
DIR = {'route_204_south': 'south (towards Jubilife)', 'route_204_north': 'north (towards Floaroma)', 'route_205_south': 'south (towards Floaroma)',
       'route_205_north': 'east (towards Eterna)', 'route_210_south': 'south (towards Solaceon)', 'route_210_north': 'west (towards Celestic)',
       'route_211_west': 'west (towards Eterna)', 'route_211_east': 'east (towards Celestic)', 'route_212_north': 'north (towards Hearthome)',
       'route_212_south': 'south/east (towards Pastoria)'}
TOWNS = {'canalave_city', 'eterna_city', 'pastoria_city', 'sunyshore_city', 'twinleaf_town', 'celestic_town', 'resort_area', 'eterna_forest', 'ravaged_path',
         'sendoff_spring', 'trophy_garden', 'lake_valor', 'lake_acuity', 'valor_lakefront', 'acuity_lakefront'}
def name(k):
    if k in CUSTOM: return CUSTOM[k]
    if k in DIR: return ('Route ' + k[6:9], DIR[k])
    if k in TOWNS: return (words(k), '')
    m = re.match(r'route_209_lost_tower_(\w+)', k)
    if m: return ('Lost Tower', m.group(1).upper())
    m = re.match(r'route_(\d+)$', k)
    if m: return ('Route ' + m.group(1), '')
    m = re.match(r'great_marsh_(\d)', k)
    if m: return ('Great Marsh', 'Area ' + m.group(1))
    m = re.match(r'turnback_cave_pillar_(\d)_room_\d', k)
    if m: return ('Turnback Cave', {'1': 'rooms before Pillar 1', '2': 'rooms between Pillars 1 and 2', '3': 'rooms between Pillars 2 and 3'}[m.group(1)])
    for pre, loc in (('oreburgh_mine_', 'Oreburgh Mine'), ('oreburgh_gate_', 'Oreburgh Gate'), ('mt_coronet_', 'Mt. Coronet'), ('victory_road_', 'Victory Road'),
                     ('snowpoint_temple_', 'Snowpoint Temple'), ('wayward_cave_', 'Wayward Cave'), ('iron_island_', 'Iron Island'), ('old_chateau_', 'Old Chateau'),
                     ('solaceon_ruins_', 'Solaceon Ruins')):
        if k.startswith(pre):
            sub = k[len(pre):]
            sub = sub.replace('_left_room', ' left room').replace('_right_room', ' right room').replace('deadend', 'dead_end')
            sub = re.sub(r'(north|south)(east|west)_dead_end', lambda m: m.group(1)[0].upper() + m.group(2)[0].upper() + ' dead end', sub)
            sub = sub.replace('_', ' ').lower()
            sub = ' '.join(w.upper() if re.fullmatch(r'b?\d+f|ne|nw|se|sw', w) else w for w in sub.split())
            return (loc, sub[0].upper() + sub[1:])
    raise KeyError(k)
POST_KEYS = {'victory_road_1f_room_1', 'victory_road_1f_room_2', 'victory_road_1f_room_3'}
POST_NOTE = {'Victory Road|Back section': 'after the Hall of Fame + National Dex (a Collector blocks it until then)'}

def tables():
    """[(key, loc, sub, rows)] rows: (method, conds, species, rate, lo, hi)."""
    out = []
    for k, (d, rows) in ALL.items():
        loc, sub = name(k)
        rows = list(rows)
        if loc == 'Great Marsh':
            land = d['land_encounters']; lv = [land[6]['level'], land[7]['level']]
            for lab, C, tag in (('story-progress-before-national-dex', GM_PRE, 'pre'), ('story-progress-national-dex', GM_POST, 'post')):
                for s, c in C.items(): rows.append(('walk', (f'great-marsh-daily-slot-{c}-of-32-{tag}', lab), s, 10, min(lv), max(lv)))
        if k == 'trophy_garden':
            land = d['land_encounters']; lv = [land[6]['level'], land[7]['level']]
            for s in TG: rows.append(('walk', ('backlot-mentioned', 'story-progress-national-dex'), s, 5, min(lv), max(lv)))
        if any(r[1] and r[1][0].startswith('slot2-') for r in rows):
            rows = [(m, c + ('story-progress-national-dex',), s, r, lo, hi) if c and c[0].startswith('slot2-') else (m, c, s, r, lo, hi) for m, c, s, r, lo, hi in rows]
        out.append((k, loc, sub, rows))
    return out

if __name__ == '__main__':
    seen = collections.defaultdict(list)
    for k, loc, sub, rows in tables(): seen[loc].append(sub or '·')
    for l, s in seen.items(): print(l, '|', s)
