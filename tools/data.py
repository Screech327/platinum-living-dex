"""Builds the final 493-row dataset for the living dex tracker."""
import sys, collections
sys.path.insert(0, '/home/claude/scripts')
from summ import classify, fmt_group
from evo import EVO, PRE, NAMES, SP

CART = {'ruby': 'Ruby', 'sapphire': 'Sapphire', 'emerald': 'Emerald', 'firered': 'FireRed', 'leafgreen': 'LeafGreen'}
TWO_DS = '2nd DS + 2nd Gen 4 cart (trade)'

# ---------------------------------------------------------------- hand-checked rows
# (category, where/how, source game, blocker/gotcha)
M = {}
def m(i, cat, where, game='Platinum', block=''):
    M[i] = (cat, where, game, block)

# Starters
for i in (1, 4, 7):
    m(i, 'Other cart', 'Get ONE from FireRed/LeafGreen (starter pick) or HG/SS (Prof. Oak gives one after you beat Red), move it to Platinum, then breed it with Ditto for the extra copies.',
      'FireRed/LeafGreen or HG/SS', 'Breed copies with Ditto')
for i in (152, 155, 158):
    m(i, 'Other cart', 'Get ONE from HG/SS (starter pick) or Emerald (Prof. Birch gives one after you complete the Hoenn Dex), then breed it with Ditto for the extra copies.',
      'HG/SS or Emerald', 'Breed copies with Ditto')
for i in (252, 255, 258):
    m(i, 'Other cart', 'Get ONE from Ruby/Sapphire/Emerald (starter pick) or HG/SS (Steven in Silph Co. after you beat Red), then breed it with Ditto for the extra copies.',
      'R/S/E or HG/SS', 'Breed copies with Ditto')
for i in (387, 390, 393):
    m(i, 'Gift', 'Platinum gives ONE starter (Route 201, Lv5). Get the other two by starting Diamond/Pearl and trading, then breed each with Ditto for copies.',
      'Platinum + Diamond/Pearl', 'Other two need Diamond/Pearl + trade')

