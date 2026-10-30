"""Per-species data from the pret/pokeplatinum decomp: [catch rate, base HP, net-ball type?, default level, type 1, type 2 or -1]."""
import json, subprocess
R = '/home/claude/ext/pokeplatinum'
names = open(R + '/generated/species.txt').read().split()
enc = json.load(open('/home/claude/work/enc.json'))
NOCATCH = {'gift', 'gift-egg', 'npc-trade', 'pokemon-ranger'}
TYPES = ['Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel']
out = []
for i in range(1, 494):
    slug = names[i].replace('SPECIES_', '').lower()
    d = json.loads(subprocess.run(['git', '-C', R, 'show', f'HEAD:res/pokemon/{slug}/data.json'], capture_output=True, text=True, check=True).stdout)
    t = d['types']
    net = int(any(x in ('TYPE_WATER', 'TYPE_BUG') for x in t))
    lv = [r[3] for r in enc.get(str(i), {}).get('Pt', []) if r[1] not in NOCATCH]
    ty = [TYPES.index(x.replace('TYPE_', '').title()) for x in t]
    out.append([d['catch_rate'], d['base_stats']['hp'], net, min(lv) if lv else 0, ty[0], ty[1] if ty[1] != ty[0] else -1])
json.dump(out, open('/home/claude/work/catch.json', 'w'), separators=(',', ':'))
print(len(out), out[0], out[145], out[486], out[291], out[485])
