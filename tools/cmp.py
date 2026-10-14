import csv, collections, sys
sys.path.insert(0, '/home/claude/scripts')
from decomp import ALL, USED
D = '/home/claude/data/'
def rd(f): return list(csv.DictReader(open(D + f, encoding='utf-8')))
methods = {r['id']: r['identifier'] for r in rd('encounter_methods.csv')}
slots = {r['id']: r for r in rd('encounter_slots.csv')}
areas = {r['id']: r for r in rd('location_areas.csv')}
an = {r['location_area_id']: r['name'] for r in rd('location_area_prose.csv') if r['local_language_id'] == '9'}
cvals = {r['id']: r['identifier'] for r in rd('encounter_condition_values.csv')}
cmap = collections.defaultdict(list)
for r in rd('encounter_condition_value_map.csv'): cmap[r['encounter_id']].append(cvals[r['encounter_condition_value_id']])
KEEP = ('time-', 'swarm-yes', 'radar-on', 'slot2-')
def agg(rows):
    g = collections.defaultdict(lambda: [0, 99, 0])
    for m, c, s, r, lo, hi in rows:
        x = g[(m, c, s)]; x[0] += r; x[1] = min(x[1], lo); x[2] = max(x[2], hi)
    # expand untimed walk to all 3 times
    out = {}
    for (m, c, s), v in g.items(): out[(m, c, s)] = tuple(v)
    return out
PA = collections.defaultdict(list)
for e in rd('encounters.csv'):
    if e['version_id'] != '14': continue
    s = slots[e['encounter_slot_id']]; m = methods[s['encounter_method_id']]
    if m not in ('walk', 'surf', 'old-rod', 'good-rod', 'super-rod'): continue
    conds = [c for c in cmap.get(e['id'], []) if c.startswith(KEEP) and c != 'slot2-none']
    if any(c.startswith(('radar', 'slot2', 'swarm')) for c in conds): continue
    if m == 'walk' and not any(c.startswith(('time-', 'swarm', 'radar', 'slot2')) for c in conds):
        for t in ('time-morning', 'time-day', 'time-night'): PA[e['location_area_id']].append((m, (t,), int(e['pokemon_id']), int(s['rarity']), int(e['min_level']), int(e['max_level'])))
    else:
        c = tuple(sorted(conds)) if not any(x.startswith(('swarm', 'radar', 'slot2')) for x in conds) else tuple(x for x in conds if x.startswith(('swarm', 'radar', 'slot2')))
        PA[e['location_area_id']].append((m, c, int(e['pokemon_id']), int(s['rarity']), int(e['min_level']), int(e['max_level'])))
PAG = {a: agg(r) for a, r in PA.items()}
used_pa = set()
MATCH = {}
for k, (d, rows) in ALL.items():
    A = agg([r for r in rows if not (r[1] and r[1][0].startswith(('radar', 'slot2', 'swarm')))]); best = None
    for a, B in PAG.items():
        ks = set(A) | set(B)
        sc = sum(1 for x in ks if A.get(x) == B.get(x)) / max(1, len(ks))
        sp = len({x[2] for x in A} & {x[2] for x in B}) / max(1, len({x[2] for x in A} | {x[2] for x in B}))
        s2 = sc + sp * 0.5
        if best is None or s2 > best[0]: best = (s2, a, sc)
    MATCH[k] = best[1]; used_pa.add(best[1])
    B = PAG[best[1]]
    diffs = [(x, A.get(x), B.get(x)) for x in sorted(set(A) | set(B), key=str) if A.get(x) != B.get(x)]
    if diffs:
        print(f"== {k}  vs PokeAPI '{an.get(best[1])}' ({areas[best[1]]['identifier']}) score {best[2]:.2f}")
        for x, a, b in diffs[:12]: print('   ', x, 'game:', a, 'pokeapi:', b)
        if len(diffs) > 12: print('    ...', len(diffs) - 12, 'more')
print('unmatched pokeapi areas:', [areas[a]['identifier'] for a in PAG if a not in used_pa])

if __name__ == '__main__':
    import json
    json.dump({k: an.get(v, '') for k, v in MATCH.items()}, open('/home/claude/work/match.json', 'w'), indent=0)