# Not in Platinum: version exclusives / other carts
m(198, 'Version exclusive', 'Eterna Forest at NIGHT (20%, Lv10–11). Also HG/SS Route 7 at night.', 'Diamond (or HG/SS)', 'Night only')
m(200, 'Version exclusive', 'Eterna Forest at NIGHT (20%, Lv10–11). Also HG/SS Johto Safari Zone at night.', 'Pearl (or HG/SS)', 'Night only')
m(431, 'Version exclusive', 'Route 218 (grass, 15%, Lv29–30) or Route 222 (20%, Lv40).', 'Pearl', 'Pearl only')
m(434, 'Version exclusive', 'Route 206 (grass, 25%, Lv14–16) — under Cycling Road.', 'Diamond', 'Diamond only')
m(328, 'Other cart', 'Not in Platinum. Easiest: Route 111 desert in Ruby/Sapphire/Emerald (35%, needs Go-Goggles) or Emerald Mirage Tower (50%). Diamond/Pearl Route 228 is only 2%.', 'R/S/E (or D/P)', 'Not in Platinum')
m(366, 'Other cart', 'Not in Platinum. HG/SS Sea Route 19 (Surf, 60%), or Diamond/Pearl Routes 219/221 (Super Rod, 15%), or Gen 3 underwater (Dive).', 'HG/SS, Diamond/Pearl or R/S/E', 'Not in Platinum')
m(143, 'Other cart', 'HG/SS Route 11 or 12 (wake with Poké Flute, Lv50, one only), or FireRed/LeafGreen Routes 12 & 16 (TWO). Then breed it with a Full Incense for Munchlax.', 'HG/SS or FireRed/LeafGreen', 'This is the Munchlax shortcut')
m(150, 'Legendary', 'Cerulean Cave B1F, Lv70. HG/SS: needs all 8 Kanto badges. FR/LG: needs the Sevii Islands Network Machine fixed.', 'HG/SS or FireRed/LeafGreen', 'Post-game')
m(243, 'Legendary', 'Roams Johto after the Burned Tower event (Lv40). Or FR/LG: one beast roams Kanto (depends on your starter).', 'HG/SS (or FR/LG)', 'Roamer — Mean Look/sleep')
m(244, 'Legendary', 'Roams Johto after the Burned Tower event (Lv40). Or FR/LG: one beast roams Kanto (depends on your starter).', 'HG/SS (or FR/LG)', 'Roamer — Mean Look/sleep')
m(245, 'Legendary', 'HG/SS: static encounter at the end of Eusine\'s Suicune chase (Route 25 in HG / Bell Tower in SS), Lv40. Or FR/LG roamer (starter-dependent).', 'HG/SS (or FR/LG)', '')
m(249, 'Legendary', 'SoulSilver: Whirl Islands during the story (Lv45). HeartGold: Whirl Islands post-game with the Silver Wing (Lv70).', 'HG/SS', 'Either version works')
m(250, 'Legendary', 'HeartGold: Bell Tower during the story (Lv45). SoulSilver: Bell Tower post-game with the Rainbow Wing (Lv70).', 'HG/SS', 'Either version works')
m(377, 'Legendary', 'Catch in Ruby/Sapphire/Emerald (Braille puzzle chambers) and Pal Park it over. Platinum\'s own Regi caves only open for an EVENT (fateful) Regigigas — the Snowpoint one does not count.', 'Ruby/Sapphire/Emerald', 'Needed for Regigigas')
m(378, 'Legendary', 'Catch in Ruby/Sapphire/Emerald (Braille puzzle chambers) and Pal Park it over. Platinum\'s own Regi caves only open for an EVENT (fateful) Regigigas — the Snowpoint one does not count.', 'Ruby/Sapphire/Emerald', 'Needed for Regigigas')
m(379, 'Legendary', 'Catch in Ruby/Sapphire/Emerald (Braille puzzle chambers) and Pal Park it over. Platinum\'s own Regi caves only open for an EVENT (fateful) Regigigas — the Snowpoint one does not count.', 'Ruby/Sapphire/Emerald', 'Needed for Regigigas')
m(380, 'Legendary', 'Roams Kanto in HeartGold (post-game) or roams Hoenn in Sapphire (post-game). Emerald: depends on the TV colour you pick at the start.', 'HeartGold or Sapphire', 'Roamer — Mean Look/sleep')
m(381, 'Legendary', 'Roams Kanto in SoulSilver (post-game) or roams Hoenn in Ruby (post-game). Emerald: depends on the TV colour you pick at the start.', 'SoulSilver or Ruby', 'Roamer — Mean Look/sleep')
m(382, 'Legendary', 'Emerald: Marine Cave (post-game). Sapphire: Cave of Origin (story). HeartGold: Embedded Tower with the Blue Orb from Mr. Pokémon (after Red).', 'Emerald, Sapphire or HeartGold', '')
m(383, 'Legendary', 'Emerald: Terra Cave (post-game). Ruby: Cave of Origin (story). SoulSilver: Embedded Tower with the Red Orb from Mr. Pokémon (after Red).', 'Emerald, Ruby or SoulSilver', '')
m(384, 'Legendary', 'Sky Pillar in Ruby/Sapphire/Emerald (Lv70, post-story). HG/SS: Embedded Tower with the Jade Orb (Oak gives it after you show him Embedded Tower Kyogre AND Groudon).', 'R/S/E (or HG/SS)', '')

