import json, collections, re
E = json.load(open('/home/claude/work/enc.json'))

MNAME = {'walk': 'grass/cave', 'surf': 'Surf', 'old-rod': 'Old Rod', 'good-rod': 'Good Rod', 'super-rod': 'Super Rod',
         'honey-tree': 'honey tree', 'gift': 'gift', 'gift-egg': 'egg gift', 'static': 'static', 'roaming-grass': 'roaming',
         'roaming-water': 'roaming', 'feebas-tile-fishing': 'Feebas tiles', 'npc-trade': 'in-game trade', 'pokemon-ranger': 'Ranger'}
TIMES = ('time-morning', 'time-day', 'time-night')
SPECIAL = ('radar-on', 'swarm-yes', 'slot2-', 'great-marsh-daily', 'backlot-', 'honey-tree-group', 'radio-')

def short(place):
    m = re.match(r'(.*?) \((.*)\)$', place)
    if not m: return place, ''
    loc, area = m.group(1), m.group(2)
    loc = loc.replace('Mt. Coronet', 'Mt. Coronet')
    inner = re.search(r'\((.*)\)', area)
    sub = ''
    if inner:
        sub = inner.group(1).split(',')[0].strip()
    elif area.startswith(loc.split(' (')[0]) and area != loc:
        sub = area[len(loc):].strip()
    sub = {'north': 'N', 'south': 'S', 'east': 'E', 'west': 'W'}.get(sub, sub)
    if any(w in sub.lower() for w in ('before', 'after', 'caught', 'pillar', 'galactic', 'exterior', 'entrance', 'cavern', 'road ', 'small room', 'inside', 'left', 'right')) or len(sub) > 10:
        sub = ''
    if loc == 'Mt. Coronet' and 'exterior' in area.lower(): loc = 'Mt. Coronet summit'
    if sub.lower() in ('', loc.lower()): sub = ''
    return loc, sub

def special_key(conds):
    for c in conds:
        for s in SPECIAL:
            if c.startswith(s): return c
    return ''

def entries(n, v='Pt'):
    """Return list of dicts: loc, subs, method, special, rate, times(list), lo, hi, extra"""
    raw = E.get(str(n), {}).get(v, [])
    g = collections.defaultdict(lambda: {'base': 0, 't': collections.Counter(), 'lo': 99, 'hi': 0, 'subs': set(), 'extra': set()})
    # key by (loc, sub, method, special)
    per_area = collections.defaultdict(lambda: {'base': 0, 't': collections.Counter(), 'lo': 99, 'hi': 0, 'extra': set()})
    for place, m, r, lo, hi, conds in raw:
        loc, sub = short(place)
        sp = special_key(conds)
        if sp.startswith('slot2-') or sp == 'radar-on' or sp == 'swarm-yes':
            pass
        k = (place, m, sp)
        a = per_area[k]
        a['loc'], a['sub'] = loc, sub
        t = [c for c in conds if c in TIMES]
        if t: a['t'][t[0]] += r
        else: a['base'] += r
        a['lo'] = min(a['lo'], lo); a['hi'] = max(a['hi'], hi)
        for c in conds:
            if c not in TIMES and not any(c.startswith(s) for s in SPECIAL): a['extra'].add(c)
    out = []
    for (place, m, sp), a in per_area.items():
        loc, sub = a['loc'], a['sub']
        rates = {t: a['base'] + a['t'][t] for t in TIMES}
        best = max(rates.values())
        times = [t[5:] for t in TIMES if rates[t] == best]
        out.append(dict(loc=loc, sub=sub, method=m, special=sp, rate=best, times=times if len(times) < 3 else [],
                        lo=a['lo'], hi=a['hi'], extra=sorted(a['extra'])))
    return out

def fmt_group(es, maxlocs=3):
    """merge sub-areas per location, sort by rate"""
    g = collections.OrderedDict()
    LAND = ('walk',)
    for e in sorted(es, key=lambda e: (e['method'] not in LAND, -e['rate'])):
        k = (e['loc'], e['method'], tuple(e['times']))
        if k not in g: g[k] = dict(e, subs=[e['sub']] if e['sub'] else [], lo=e['lo'], hi=e['hi'])
        else:
            x = g[k]
            if e['sub'] and e['sub'] not in x['subs']: x['subs'].append(e['sub'])
            x['lo'] = min(x['lo'], e['lo']); x['hi'] = max(x['hi'], e['hi'])
    items = list(g.values())
    parts = []
    for x in items[:maxlocs]:
        loc = x['loc']
        if x['subs'] and len(x['subs']) <= 3: loc += ' ' + '/'.join(x['subs'])
        meth = MNAME.get(x['method'], x['method'])
        if meth == 'grass/cave':
            meth = 'grass' if 'summit' in x['loc'] else 'cave' if any(w in x['loc'] for w in ('Cave', 'Coronet', 'Ruins', 'Island', 'Ironworks', 'Mine', 'Gate', 'Victory', 'Chateau', 'Tower', 'Temple', 'Cavern', 'Path', 'Spring', 'Mountain', 'Underpass')) else 'grass'
        lv = f"Lv{x['lo']}" if x['lo'] == x['hi'] else f"Lv{x['lo']}–{x['hi']}"
        tm = (' ' + '/'.join(x['times']) + ' only') if x['times'] else ''
        rate = f"{x['rate']}%" if x['method'] not in ('gift', 'gift-egg', 'static', 'roaming-grass', 'roaming-water', 'npc-trade') else ''
        parts.append(f"{loc} ({meth}{', ' + rate if rate else ''}, {lv}{tm})")
    more = len(items) - maxlocs
    s = '; '.join(parts)
    if more > 0: s += f'; +{more} more'
    return s

def classify(n):
    es = entries(n)
    buckets = collections.defaultdict(list)
    for e in es:
        sp = e['special']
        if sp == 'radar-on': b = 'radar'
        elif sp == 'swarm-yes': b = 'swarm'
        elif sp.startswith('slot2-'): b = 'slot2-' + sp[6:]
        elif sp.startswith('great-marsh-daily'): b = 'marsh-rot' if 'none' not in sp else 'wild'
        elif sp == 'backlot-mentioned': b = 'trophy'
        elif sp.startswith('honey-tree'): b = 'honey'
        elif e['method'] in ('gift', 'gift-egg'): b = 'gift'
        elif e['method'] in ('static',): b = 'static'
        elif e['method'].startswith('roaming'): b = 'roam'
        elif e['method'] == 'npc-trade': b = 'trade'
        elif e['method'] == 'feebas-tile-fishing': b = 'feebas'
        elif e['method'] == 'pokemon-ranger': b = 'ranger'
        else: b = 'wild'
        buckets[b].append(e)
    return buckets

if __name__ == '__main__':
    import sys
    for n in sys.argv[1:]:
        b = classify(int(n))
        for k, v in b.items(): print(n, k, '|', fmt_group(v))
