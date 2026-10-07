import sys, csv, json
sys.path.insert(0, '/home/claude/scripts')
from summ import classify, fmt_group
from site_data import entry_rank, OUT
from evo import PRE, EVO, NAMES
D = '/home/claude/data/'
rows = sorted((r for r in csv.DictReader(open(D + 'pokemon_dex_numbers.csv')) if r['pokedex_id'] == '6'), key=lambda r: int(r['pokedex_number']))
order = [int(r['species_id']) for r in rows]
res = []
story = {}
for sid in order:
    b = classify(sid)
    es = [e for e in b.get('wild', []) if entry_rank(e) <= 3] + [e for e in b.get('honey', [])] + [e for e in b.get('marsh-rot', []) if entry_rank(e) <= 3]
    story[sid] = es
for k, sid in enumerate(order, 1):
    es = story[sid]
    if es:
        txt = fmt_group(es, 3); how = 'catch'
    elif sid in PRE and story.get(PRE[sid]) is not None:
        txt = EVO[sid]; how = 'evolve'
    else:
        txt = ''; how = 'special'
    res.append(dict(rn=k, id=sid, how=how, story=txt))
if __name__ == '__main__':
    for r in res:
        if r['how'] != 'catch': print(r['rn'], r['id'], NAMES[r['id']], r['how'], r['story'][:90])
    json.dump(res, open('/home/claude/work/sinnoh.json', 'w'), ensure_ascii=False)
