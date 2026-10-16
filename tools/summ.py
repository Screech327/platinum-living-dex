import json, collections, re
E = json.load(open('/home/claude/work/enc.json'))

MNAME = {'walk': 'grass/cave', 'surf': 'Surf', 'old-rod': 'Old Rod', 'good-rod': 'Good Rod', 'super-rod': 'Super Rod',
         'honey-tree': 'honey tree', 'gift': 'gift', 'gift-egg': 'egg gift', 'static': 'static', 'roaming-grass': 'roaming',
         'roaming-water': 'roaming', 'feebas-tile-fishing': 'Feebas tiles', 'npc-trade': 'in-game trade', 'pokemon-ranger': 'Ranger'}
TIMES = ('time-morning', 'time-day', 'time-night')
SPECIAL = ('radar-on', 'swarm-yes', 'slot2-', 'great-marsh-daily', 'backlot-', 'honey-tree-group', 'radio-')

def short(place):
    if '|' in place:
        loc, sub = place.split('|')[:2]
        return loc, sub
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
        a['post'] = place.split('|')[2:3] == ['post']
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
        out.append(dict(loc=loc, sub=sub, method=m, special=sp, rate=best, times=times if len(times) < 3 else [], rt=[rates[t] for t in TIMES],
                        lo=a['lo'], hi=a['hi'], extra=sorted(a['extra']), post=a.get('post', False)))
    return out

CAVE_WORDS = ('Cave', 'Coronet', 'Ruins', 'Island', 'Ironworks', 'Mine', 'Gate', 'Victory', 'Chateau', 'Tower', 'Temple', 'Cavern', 'Path', 'Spring', 'Mountain', 'Underpass', 'Tunnel')
NORATE = ('gift', 'gift-egg', 'static', 'roaming-grass', 'roaming-water', 'npc-trade', 'pokemon-ranger')
POST_TXT = ' — after the Hall of Fame + National Dex'
LATE = {'Route 224', 'Route 225', 'Route 227', 'Route 228', 'Route 229', 'Sea Route 226', 'Sea Route 230', 'Resort Area', 'Stark Mountain', 'Snowpoint Temple',
        'Turnback Cave', 'Sendoff Spring', 'Victory Road', 'Flower Paradise', 'Newmoon Island', 'Hall of Origin'}

def _groups(es):
    """One group per place+method+level range (story areas before post-game ones); sub-areas with identical levels are merged."""
    m = collections.OrderedDict()  # first merge tables that share a name (e.g. Turnback Cave rooms)
    for e in es:
        k = (e['loc'], e['sub'], e['method'], e.get('post', False))
        if k not in m: m[k] = dict(e, times=list(e['times']))
        else:
            x = m[k]; x['lo'] = min(x['lo'], e['lo']); x['hi'] = max(x['hi'], e['hi']); x['rate'] = max(x['rate'], e['rate']); x['rt'] = [max(a, b) for a, b in zip(x['rt'], e['rt'])]
            x['times'] = sorted(set(x['times']) | set(e['times'])) if x['times'] and e['times'] else []
    g = collections.OrderedDict()
    # easiest first: story areas before late/post-game ones, then lowest level, then highest rate
    for e in sorted(m.values(), key=lambda e: (e.get('post', False), e['loc'] in LATE, e['method'] not in ('walk', 'surf', 'old-rod'), e['lo'], -e['rate'])):
        k = (e['loc'], e['method'], e['lo'], e['hi'], e.get('post', False))
        x = g.setdefault(k, dict(loc=e['loc'], method=e['method'], subs=[], rates=set(), rts=set(), lo=e['lo'], hi=e['hi'], post=e.get('post', False), anytime=False, times=set()))
        if e['sub'] and e['sub'] not in x['subs']: x['subs'].append(e['sub'])
        x['rates'].add(e['rate']); x['rts'].add(tuple(e['rt']))
        if e['times']: x['times'].update(e['times'])
        else: x['anytime'] = True
    return list(g.values())

def _fmt(x, maxsubs=3):
    loc = x['loc']
    if x['subs'] and all(re.fullmatch(r'Area \d', t) for t in x['subs']): loc += ' Area ' + '/'.join(t[5:] for t in sorted(x['subs']))
    elif x['subs']: loc += ' ' + (', '.join(re.sub(r' \(.*\)$', '', t) for t in x['subs']) if len(x['subs']) <= maxsubs else f"({len(x['subs'])} areas)")
    meth = MNAME.get(x['method'], x['method'])
    if meth == 'grass/cave':
        meth = 'grass' if 'Outside' in loc or 'summit' in loc else 'cave' if any(w in x['loc'] for w in CAVE_WORDS) else 'grass'
    lv = f"Lv{x['lo']}" if x['lo'] == x['hi'] else f"Lv{x['lo']}–{x['hi']}"
    rate, tm = '', ''
    if x['method'] not in NORATE:
        if len(x['rts']) == 1:
            rt = next(iter(x['rts'])); TN = ('morning', 'day', 'night')
            if len(set(rt)) == 1: rate = f", {rt[0]}%"
            else:
                on = [TN[i] for i in range(3) if rt[i]]
                if len(on) < 3:
                    rate = f", {max(rt)}%" if len({rt[i] for i in range(3) if rt[i]}) == 1 else ', ' + ' / '.join(f"{rt[i]}% {TN[i]}" for i in range(3) if rt[i])
                    tm = ' — ' + ' & '.join(on) + ' only'
                else:
                    rate = ', ' + ' / '.join(f"{rt[i]}% {TN[i][0].upper()}" for i in range(3))
        else:
            rate = f", up to {max(x['rates'])}%"
            T = [t for t in ('morning', 'day', 'night') if t in x['times']]
            tm = '' if x['anytime'] or not T or len(T) == 3 else (' — mostly ' + ' & '.join(T))
    if x['method'] == 'npc-trade': return f"{loc} (in-game trade)"
    return f"{loc} ({meth}{rate}, {lv}){tm}{POST_TXT if x['post'] else ''}"

def fmt_group(es, maxlocs=3):
    items = _groups(es)
    s = '; '.join(_fmt(x) for x in items[:maxlocs])
    if len(items) > maxlocs: s += f'; +{len(items) - maxlocs} more'
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


def full_list(es):
    """Every place, one line per level range."""
    return [_fmt(x, 4) for x in _groups(es)]