# Events
m(151, 'EVENT', 'Event distribution only (Old Sea Map — never released outside Japan). Fan-run WFC is the only practical route.', 'Event / fan WFC', 'Event only')
m(251, 'EVENT', 'Event distribution only (Colosseum bonus disc / WFC). The HG/SS GS Ball event itself needs an event Celebi.', 'Event / fan WFC', 'Event only')
m(385, 'EVENT', 'Event distribution only (Colosseum bonus disc / WFC).', 'Event / fan WFC', 'Event only')
m(386, 'EVENT', 'Event distribution only (Aurora Ticket / WFC). Forme depends on which game it\'s in.', 'Event / fan WFC', 'Event only')
m(489, 'EVENT', 'Breed a Manaphy with Ditto — the egg hatches into Phione.', 'Needs Manaphy', 'Needs event Manaphy')
m(490, 'EVENT', 'Pokémon Ranger special mission egg, or WFC distribution.', 'Event / fan WFC / Ranger', 'Event only')
m(491, 'EVENT', 'Member Card (event item) → Harbor Inn in Canalave → Newmoon Island, Lv50.', 'Event / fan WFC', 'Event item')
m(492, 'EVENT', 'Oak\'s Letter (event item) → Route 224 → Flower Paradise, Lv30.', 'Event / fan WFC', 'Event item')
m(493, 'EVENT', 'Azure Flute (never officially distributed) → Spear Pillar → Hall of Origin, Lv80.', 'Event / fan WFC', 'Event item')

# Platinum legendaries
m(144, 'Legendary', 'After the National Dex, talk to Prof. Oak in Eterna City — Articuno, Zapdos and Moltres start roaming Sinnoh (Lv60).', 'Platinum', 'Roamer — Mean Look/sleep')
m(145, 'Legendary', 'After the National Dex, talk to Prof. Oak in Eterna City — Articuno, Zapdos and Moltres start roaming Sinnoh (Lv60).', 'Platinum', 'Roamer — Mean Look/sleep')
m(146, 'Legendary', 'After the National Dex, talk to Prof. Oak in Eterna City — Articuno, Zapdos and Moltres start roaming Sinnoh (Lv60).', 'Platinum', 'Roamer — Mean Look/sleep')
m(480, 'Legendary', 'Acuity Cavern (Lake Acuity), Lv50 — after the story.', 'Platinum', 'Save first')
m(481, 'Legendary', 'Interact in Verity Cavern after the story; it then roams Sinnoh (Lv50).', 'Platinum', 'Roamer — Mean Look/sleep')
m(482, 'Legendary', 'Valor Cavern (Lake Valor), Lv50 — after the story.', 'Platinum', 'Save first')
m(483, 'Legendary', 'Post-National Dex: talk to Cynthia\'s grandmother in Celestic Town, collect the Adamant Orb in Mt. Coronet, then go to Spear Pillar (Lv70).', 'Platinum', 'Needs Adamant Orb')
m(484, 'Legendary', 'Post-National Dex: talk to Cynthia\'s grandmother in Celestic Town, collect the Lustrous Orb in Mt. Coronet, then go to Spear Pillar (Lv70).', 'Platinum', 'Needs Lustrous Orb')
m(485, 'Legendary', 'Stark Mountain, innermost chamber (Lv50) — after the Buck/Charon events at Stark Mountain.', 'Platinum', 'Post-National Dex')
m(486, 'Legendary', 'Snowpoint Temple B5F, Lv1 (yes, level 1). Needs Regirock + Regice + Registeel in your party.', 'Platinum', 'Needs all 3 Regis')
m(487, 'Legendary', 'Distortion World during the story (Lv47). If you KO it, it reappears in Turnback Cave after the Elite Four.', 'Platinum', 'Save first')
m(488, 'Legendary', 'Post-National Dex: Canalave sailor\'s son quest → Fullmoon Island. After you see it, it roams Sinnoh (Lv50).', 'Platinum', 'Roamer — Mean Look/sleep')

