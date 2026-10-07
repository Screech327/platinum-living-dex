"""Site dataset: everything in data.py plus unlock tiers, requirement steps, transfer path and families."""
import sys, json, collections
sys.path.insert(0, '/home/claude/scripts')
from data import build
from summ import classify
from evo import PRE, NAMES, SP, EVO

R = build()

# ---- Platinum access tiers ---------------------------------------------------------------
TIERS = ['Story', 'Story · Good Rod', 'Story · Surf', 'Victory Road (8 badges)', 'After Hall of Fame', 'After National Dex', 'Other game', 'Event only']
POST_HOF = {'Route 224', 'Route 225', 'Route 227', 'Route 228', 'Route 229', 'Sea Route 226', 'Sea Route 230', 'Resort Area', 'Stark Mountain',
            'Turnback Cave', 'Sendoff Spring', 'Snowpoint Temple', 'Flower Paradise', 'Newmoon Island', 'Hall of Origin'}
NATDEX = {'Trophy Garden'}
VICTORY = {'Victory Road'}
def loc_rank(loc):
    if loc in NATDEX: return 5
    if loc in POST_HOF: return 4
    if loc in VICTORY: return 3
    return 0
def method_rank(m):
    return {'surf': 2, 'good-rod': 1, 'super-rod': 4}.get(m, 0)

def entry_rank(e):
    r = max(loc_rank(e['loc']), method_rank(e['method']))
    if 'story-progress-national-dex' in e['extra']: r = max(r, 5)
    sp = e['special']
    if sp in ('radar-on', 'swarm-yes') or sp.startswith('slot2-') or sp == 'backlot-mentioned': r = max(r, 5)
    if sp == 'swarm-yes': r = max(r, 5)
    return r

BUCKET_FOR_CAT = {'Wild': 'wild', 'Poké Radar': 'radar', 'Swarm': 'swarm', 'Trophy Garden': 'trophy', 'Great Marsh (daily)': 'marsh-rot', 'Honey tree': 'honey'}

def best_rank(i, cat):
    b = classify(i)
    if cat == 'Dual-slot': return 5
    key = BUCKET_FOR_CAT.get(cat)
    if not key or key not in b: return None
    return min(entry_rank(e) for e in b[key])

