"""enc.json = PokeAPI encounters for every game, but Platinum's wild tables replaced with the decomp's (ground truth)."""
import json, sys
sys.path.insert(0, '/home/claude/scripts')
from pt_tables import tables, POST_KEYS
E = json.load(open('/home/claude/work/enc_pokeapi.json'))
WILD = ('walk', 'surf', 'old-rod', 'good-rod', 'super-rod')
for k, d in E.items():
    if 'Pt' in d: d['Pt'] = [e for e in d['Pt'] if e[1] not in WILD]
for key, loc, sub, rows in tables():
    place = f"{loc}|{sub}|{'post' if key in POST_KEYS else ''}|{key}"
    for m, c, s, r, lo, hi in rows:
        if not s: continue
        E.setdefault(str(s), {}).setdefault('Pt', []).append([place, m, r, lo, hi, list(c)])
json.dump(E, open('/home/claude/work/enc.json', 'w'))
print('ok', sum(len(d.get('Pt', [])) for d in E.values()))