# Platinum specials
m(479, 'Special', 'Old Chateau 2F, left room: check the TV at NIGHT (Lv20).', 'Platinum', 'Night only')
m(442, 'Special', 'Put the Odd Keystone in the Hallowed Tower (Route 209), talk to 32 people in the Underground, then check the tower (Lv25).', 'Platinum', 'Odd Keystone + 32 Underground talks')
m(425, 'Special', 'Valley Windworks gate on FRIDAYS, after clearing the Galactic grunts there (Lv15). One per week — breed Drifblim for extras.', 'Platinum', 'Fridays only')
m(349, 'Special', 'Mt. Coronet B1F lake (the big room off Route 211 W): fish only 4 hidden tiles, which change daily. 50% Feebas even on the right tile.', 'Platinum', 'Worst grind — need 2')
m(133, 'Gift', 'Bebe in Hearthome City gives one Eevee (Lv20). For the other 7, use Trophy Garden Eevee or breed with Ditto.', 'Platinum', 'Need 8 total')
m(137, 'Gift', 'Man inside the Veilstone Pokémon Center, after the National Dex (Lv25). One only — breed with Ditto for copies.', 'Platinum', 'One-time gift — breed copies')
m(175, 'Gift', 'Cynthia gives a Togepi egg in Eterna City (after Team Galactic\'s building). Copies: Poké Radar Route 230, or breed.', 'Platinum', 'One-time egg — breed copies')
m(447, 'Gift', 'Riley gives a Riolu egg after you clear Iron Island. One only — evolve it, then breed Lucario for a second Riolu.', 'Platinum', 'One-time egg — breed copies')
m(94, 'Dual-slot', 'Old Chateau 2F (the room with eyes on the walls) with ANY Gen 3 cart in the GBA slot. Far easier than trading a Haunter.', 'Any Gen 3 cart in GBA slot', 'DS/DS Lite + any GBA cart')

FOSSIL = {138: ('Helix Fossil', True), 140: ('Dome Fossil', True), 142: ('Old Amber', True), 345: ('Root Fossil', True), 347: ('Claw Fossil', True),
          408: ('Skull Fossil', False), 410: ('Armor Fossil', False)}
for i, (f, nat) in FOSSIL.items():
    if i == 408:
        m(i, 'Fossil', 'Dig a Skull Fossil in the Underground → Oreburgh Mining Museum (Lv20). Platinum only gives Skull Fossils if your Trainer ID is ODD.', 'Platinum (odd TID) or Diamond', 'Even TID → get it from Diamond')
    elif i == 410:
        m(i, 'Fossil', 'Dig an Armor Fossil in the Underground → Oreburgh Mining Museum (Lv20). Platinum only gives Armor Fossils if your Trainer ID is EVEN.', 'Platinum (even TID) or Pearl', 'Odd TID → get it from Pearl')
    else:
        m(i, 'Fossil', f'Dig {"an" if f[0] in "AEIOU" else "a"} {f} in the Underground (only appears after the National Dex) → Oreburgh Mining Museum (Lv20).', 'Platinum', 'Post-National Dex')

# Breed-only in Platinum (base form never appears wild)
INC = {360: ('Wobbuffet', 'Lax Incense (Route 225)'), 446: ('Snorlax', 'Full Incense (Veilstone City)'),
       298: ('Marill/Azumarill', 'Sea Incense (Route 204)'), 438: ('Sudowoodo', 'Rock Incense (Fuego Ironworks)'),
       439: ('Mr. Mime', 'Odd Incense (Solaceon Ruins)'), 440: ('Chansey/Blissey', 'Luck Incense (Ravaged Path)'),
       433: ('Chimecho', 'Pure Incense (Route 221)'), 406: ('Roselia/Roserade', 'Rose Incense (Route 212)'),
       458: ('Mantine', 'Wave Incense (Route 210)')}
