import csv, collections, json, sys
D = '/home/claude/data/'
def rd(f): return list(csv.DictReader(open(D + f, encoding='utf-8')))

methods = {r['id']: r['identifier'] for r in rd('encounter_methods.csv')}
slots = {r['id']: r for r in rd('encounter_slots.csv')}
areas = {r['id']: r for r in rd('location_areas.csv')}
area_name = {r['location_area_id']: r['name'] for r in rd('location_area_prose.csv') if r['local_language_id'] == '9'}
loc_name = {r['location_id']: r['name'] for r in rd('location_names.csv') if r['local_language_id'] == '9'}
cvals = {r['id']: r['identifier'] for r in rd('encounter_condition_values.csv')}
cmap = collections.defaultdict(list)
for r in rd('encounter_condition_value_map.csv'):
    cmap[r['encounter_id']].append(cvals[r['encounter_condition_value_id']])

def place(aid):
    a = areas[aid]
    ln = loc_name.get(a['location_id'], a['identifier'])
    an = area_name.get(aid, '')
    return f"{ln} ({an})" if an else ln

VERS = {'12': 'D', '13': 'P', '14': 'Pt', '15': 'HG', '16': 'SS', '7': 'R', '8': 'S', '9': 'E', '10': 'FR', '11': 'LG'}
out = collections.defaultdict(lambda: collections.defaultdict(list))
for e in rd('encounters.csv'):
    v = e['version_id']
    if v not in VERS: continue
    s = slots[e['encounter_slot_id']]
    m = methods[s['encounter_method_id']]
    conds = [c for c in cmap.get(e['id'], []) if c not in ('swarm-no', 'radar-off', 'slot2-none', 'radio-off', 'story-progress-none', 'other-none', 'item-none')]
    out[int(e['pokemon_id'])][VERS[v]].append((place(e['location_area_id']), m, int(s['rarity'] or 0), int(e['min_level']), int(e['max_level']), tuple(sorted(conds))))
json.dump({k: {v: l for v, l in d.items()} for k, d in out.items()}, open('/home/claude/work/enc.json', 'w'))
print(len(out))
