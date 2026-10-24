"""Per-species catch data from the pret/pokeplatinum decomp: [catch rate, base HP, net-ball type?, default level]."""
import json, subprocess
R = '/home/claude/ext/pokeplatinum'
names = open(R + '/generated/species.txt').read().split()
enc = json.load(open('/home/claude/work/enc.json'))
NOCATCH = {'gift', 'gift-egg', 'npc-trade', 'pokemon-ranger'}
out = []
for i in range(1, 494):
    slug = names[i].replace('SPECIES_', '').lower()
    d = json.loads(subprocess.run(['git', '-C', R, 'show', f'HEAD:res/pokemon/{slug}/data.json'], capture_output=True, text=True, check=True).stdout)
    t = d['types']
    net = int(any(x in ('TYPE_WATER', 'TYPE_BUG') for x in t))
    lv = [r[3] for r in enc.get(str(i), {}).get('Pt', []) if r[1] not in NOCATCH]
    out.append([d['catch_rate'], d['base_stats']['hp'], net, min(lv) if lv else 0])
json.dump(out, open('/home/claude/work/catch.json', 'w'), separators=(',', ':'))
print(len(out), out[0], out[145], out[486], out[291], out[485])