# ---- hand-written requirement steps (checked against Bulbapedia/Serebii) ---------------------
PAL_GEN3 = 'Move it to Platinum with Pal Park — easiest through HG/SS (no daily limit, needs the HG/SS National Dex), then trade HG/SS → Platinum (2 DS systems).'
TRADE_DS = 'Trade it to Platinum over DS wireless (needs both carts + 2 DS systems).'
STEPS = {
    # Kanto starters
    1: ['FireRed/LeafGreen: pick it as your starter at the very start (Prof. Oak\'s lab).', 'OR HG/SS: beat Red on Mt. Silver, then Prof. Oak in Pallet Town lets you pick one Kanto starter.', 'In Platinum, breed it with Ditto (Trophy Garden) for the extra copies.'],
    152: ['HG/SS: pick it as your starter at the very start (Prof. Elm\'s lab).', 'OR Emerald: complete the Hoenn Pokédex (catch 200), then Prof. Birch offers a Johto starter.', 'In Platinum, breed it with Ditto for the extra copies.'],
    252: ['Ruby/Sapphire/Emerald: pick it as your starter at the very start.', 'OR HG/SS: beat Red, then Steven in Silph Co. (Saffron) gives one Hoenn starter.', 'In Platinum, breed it with Ditto for the extra copies.'],
    387: ['Platinum: pick ONE at the start of the game (Route 201).', 'Start Diamond or Pearl and pick a different one; repeat (or trade) for the third.', 'Breed each with Ditto in Platinum for the extra copies.'],
    198: ['Diamond: beat Roark (1st badge) and reach Eterna Forest.', 'Catch it at NIGHT (8 PM–4 AM) in Eterna Forest grass (20%).', 'Alternative: HG/SS Route 7 at night.'],
    200: ['Pearl: beat Roark (1st badge) and reach Eterna Forest.', 'Catch it at NIGHT (8 PM–4 AM) in Eterna Forest grass (20%).', 'Alternative: HG/SS Johto Safari Zone at night.'],
    431: ['Pearl: get Surf (5th badge in D/P, Fantina\'s Relic Badge) to reach Route 218 from Jubilife/Canalave.', 'Catch it in Route 218 grass (15%), or Route 222 (20%, late game).'],
    434: ['Diamond: get the Bicycle in Eterna City (after 2nd badge).', 'Route 206 under Cycling Road (grass, 25%).'],
    328: ['Ruby/Sapphire/Emerald: get the Go-Goggles (after beating Flannery, 4th badge, then talk to Brendan/May at Route 111).', 'Route 111 desert (35%). Emerald also has it in Mirage Tower (50%) when that appears.', 'Fallback: Diamond/Pearl Route 228 (post-game, 2%).'],
    366: ['HG/SS: reach Kanto and Surf on Sea Route 19 south of Fuchsia (60%).', 'OR Ruby/Sapphire/Emerald: Dive (7th badge) in Routes 124/126 underwater seaweed.', 'OR Diamond/Pearl: Super Rod (post-game) on Routes 219/221.', 'You need 3 (Clamperl + Huntail + Gorebyss). Huntail = trade holding Deep Sea Tooth, Gorebyss = trade holding Deep Sea Scale.'],
    143: ['FireRed/LeafGreen: get the Poké Flute from Mr. Fuji (after clearing Pokémon Tower in Lavender Town).', 'Wake the TWO Snorlax on Route 12 and Route 16 (Lv30).', 'OR HG/SS: after the Kanto Radio Tower Expansion Card (post-Elite Four, Kanto), play the Poké Flute channel at the Snorlax by Diglett\'s Cave (Lv50).', 'In Platinum: Snorlax holding a Full Incense + Ditto at the Day-Care hatches Munchlax.'],
    150: ['HG/SS: earn all 16 badges (8 Johto + 8 Kanto), then Cerulean Cave opens (north of Cerulean City). Mewtwo Lv70, B1F.', 'OR FireRed/LeafGreen: beat the Elite Four, finish the Sevii Islands storyline (restore the Network Machine with the Ruby and Sapphire), then Cerulean Cave opens.', 'Bring Ultra/Dusk-style balls and a sleep move. Save first.'],
    243: ['HG/SS: trigger the Burned Tower event in Ecruteak (story).', 'Raikou and Entei then roam Johto (Lv40). Use Mean Look/Block and sleep.', 'OR FireRed/LeafGreen: after beating the Elite Four and getting the National Dex, one beast roams Kanto: Raikou if you picked Squirtle, Entei if Bulbasaur, Suicune if Charmander.'],
    245: ['HG/SS: trigger the Burned Tower event, then follow Eusine\'s Suicune sightings across Johto/Kanto.', 'HeartGold: catch it at Route 25 after the sightings. SoulSilver: Bell Tower after the sightings (needs the Clear Bell). Lv40.', 'OR FireRed/LeafGreen: roams Kanto post-game if you picked Charmander.'],
    249: ['SoulSilver: story — Whirl Islands after the Kimono Girls give you the Tidal Bell (Lv45).', 'HeartGold: post-game — get the Silver Wing (from the old man in Pewter City after Kanto), then Whirl Islands (Lv70).'],
    250: ['HeartGold: story — Bell Tower after the Kimono Girls give you the Clear Bell (Lv45).', 'SoulSilver: post-game — get the Rainbow Wing (Pewter City old man, after all 16 badges), then Bell Tower (Lv70).'],
    377: ['Ruby/Sapphire/Emerald: post-game. Solve the Sealed Chamber Braille puzzle (Dive near Pacifidlog; Ruby/Sapphire need Relicanth + Wailord in party).', 'Then Desert Ruins (Regirock), Island Cave (Regice), Ancient Tomb (Registeel) open. Each Lv40.', 'Platinum\'s own Regi caves need an EVENT Regigigas, so this is the only way with your carts.'],
    380: ['HeartGold: after beating Red, Latias roams Kanto (Lv35).', 'OR Sapphire: after the Elite Four, Latias roams Hoenn (Lv40).', 'OR Emerald: if you chose RED on the TV after the Elite Four, Latias roams Hoenn.'],
    381: ['SoulSilver: after beating Red, Latios roams Kanto (Lv35).', 'OR Ruby: after the Elite Four, Latios roams Hoenn (Lv40).', 'OR Emerald: if you chose BLUE on the TV after the Elite Four, Latios roams Hoenn.'],
    382: ['Sapphire: story — Cave of Origin (Lv45).', 'OR Emerald: post-game — Marine Cave (find it via the weather reports in the Weather Institute, Lv70).', 'OR HeartGold: beat Red, get the Blue Orb from Mr. Pokémon, then Embedded Tower (Route 47) Lv50.'],
    383: ['Ruby: story — Cave of Origin (Lv45).', 'OR Emerald: post-game — Terra Cave (via weather reports, Lv70).', 'OR SoulSilver: beat Red, get the Red Orb from Mr. Pokémon, then Embedded Tower (Route 47) Lv50.'],
    384: ['Ruby/Sapphire: post-game — Sky Pillar (needs Mach Bike), Lv70.', 'Emerald: after the story wake-up, return post-game — Sky Pillar, Lv70.', 'OR HG/SS: show Prof. Oak an Embedded Tower Kyogre AND Groudon (needs both HG and SS) to get the Jade Orb, then Embedded Tower.'],
    144: ['Platinum: get the National Dex.', 'Go to Eterna City and talk to Prof. Oak (he visits after the National Dex).', 'Articuno, Zapdos and Moltres start roaming Sinnoh (Lv60). Track them with the Marking Map app; trap with Mean Look/Block.'],
    480: ['Platinum: after the Spear Pillar/Distortion World story, go to Lake Acuity (needs Rock Climb route).', 'Enter Acuity Cavern: Uxie Lv50. Save first; it respawns after the Elite Four if KO\'d.'],
    481: ['Platinum: after the story, enter Verity Cavern at Lake Verity.', 'Mesprit flees and roams Sinnoh (Lv50). Trap with Mean Look/Block.'],
    482: ['Platinum: after the story, enter Valor Cavern at Lake Valor.', 'Azelf Lv50. Save first.'],
    483: ['Platinum: get the National Dex.', 'Talk to Cynthia\'s grandmother in Celestic Town.', 'Pick up the Adamant Orb in Mt. Coronet, then go to Spear Pillar: Dialga Lv70.'],
    484: ['Platinum: get the National Dex.', 'Talk to Cynthia\'s grandmother in Celestic Town.', 'Pick up the Lustrous Orb in Mt. Coronet, then go to Spear Pillar: Palkia Lv70.'],
    485: ['Platinum: after the Hall of Fame, go to the Battle Zone and complete the Stark Mountain events with Buck.', 'Return to the innermost chamber: Heatran Lv50.'],
    486: ['Platinum: get Regirock, Regice and Registeel first (from Ruby/Sapphire/Emerald via Pal Park).', 'Put all three in your party and go to Snowpoint Temple B5F: Regigigas Lv1.'],
    487: ['Platinum: story — Distortion World (Lv47).', 'If you KO or run: after the Elite Four it waits in Turnback Cave (through Sendoff Spring).'],
    488: ['Platinum: get the National Dex.', 'In Canalave City, the sailor\'s son has nightmares. Go to Fullmoon Island and interact with Cresselia.', 'It roams Sinnoh (Lv50). Take the Lunar Wing back to wake the boy.'],
    442: ['Platinum: get the Odd Keystone (Route 208 trainer gift, or dig in the Underground).', 'Put it in the Hallowed Tower on Route 209.', 'Talk to 32 people in the Underground (leave and re-enter to talk to the same people again), then check the tower: Spiritomb Lv25.'],
    425: ['Platinum: clear Team Galactic from the Valley Windworks (story).', 'On a FRIDAY, a Drifloon appears by the gate (Lv15). One per week; breed Drifblim for extras.'],
    479: ['Platinum: Old Chateau (Eterna Forest, needs Cut).', 'At NIGHT, check the TV in the 2nd-floor left room: Rotom Lv20.'],
    349: ['Platinum: Good Rod or better.', 'Mt. Coronet B1F lake room (the big room reached from Route 211 West).', 'Only 4 hidden water tiles hold Feebas and they change every day. 50% Feebas even on the right tile.', 'Milotic: feed Feebas dry (blue) Poffins until its Beauty maxes, then level it up.'],
    133: ['Platinum: Bebe in Hearthome City gives you one Eevee (Lv20) — story.', 'For the other 7: Trophy Garden Eevee (after National Dex) or breed with Ditto.'],
    137: ['Platinum: get the National Dex.', 'Talk to the man inside the Veilstone City Pokémon Center: Porygon Lv25. One only — breed copies with Ditto.', 'Up-Grade: Prof. Oak gives it in Eterna City.'],
    175: ['Platinum: story — Cynthia gives you a Togepi egg in Eterna City.', 'Extra copies: Poké Radar on Sea Route 230 (post-game) or breed.'],
    447: ['Platinum: story — clear Iron Island with Riley and he gives you a Riolu egg.', 'Evolve it (friendship, daytime), then breed Lucario for the second Riolu.'],
    446: ['Get Snorlax from HG/SS or FireRed/LeafGreen (see Snorlax).', 'Pick up the Full Incense in Veilstone City (Platinum).', 'Day-Care: Snorlax holding Full Incense + Ditto → egg hatches Munchlax.', 'Honey trees work too, but only 4 hidden trees and about 1% — not worth it.'],
    360: ['Platinum: Wobbuffet (Poké Radar at Lake Verity/Valor, post-National Dex).', 'Pick up the Lax Incense on Route 225 (post-game).', 'Day-Care: Wobbuffet holding Lax Incense + Ditto → Wynaut.', 'Alternative: Emerald gives a Wynaut egg in Lavaridge Town.'],
}
for a, b in ((4, 1), (7, 1), (155, 152), (158, 152), (255, 252), (258, 252), (390, 387), (393, 387), (244, 243), (378, 377), (379, 377), (145, 144), (146, 144)):
    STEPS[a] = STEPS[b]