m(360, 'Breed only', 'Day-Care: Wobbuffet holding a Lax Incense (Route 225) + Ditto. Or Emerald\'s Lavaridge Town egg / Mirage Island.', 'Platinum (or R/S/E)', 'Needs Lax Incense')
m(446, 'Breed only', 'BEST: Day-Care Snorlax (from HG/SS or FR/LG) holding a Full Incense (Veilstone City) + Ditto. Honey trees: only 4 hidden trees, ~1% — avoid.', 'Platinum + Snorlax from HG/SS', 'Needs Snorlax + Full Incense')
m(86, 'Breed only', 'Day-Care: Dewgong (Victory Road) + Ditto. Or wild in Diamond (Sea Route 226) / HG/SS Seafoam Islands.', 'Platinum (or Diamond, HG/SS)', 'Breed')
m(165, 'Breed only', 'Day-Care: Ledian (Route 229, mornings) + Ditto. Or wild in HG/SS mornings (Route 30/31).', 'Platinum (or HG/SS)', 'Breed')
m(167, 'Breed only', 'Day-Care: Ariados (Route 229, nights) + Ditto. Or wild in HG/SS at night (Route 30/37).', 'Platinum (or HG/SS)', 'Breed')
m(239, 'Breed only', 'Day-Care: Electabuzz (Route 222) + Ditto.', 'Platinum', 'Breed')
m(240, 'Breed only', 'Day-Care: Magmar (Fuego Ironworks) + Ditto.', 'Platinum', 'Breed')
m(276, 'Breed only', 'Day-Care: Swellow (Poké Radar, Route 213) + Ditto. Or wild in Ruby/Sapphire/Emerald (Route 104/116).', 'Platinum (or R/S/E)', 'Breed')
m(293, 'Breed only', 'Day-Care: Loudred (Poké Radar, Mt. Coronet summit) + Ditto. Or wild in HG/SS (Route 32) or R/S/E (Rusturf Tunnel).', 'Platinum (or HG/SS, R/S/E)', 'Breed')
m(353, 'Breed only', 'Day-Care: Banette (Routes 225/226 at night) + Ditto. Or wild in Sapphire/Emerald (Mt. Pyre).', 'Platinum (or R/S/E)', 'Breed')
m(363, 'Breed only', 'Day-Care: Sealeo (Sea Route 230) + Ditto. Or wild in Pearl (Sea Route 226) / Gen 3 Shoal Cave.', 'Platinum (or Pearl, R/S/E)', 'Breed')

GENDER = {475: 'Male Kirlia only', 478: 'Female Snorunt only', 416: 'Female Combee only', 413: 'Female Burmy only', 414: 'Male Burmy only'}

HONEY = {415: 'Combee ~32%', 412: 'Burmy ~22%', 265: 'Wurmple ~14%', 420: 'Cherubi ~11%', 190: 'Aipom ~10%', 214: 'Heracross ~1% (≈3.5% on a Munchlax tree)'}

def item_block(t):
    for k in ('Leaf Stone', 'Fire Stone', 'Water Stone', 'Thunder Stone', 'Moon Stone', 'Sun Stone', 'Dusk Stone', 'Dawn Stone', 'Shiny Stone',
              'Oval Stone', 'Razor Claw', 'Razor Fang', 'King’s Rock', 'Metal Coat', 'Dragon Scale', 'Upgrade', 'Dubious Disc', 'Protector',
              'Electirizer', 'Magmarizer', 'Reaper Cloth', 'Deep Sea Tooth', 'Deep Sea Scale'):
        if k in t: return 'Needs ' + k.replace('Upgrade', 'Up-Grade')
    return ''

