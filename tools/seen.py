"""For each Sinnoh Dex species: which trainers use it, where, in story order (from pret/pokeplatinum)."""
import json, re, collections, sys
sys.path.insert(0, '/home/claude/scripts')
from evo import NAMES
RES = '/home/claude/ext/pokeplatinum/res/'
trmap = json.load(open('/home/claude/work/trmap.json'))
sinnoh = json.load(open('/home/claude/work/sinnoh.json'))
SPC = {v.upper().replace('♀', '_F').replace('♂', '_M').replace('. ', '_').replace('.', '').replace('’', '').replace("'", '').replace(' ', '_').replace('-', '_'): k for k, v in NAMES.items()}
SPC['MR_MIME'] = 122; SPC['MIME_JR'] = 439; SPC['PORYGON_Z'] = 474; SPC['HO_OH'] = 250; SPC['FARFETCHD'] = 83; SPC['NIDORAN_F'] = 29; SPC['NIDORAN_M'] = 32

ORDER = ['trainers_school', 'route_202', 'jubilife_city', 'route_203', 'oreburgh_gate', 'oreburgh_mine', 'oreburgh_city_gym', 'route_204_south', 'route_204_north',
         'floaroma_meadow', 'valley_windworks', 'route_205_south', 'eterna_forest', 'route_205_north', 'team_galactic_eterna_building', 'eterna_city_gym',
         'route_211_west', 'mt_coronet_1f_tunnel', 'route_206', 'wayward_cave', 'route_207', 'route_208', 'hearthome_city_gym', 'route_209', 'solaceon_ruins',
         'route_210_south', 'route_215', 'veilstone_city_gym', 'route_214', 'valor_lakefront', 'restaurant', 'route_213', 'pastoria_city', 'route_212_south',
         'route_212_north', 'pokemon_mansion', 'cafe', 'celestic_town', 'route_210_north', 'route_211_east', 'route_218', 'canalave_city', 'iron_island',
         'veilstone_city', 'lake_valor', 'valor_cavern', 'lake_verity', 'route_216', 'route_217', 'snowpoint_city_gym', 'galactic_hq', 'mt_coronet',
         'spear_pillar', 'distortion_world', 'route_219', 'route_220', 'route_221', 'route_222', 'sunyshore_city_gym', 'route_223', 'victory_road',
         'pokemon_league', 'fuego_ironworks', 'route_224', 'fight_area', 'route_225', 'survival_area', 'route_226', 'route_227', 'stark_mountain',
         'route_228', 'route_229', 'route_230', 'pokemon_league_north']
POST = {'route_224', 'fight_area', 'route_225', 'survival_area', 'route_226', 'route_227', 'stark_mountain', 'route_228', 'route_229', 'route_230', 'pokemon_league_north', 'fuego_ironworks'}
def order_of(m):
    best = None
    for k, pre in enumerate(ORDER):
        if m.startswith(pre) and (best is None or len(pre) > len(ORDER[best])): best = k
    return best if best is not None else 999
def area(m):
    k = order_of(m); return ORDER[k] if k < 999 else m