FOSSIL_STEPS = {138: 'Helix Fossil', 140: 'Dome Fossil', 142: 'Old Amber', 345: 'Root Fossil', 347: 'Claw Fossil'}
for i, f in FOSSIL_STEPS.items():
    STEPS[i] = [f'Platinum: get the National Dex (the five older fossils only appear after it).', f'Dig a {f} in the Underground walls (Explorer Kit from Eterna City).', 'Take it to the Oreburgh Mining Museum, step outside and back in, collect the Pokémon (Lv20).']
STEPS[408] = ['Platinum: Underground (Explorer Kit from Eterna City) — available during the story.', 'You only dig Skull Fossils if your Trainer ID is ODD. Even TID → dig it in Diamond and trade it over.', 'Revive at the Oreburgh Mining Museum (Lv20).']
STEPS[410] = ['Platinum: Underground (Explorer Kit from Eterna City) — available during the story.', 'You only dig Armor Fossils if your Trainer ID is EVEN. Odd TID → dig it in Pearl and trade it over.', 'Revive at the Oreburgh Mining Museum (Lv20).']
EVENT_STEPS = ['Needs an event distribution. Official Nintendo WFC closed in 2014; fan-run WFC servers (e.g. Wiimmfi) still hand these out.', 'Legal in-game, but collectors don\'t count fan-server copies as legitimate — your call.']
for i in (151, 251, 385, 386, 490, 491, 492, 493):
    STEPS.setdefault(i, EVENT_STEPS)