def build():
    rows = {}
    obt = {}
    # two passes so later-numbered pre-evolutions (babies) resolve
    for _ in range(2):
        for i in range(1, 494):
            b = classify(i)
            pre = PRE.get(i)
            pre_ok = pre is not None and obt.get(pre, False)
            trade = EVO.get(i, '').startswith('Trade ')
            alts = []
            if i in M:
                cat, where, game, block = M[i]
            elif 'wild' in b:
                cat, game = 'Wild', 'Platinum'
                where = fmt_group(b['wild'])
                block = ''
                if pre: alts.append('or evolve: ' + EVO[i])
            elif pre_ok:
                cat = 'Trade evolution' if trade else 'Evolve'
                where = EVO[i]
                game = 'Platinum'
                block = TWO_DS if trade else item_block(EVO[i])
                if i in GENDER: block = GENDER[i] + ('; ' + block if block else '')
            elif 'trophy' in b:
                cat, where, game, block = 'Trophy Garden', 'Trophy Garden (Pokémon Mansion, Route 212) on days Mr. Backlot names it ' + fmt_group(b['trophy']).replace('Trophy Garden ', '') + '. Save before talking to him — soft-reset to get a different species.', 'Platinum', 'Post-National Dex · daily'
            elif 'honey' in b:
                cat, where, game, block = 'Honey tree', f'Slather Honey on any of the 21 honey trees, come back 6+ REAL hours later. {HONEY.get(i, "")}.', 'Platinum', 'Real-time wait'
            elif 'swarm' in b:
                cat, where, game, block = 'Swarm', 'Mass outbreak: ' + fmt_group(b['swarm']) + '. Ask Dawn\'s/Lucas\' sister in Sandgem Town which species is swarming today (fixed per day — resetting won\'t change it).', 'Platinum', 'Post-Hall of Fame · daily swarm'
            elif 'radar' in b:
                cat, where, game, block = 'Poké Radar', fmt_group(b['radar']) + ' — only appears in Poké Radar patches.', 'Platinum', 'Post-National Dex · Poké Radar'
            elif 'marsh-rot' in b:
                cat, where, game, block = 'Great Marsh (daily)', 'Great Marsh daily rotation (check the binoculars on the 2nd floor of the Marsh building). Appears at 10% in one area on days it is picked.', 'Platinum', 'Post-National Dex · daily'
            elif any(k.startswith('slot2') for k in b):
                carts = sorted({k[6:] for k in b if k.startswith('slot2')})
                cat = 'Dual-slot'
                where = ' | '.join(f"{CART[c]} in GBA slot: {fmt_group(b['slot2-' + c], 2)}" for c in carts)
                game = ' / '.join(CART[c] for c in carts) + ' in GBA slot'
                block = 'DS/DS Lite + ' + ' or '.join(CART[c] for c in carts)
            elif pre is not None:
                cat = 'Trade evolution' if trade else 'Evolve'
                where = EVO[i]
                game = rows.get(pre, {}).get('game', '?')
                block = TWO_DS if trade else item_block(EVO[i])
                if i in GENDER: block = GENDER[i] + ('; ' + block if block else '')
            else:
                cat, where, game, block = 'TODO', '', '', ''
            # if an Evolve row is also catchable somewhere special, mention it
            if cat in ('Evolve', 'Trade evolution'):
                for k, lab in (('radar', 'Poké Radar'), ('swarm', 'Swarm'), ('marsh-rot', 'Great Marsh rotation'), ('trophy', 'Trophy Garden')):
                    if k in b: alts.append(f'also {lab}: ' + fmt_group(b[k], 2))
                slots = sorted({k[6:] for k in b if k.startswith('slot2')})
                if slots and i != 94: alts.append('also dual-slot (' + '/'.join(CART[c] for c in slots) + '): ' + fmt_group(b['slot2-' + slots[0]], 1))
            if cat == 'Trophy Garden' and i in INC: alts.append(f'or breed: {INC[i][0]} holding {INC[i][1]} + Ditto')
            if cat == 'Wild' and i in HONEY: alts.append('also honey trees (' + HONEY[i] + ')')
            if alts: where = where + ' · ' + ' · '.join(alts)
            if cat in ('Evolve', 'Trade evolution') and pre in rows and (rows[pre]['cat'] == 'Version exclusive' or pre in (328, 366)):
                src = rows[pre]['game']
                block = (block + '; ' if block else '') + f'{NAMES[pre]} comes from {src}'
            rows[i] = dict(i=i, name=NAMES[i], gen=int(SP[i]['generation_id']), cat=cat, where=where, game=game, block=block)
            obt[i] = cat not in ('TODO', 'EVENT', 'Breed only') or (cat == 'Breed only' and False)
    # ---- copies: each Evolve/Trade member consumes one individual of its nearest non-evolve ancestor
    need = collections.Counter()
    for i, r in rows.items():
        if r['cat'] in ('Evolve', 'Trade evolution') and i != 292:  # Shedinja is free with Ninjask
            j = i
            while j in PRE and rows[j]['cat'] in ('Evolve', 'Trade evolution'):
                j = PRE[j]
            need[j] += 1
    for i, r in rows.items():
        r['copies'] = need[i] + 1 if need[i] else None
    return rows

if __name__ == '__main__':
    R = build()
    for i, r in R.items():
        print(f"{i}\t{r['name']}\t{r['copies'] or ''}\t{r['cat']}\t{r['game']}\t{r['block']}\t{r['where']}")
