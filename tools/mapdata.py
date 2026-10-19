"""Per-location Platinum encounter tables for the site's map (rates by morning/day/night).
Wild tables come straight from the pret/pokeplatinum decompilation; gifts/statics/trades/Feebas from PokeAPI (checked against the decomp scripts)."""
import json, sys, collections, csv
sys.path.insert(0, '/home/claude/scripts')
from pt_tables import tables, POST_KEYS
CART = {'ruby': 'Ruby', 'sapphire': 'Sapphire', 'emerald': 'Emerald', 'firered': 'FireRed', 'leafgreen': 'LeafGreen'}
ROD = {'surf': 'Surfing', 'old-rod': 'Old Rod', 'good-rod': 'Good Rod', 'super-rod': 'Super Rod'}

def sections(rows):
    S = collections.OrderedDict()
    def add(sec, s, rt, lo, hi, note=''):
        x = S.setdefault(sec, collections.OrderedDict()).setdefault(s, [0, 0, 0, 99, 0, note])
        for i in range(3): x[i] += rt[i]
        x[3] = min(x[3], lo); x[4] = max(x[4], hi)
    for m, c, s, r, lo, hi in rows:
        if not s: continue
        if m in ROD: add(ROD[m], s, [r] * 3, lo, hi)
        elif c and c[0].startswith('time-'): add('Grass / cave', s, [r if c[0] == t else 0 for t in ('time-morning', 'time-day', 'time-night')], lo, hi)
        elif c[0] == 'swarm-yes': add('Swarm (daily outbreak)', s, [r] * 3, lo, hi)
        elif c[0] == 'radar-on': add('Poké Radar (after National Dex)', s, [r] * 3, lo, hi)
        elif c[0].startswith('slot2-'): add('Dual-slot:' + c[0][6:], s, [r] * 3, lo, hi)
        elif c[0].startswith('great-marsh-daily'):
            n = c[0].split('-')[4]; pre = c[0].endswith('-pre')
            add('Daily Pokémon — ' + ('before' if pre else 'after') + ' National Dex', s, [r] * 3, lo, hi, f'{round(int(n) / 32 * 100)}% chance it’s today’s pick')
        elif c[0] == 'backlot-mentioned': add("Mr. Backlot's daily Pokémon (after National Dex)", s, [r] * 3, lo, hi, 'one at a time, changes daily')
    out = []
    # merge identical dual-slot tables across carts
    duals = collections.OrderedDict()
    for sec, mons in S.items():
        rows = sorted([[s, *v] for s, v in mons.items()], key=lambda r: (-max(r[1:4]), -int(r[6].split('~')[1].split()[0]) if '~' in r[6] else 0, r[0]))
        if sec.startswith('Dual-slot:'): duals.setdefault(json.dumps(rows), []).append(CART[sec[10:]]); continue
        out.append([sec, rows])
    for rows, carts in duals.items(): out.append(['Dongle: ' + '/'.join(carts) + ' in GBA slot (after National Dex)', json.loads(rows)])
    ORDER = ['Grass / cave', 'Surfing', 'Old Rod', 'Good Rod', 'Super Rod']
    out.sort(key=lambda s: ORDER.index(s[0]) if s[0] in ORDER else 50)
    return out

LOCS = collections.OrderedDict()
for key, loc, sub, rows in tables():
    secs = sections(rows)
    if key in POST_KEYS: sub = f'Back room {key[-1]} · post-game'
    subs = LOCS.setdefault(loc, [])
    sig = json.dumps(secs)
    for s in subs:
        if s[2] == sig:
            if sub not in s[0]: s[0].append(sub)
            break
    else: subs.append([[sub], secs, sig, key])
# same label, different tables → number them
OUT = collections.OrderedDict()
for loc, subs in LOCS.items():
    cnt = collections.Counter(tuple(s[0]) for s in subs); seen = collections.Counter()
    res = []
    for labels, secs, sig, key in subs:
        t = tuple(labels); seen[t] += 1
        lab = ', '.join(labels) if len(labels) <= 3 else ('All rooms' if len(subs) == 1 else 'Most rooms')
        if cnt[t] > 1: lab += f' ({seen[t]})'
        res.append([lab, secs])
    CO = ['1F south', '1F Route 211', '1F Route 216', '1F back', '2F', '3F', '4F', '4F small', '5F', '6F', 'Outside', 'B1F']
    if loc == 'Victory Road': res.sort(key=lambda s: (len(s[0]) > 3, s[0]))
    if loc == 'Mt. Coronet': res.sort(key=lambda s: next(i for i, p in enumerate(CO) if s[0].startswith(p)))
    OUT[loc] = res