STEPS[489] = ['Needs an event Manaphy first.', 'Day-Care: Manaphy + Ditto → the egg hatches Phione.']

# transfer path into Platinum
def transfer(r):
    g = r['game']
    if r['cat'] == 'EVENT': return 'Event distribution'
    if 'Platinum' in g and not any(x in g for x in ('or', '+')): return 'Native to Platinum'
    if r['cat'] in ('Version exclusive',) or 'Diamond' in g or 'Pearl' in g and 'R/S/E' not in g: pass
    parts = []
    if any(x in g for x in ('HG/SS', 'HeartGold', 'SoulSilver', 'Diamond', 'Pearl', 'D/P')): parts.append('DS trade from ' + ', '.join(x for x in ('Diamond', 'Pearl', 'HG/SS') if x in g or (x == 'HG/SS' and ('HeartGold' in g or 'SoulSilver' in g)) or (x in ('Diamond', 'Pearl') and 'D/P' in g)))
    if any(x in g for x in ('FireRed', 'LeafGreen', 'R/S/E', 'Ruby', 'Sapphire', 'Emerald', 'FR/LG')): parts.append('Pal Park from Gen 3 (best via HG/SS)')
    if 'GBA slot' in g: return 'Catch in Platinum with the cart in the GBA slot (no transfer)'
    return ' or '.join(parts) if parts else 'Native to Platinum'

