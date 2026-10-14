"""Platinum wild encounters straight from the pret/pokeplatinum decompilation (ground truth).
Produces per-map-header rows: (method, conds tuple, species_id, rate, lo, hi)."""
import json, re, csv, collections, os
R = '/home/claude/ext/pokeplatinum/'
ENC = R + 'res/field/encounters/'
SP = {r['identifier']: int(r['id']) for r in csv.DictReader(open('/home/claude/data/pokemon_species.csv'))}
def sid(s):
    k = s[8:].lower().replace('_', '-')
    k = {'nidoran-f': 'nidoran-f', 'farfetchd': 'farfetchd', 'mr-mime': 'mr-mime', 'mime-jr': 'mime-jr'}.get(k, k)
    return SP[k] if s != 'SPECIES_NONE' else 0
LAND = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
SURF = [60, 30, 5, 4, 1]
OLD = [60, 30, 5, 4, 1]
GOOD = [40, 40, 15, 4, 1]
SWARM_MAPS = {'route_201', 'route_202', 'route_203', 'route_206', 'route_207', 'route_208', 'route_209', 'route_214', 'route_215', 'route_217', 'route_218', 'route_221', 'route_222',
              'route_224', 'route_225', 'route_226', 'route_227', 'route_228', 'route_229', 'route_230', 'valley_windworks_outside', 'eterna_forest'}
hdr = open(R + 'include/data/map_headers.h').read()
USED = {}
for h, b in re.findall(r'\[(MAP_HEADER_\w+)\]\s*=\s*\{(.*?)\n    \}', hdr, re.S):
    m = re.search(r'wildEncountersArchiveID = (\w+)', b)
    if m and m.group(1) != 'ENCOUNTERS_NONE': USED[m.group(1)[len('encounters_'):]] = h

def rows_for(key):
    d = json.load(open(ENC + 'encounters_' + key + '.json'))
    out = []  # (method, conds, sp, rate, lo, hi)
    if d['land_rate']:
        land = [(sid(e['species']), e['level']) for e in d['land_encounters']]
        for t, rep in (('time-morning', None), ('time-day', d['day']), ('time-night', d['night'])):
            for i, (s, lv) in enumerate(land):
                if key.startswith('great_marsh_') and i in (6, 7): continue  # always replaced by the daily Pokémon during the Safari Game
                if i in (2, 3):
                    s2 = s if rep is None else sid(rep[i - 2])
                    out.append(('walk', (t,), s2, LAND[i], lv, lv))
                else:
                    out.append(('walk', (t,), s, LAND[i], lv, lv))
        # special slots: only list the ones that actually change the species in that slot
        def rep(cond, species, idx):
            for s, i in zip(species, idx):
                s = sid(s)
                if s and s != land[i][0]: out.append(('walk', (cond,), s, LAND[i], land[i][1], land[i][1]))
        if key in SWARM_MAPS: rep('swarm-yes', d['swarms'], (0, 1))
        rep('radar-on', d['radar'], (4, 5, 10, 11))
        for g in ('ruby', 'sapphire', 'emerald', 'firered', 'leafgreen'): rep('slot2-' + g, d[g], (8, 9))
    for meth, rates, k in (('surf', SURF, 'surf'), ('old-rod', OLD, 'old_rod'), ('good-rod', GOOD, 'good_rod'), ('super-rod', GOOD, 'super_rod')):
        if d[k + '_rate']:
            for i, e in enumerate(d[k + '_encounters']):
                if e['species'] != 'SPECIES_NONE':
                    out.append((meth, (), sid(e['species']), rates[i], min(e['level_min'], e['level_max']), max(e['level_min'], e['level_max'])))
    return d, out

ALL = {k: rows_for(k) for k in USED}
GM = json.load(open(ENC + 'encounters_great_marsh_lookout.json'))
GM_PRE = collections.Counter(sid(s) for s in GM['before_national_dex'])
GM_POST = collections.Counter(sid(s) for s in GM['after_national_dex'])
TG = [sid(s) for s in json.load(open(ENC + 'encounters_trophy_garden.json'))['daily_encounters']]
if __name__ == '__main__':
    print(len(ALL), 'tables'); print(sorted(set(os.path.basename(f)[11:-5] for f in os.listdir(ENC) if f.endswith('.json')) - set(USED)))