# ---- non-wild Platinum encounters (PokeAPI; levels verified against the decomp scripts) + things PokeAPI lacks
E = json.load(open('/home/claude/work/enc_pokeapi.json'))
SEC = {'gift': 'Gift', 'gift-egg': 'Egg gift', 'static': 'One-time encounter', 'npc-trade': 'In-game trade', 'feebas-tile-fishing': 'Feebas tiles (any rod; 4 hidden tiles that change daily; 50% on them)'}
NOTE = {(133, 'gift'): 'from Bebe', (137, 'gift'): 'from a man in Veilstone', (175, 'gift-egg'): 'egg from Cynthia', (447, 'gift-egg'): 'egg from Riley',
        (387, 'gift'): 'starter', (390, 'gift'): 'starter', (393, 'gift'): 'starter', (442, 'static'): 'Hallowed Tower + Odd Keystone',
        (425, 'static'): 'Fridays, after the Galactic event', (479, 'static'): 'TV in the back room', (486, 'static'): 'needs Regirock, Regice, Registeel in party',
        (487, 'static'): '', (493, 'static'): 'needs the Azure Flute (event item)', (491, 'static'): 'needs the Member Card (event item)', (492, 'static'): "needs Oak's Letter (event item)", (493, 'static'): 'needs the Azure Flute (event item)', (491, 'static'): 'needs the Member Card (event item)', (492, 'static'): "needs Oak's Letter (event item)", (63, 'npc-trade'): 'trade a Machop', (441, 'npc-trade'): 'trade a Buizel', (129, 'npc-trade'): 'trade a Finneon', (93, 'npc-trade'): 'trade a Medicham', (483, 'static'): 'after Hall of Fame, Adamant Orb', (484, 'static'): 'after Hall of Fame, Lustrous Orb'}
for loc_name in ('Oreburgh City',):
    pass
extra = collections.defaultdict(lambda: collections.defaultdict(dict))
loc_fix = {'Mt. Coronet': 'Mt. Coronet'}
for sid, d in E.items():
    for place, m, r, lo, hi, conds in d.get('Pt', []):
        if m not in SEC: continue
        loc = place.split(' (')[0] if ' (' in place else place
        sid_i = int(sid)
        note = NOTE.get((sid_i, m), '')
        if sid_i in (138, 140, 142, 345, 347, 408, 410): note = 'revived fossil (Mining Museum)'
        if m == 'npc-trade': lo = hi = 0
        extra[loc][SEC[m]][sid_i] = [sid_i, 0, 0, 0, lo, hi, note]
for loc, sid_i, lv, note in (('Route 228', 377, 30, 'Regirock — Rock Peak Ruins, Regigigas in party'), ('Route 217', 378, 30, 'Regice — Iceberg Ruins, Regigigas in party'),
                             ('Iron Island', 379, 30, 'Registeel — Iron Ruins, Regigigas in party'), ('Lake Acuity', 480, 50, 'Acuity Cavern'), ('Lake Valor', 482, 50, 'Valor Cavern'),
                             ('Turnback Cave', 487, 47, 'if you didn’t catch it in the Distortion World')):
    extra[loc]['One-time encounter'][sid_i] = [sid_i, 0, 0, 0, lv, lv, note]
HONEY = [[415, 32, 32, 32, 5, 15, ''], [412, 22, 22, 22, 5, 15, ''], [265, 14, 14, 14, 5, 15, ''], [420, 11, 11, 11, 5, 15, ''], [190, 10, 10, 10, 5, 15, ''],
         [214, 1, 1, 1, 5, 15, '≈3.5% on a Munchlax tree'], [446, 1, 1, 1, 5, 15, 'only on 4 trees, set by your Trainer ID']]
HONEY_LOCS = ['Route 205', 'Route 206', 'Route 207', 'Route 208', 'Route 209', 'Route 210', 'Route 211', 'Route 212', 'Route 213', 'Route 214', 'Route 215',
              'Route 218', 'Route 221', 'Route 222', 'Valley Windworks', 'Eterna Forest', 'Fuego Ironworks', 'Floaroma Meadow']
for loc in HONEY_LOCS: extra[loc]['Honey tree (per slather; 10% nothing)'] = {r[0]: r for r in HONEY}
for loc, secs in extra.items():
    for sec, mons in secs.items():
        rows = list(mons.values())
        if loc in OUT and sec.startswith('Feebas'):
            for s in OUT[loc]:
                if s[0].startswith('B1F'): s[1].append([sec, rows])
            continue
        if loc in OUT:
            for s in OUT[loc]: pass
            if len(OUT[loc]) == 1: OUT[loc][0][1].append([sec, rows])
            else:
                sp = next((x for x in OUT[loc] if x[0] == 'Special'), None)
                if not sp: sp = ['Special', []]; OUT[loc].append(sp)
                sp[1].append([sec, rows])
        else:
            OUT.setdefault(loc, [['', []]])[0][1].append([sec, rows])
for loc, subs in OUT.items():
    for x in subs:
        if x[0] == 'Special': x[0] = 'Honey tree' if all(n.startswith('Honey') for n, _ in x[1]) else 'Special encounters'
# footnotes
NOTES = {'Victory Road': 'The back rooms open after the Hall of Fame + National Dex (a Collector blocks the way until then).',
         'Mt. Coronet': 'B1F (the Feebas lake) is reached from the Route 211 tunnel or the Route 216 entrance.','Trophy Garden': "After the National Dex, Mr. Backlot's two daily Pokémon take over the two 5% slots (the Lv22 Pikachu and Pichu slots).",
         'Great Marsh': 'You are always in the Safari Game here, so every area also has its own daily Pokémon at 10%. The binoculars in the Great Marsh building show today’s picks.'}
res = [[loc, subs, NOTES.get(loc, '')] for loc, subs in OUT.items()]
json.dump(res, open(sys.argv[1], 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(res), 'locations')
for loc, subs, n in res: print(loc, '|', [s[0] for s in subs])