# families
chain = collections.defaultdict(list)
for i in range(1, 494): chain[SP[i]['evolution_chain_id']].append(i)

OUT = []
for i in range(1, 494):
    r = R[i]
    cat = r['cat']
    rank = best_rank(i, cat)
    if cat in ('Evolve', 'Trade evolution'):
        j = i
        while j in PRE and R[j]['cat'] in ('Evolve', 'Trade evolution'): j = PRE[j]
        src_rank = OUT[j - 1]['rank'] if j < i else None
        rank = src_rank
    if rank is None:
        rank = {'EVENT': 7, 'Other cart': 6, 'Version exclusive': 6}.get(cat)
    if rank is None:
        rank = {137: 5, 138: 5, 140: 5, 142: 5, 345: 5, 347: 5, 144: 5, 145: 5, 146: 5, 483: 5, 484: 5, 488: 5, 485: 4, 480: 4, 481: 4, 482: 4,
                486: 6, 487: 0, 442: 0, 425: 0, 479: 0, 349: 1, 133: 0, 175: 0, 447: 0, 408: 0, 410: 0, 387: 0, 390: 0, 393: 0, 94: 5,
                86: 3, 165: 4, 167: 4, 239: 2, 240: 2, 276: 5, 293: 5, 353: 4, 363: 4, 360: 5, 446: 6}.get(i)
    if rank is None:
        if cat in ('Legendary',): rank = 6
        else: rank = 0
    steps = STEPS.get(i)
    if not steps and cat == 'Breed only': steps = [r['where']]
    if not steps and cat in ('Evolve', 'Trade evolution'): steps = [EVO[i]] + ([r['block']] if r['block'] else [])
    fam = chain[SP[i]['evolution_chain_id']]
    OUT.append(dict(id=i, n=r['name'], g=r['gen'], c=cat, w=r['where'], src=r['game'], need=r['block'], cp=r['copies'] or 0,
                    rank=rank, steps=steps or [], tr=transfer(r), fam=fam, pre=PRE.get(i), evo=EVO.get(i, '')))

if __name__ == '__main__':
    json.dump(OUT, open(sys.argv[1], 'w'), ensure_ascii=False, separators=(',', ':'))
    print(collections.Counter(TIERS[o['rank']] for o in OUT))
    for o in OUT:
        if o['id'] in (16, 25, 41, 131, 147, 113, 2, 65, 94, 143, 150, 86, 238, 371, 1, 429): print(o['id'], o['n'], TIERS[o['rank']], '|', o['tr'], '|', o['steps'][:1])