def pretty_map(m):
    special = {'trainers_school': "Jubilife Trainers' School", 'restaurant': 'Veilstone Restaurant (Route 212)', 'cafe': 'Café Cabin (Route 210)',
               'pokemon_mansion': 'Pokémon Mansion (Route 212)', 'distortion_world_b7f': 'Distortion World', 'celestic_town_cave': 'Celestic Town ruins',
               'route_222_west_house': 'Route 222 house', 'pokemon_league_north_pokecenter_1f': 'Pokémon League (north)',
               'pokemon_league_champion_room': 'Pokémon League — Champion', 'lake_valor_drained': 'Lake Valor', 'fuego_ironworks_building': 'Fuego Ironworks'}
    if m in special: return special[m]
    mm = re.match(r'pokemon_league_(\w+)_room', m)
    if mm: return f'Pokémon League — Elite Four {mm.group(1).title()}'
    mm = re.match(r'(\w+?)_city_gym', m)
    if mm: return mm.group(1).replace('_', ' ').title() + ' Gym'
    s = m.replace('team_galactic_eterna_building', 'Galactic Eterna Building').replace('galactic_hq', 'Galactic HQ').replace('route_209_lost_tower', 'Lost Tower')
    s = re.sub(r'_(\d)f', r' \1F', s); s = re.sub(r'_b(\d)f', r' B\1F', s)
    s = re.sub(r'_room_\d+|_rooms_\d+_and_\d+|_tunnel_room|_left_room|_right_room|_outside|_building|_gate_to_hearthome_city', '', s)
    s = s.replace('_north', ' (north)').replace('_south', ' (south)').replace('_east', ' (east)').replace('_west', ' (west)')
    s = s.replace('_', ' ')
    s = ' '.join(w if w.isupper() or w[0].isdigit() or w in ('(north)', '(south)', '(east)', '(west)') else w.capitalize() for w in s.split())
    return s.replace('Mt Coronet', 'Mt. Coronet').replace('Pokemon', 'Pokémon')

CLASS = lambda c: c.replace('TRAINER_CLASS_', '').replace('_MALE', '').replace('_FEMALE', '').replace('_', ' ').title().replace('Pi', 'PI') if c else ''
def trainer_label(key, d):
    k = key[8:].lower()
    name = d['name']
    cls = CLASS(d.get('class', ''))
    starter = re.search(r'_(turtwig|chimchar|piplup)$', k)
    if k.startswith('rival_'): who = 'Barry (rival)'
    elif k.startswith('dawn_') or k.startswith('lucas_'): who = name + ' (tag partner/battle)'
    elif k.startswith('leader_'): who = f'Gym Leader {name}'
    elif k.startswith('elite_four_'): who = f'Elite Four {name}'
    elif k.startswith('champion_'): who = f'Champion {name}'
    elif k.startswith('commander_'): who = f'Commander {name}'
    elif k.startswith('galactic_boss'): who = f'Boss {name}'
    elif k.startswith('galactic_grunt'): who = 'Galactic Grunt'
    else: who = f'{cls} {name}'.strip()
    if starter: who += f' — if you chose {starter.group(1).title()}'
    return who

seen = collections.defaultdict(list)
for key, maps in trmap.items():
    k = key[8:].lower()
    if 'rematch' in k: continue
    maps = [m for m in maps if '_dp_' not in m and not m.startswith('battle_')]
    if not maps: continue
    try: d = json.load(open(f'{RES}trainers/data/{k}.json'))
    except FileNotFoundError: continue
    m = min(maps, key=order_of)
    for p in d.get('party', []):
        sp = p['species'].replace('SPECIES_', '')
        sid = SPC.get(sp)
        if sid is None: print('?', sp); continue
        seen[sid].append(dict(o=order_of(m), map=pretty_map(m), area=area(m), who=trainer_label(key, d), lv=p['level'], post=area(m) in POST))

out = {}
for s in sinnoh:
    sid = s['id']
    lst = sorted(seen.get(sid, []), key=lambda x: (x['o'], x['lv']))
    uniq = []
    for x in lst:
        t = (x['map'], x['who'])
        if t not in [(u['map'], u['who']) for u in uniq]: uniq.append(x)
    story = [u for u in uniq if not u['post']]
    areas = {u['area'] for u in story}
    out[sid] = dict(n=len(uniq), story=len(story), areas=len(areas),
                    list=[f"{u['map']}: {u['who']} (Lv{u['lv']})" + (' — post-game' if u['post'] else '') for u in uniq[:8]], more=max(0, len(uniq) - 8))
json.dump(out, open('/home/claude/work/seen.json', 'w'), ensure_ascii=False)
if __name__ == '__main__':
    for s in sinnoh:
        o = out[s['id']]
        if s['how'] != 'catch' and o['story'] <= 2:
            print(s['rn'], NAMES[s['id']], s['how'], o['story'], o['list'][:3])
