import csv, collections
D = '/home/claude/data/'
def rd(f): return list(csv.DictReader(open(D + f, encoding='utf-8')))
SP = {int(r['id']): r for r in rd('pokemon_species.csv') if int(r['id']) <= 493}
NAMES = {int(r['pokemon_species_id']): r['name'] for r in rd('pokemon_species_names.csv') if r['local_language_id'] == '9' and int(r['pokemon_species_id']) <= 493}
ITEMS = {r['item_id']: r['name'] for r in rd('item_names.csv') if r['local_language_id'] == '9'}
MOVES = {'246': 'AncientPower', '458': 'Double Hit', '102': 'Mimic', '205': 'Rollout'}

# Gen-4-correct overrides (later games changed several of these)
OVR = {
    462: 'Level up Magneton inside Mt. Coronet',
    476: 'Level up Nosepass inside Mt. Coronet',
    470: 'Level up Eevee near the Moss Rock (Eterna Forest)',
    471: 'Level up Eevee near the Ice Rock (Route 217)',
    350: 'Level up Feebas with Beauty maxed (feed dry/blue Poffins)',
    196: 'Level up Eevee with high friendship during the DAY',
    197: 'Level up Eevee with high friendship at NIGHT',
    292: 'Appears when Nincada evolves at Lv20 — needs an empty party slot AND a spare Poké Ball in the bag',
    291: 'Nincada Lv20',
    106: 'Tyrogue Lv20 with Attack > Defense',
    107: 'Tyrogue Lv20 with Attack < Defense',
    237: 'Tyrogue Lv20 with Attack = Defense',
    266: 'Wurmple Lv7 (Silcoon vs Cascoon is decided by personality value — random)',
    268: 'Wurmple Lv7 (Silcoon vs Cascoon is decided by personality value — random)',
    413: 'FEMALE Burmy Lv20 — cloak at evolution is permanent',
    414: 'MALE Burmy Lv20',
    416: 'FEMALE Combee Lv21 (males never evolve)',
    475: 'Dawn Stone on a MALE Kirlia',
    478: 'Dawn Stone on a FEMALE Snorunt',
    226: 'Level up Mantyke with a Remoraid in the party',
    424: 'Level up Aipom knowing Double Hit (learned at Lv32)',
    469: 'Level up Yanma knowing AncientPower (learned at Lv33)',
    465: 'Level up Tangela knowing AncientPower (learned at Lv33)',
    463: 'Level up Lickitung knowing Rollout (learned at Lv33)',
    473: 'Level up Piloswine knowing AncientPower (Lv1 move: Move Relearner in Pastoria for a Heart Scale, or Platinum Move Tutor)',
    185: 'Level up Bonsly knowing Mimic (learned at Lv17)',
    122: 'Level up Mime Jr. knowing Mimic (learned at Lv18)',
    242: 'Level up Chansey with high friendship',
    113: 'Level up Happiny holding an Oval Stone during the DAY',
    472: 'Level up Gligar holding a Razor Fang at NIGHT',
    461: 'Level up Sneasel holding a Razor Claw at NIGHT',
    358: 'Level up Chingling with high friendship at NIGHT',
    448: 'Level up Riolu with high friendship during the DAY',
    68: 'Trade Machoke', 76: 'Trade Graveler', 94: 'Trade Haunter',
    65: 'Trade Kadabra (an Everstone will NOT stop this one in Gen 4)',
}

def evo_text(i):
    if i in OVR: return OVR[i]
    rows = [r for r in rd_evo if int(r['evolved_species_id']) == i]
    if not rows: return ''
    r = rows[0]
    pre = NAMES[int(SP[i]['evolves_from_species_id'])]
    t = r['evolution_trigger_id']
    bits = []
    if t == '1':
        if r['minimum_level']: bits.append(f"{pre} Lv{r['minimum_level']}")
        else: bits.append(f"Level up {pre}")
        if r['minimum_happiness']: bits.append('with high friendship')
        if r['held_item_id']: bits.append(f"holding {ITEMS[r['held_item_id']]}")
        if r['time_of_day']: bits.append(f"({r['time_of_day'].upper()})")
        if r['gender_id']: bits.append('(female)' if r['gender_id'] == '1' else '(male)')
        if r['known_move_id']: bits.append(f"knowing move {r['known_move_id']}")
    elif t == '2':
        bits.append(f"Trade {pre}")
        if r['held_item_id']: bits.append(f"holding {ITEMS[r['held_item_id']]}")
    elif t == '3':
        bits.append(f"{ITEMS[r['trigger_item_id']]} on {pre}")
        if r['gender_id']: bits.append('(female)' if r['gender_id'] == '1' else '(male)')
    else:
        bits.append(f"evolve {pre} ({t})")
    return ' '.join(bits)

rd_evo = rd('pokemon_evolution.csv')
EVO = {i: evo_text(i) for i in SP if SP[i]['evolves_from_species_id']}
PRE = {i: int(SP[i]['evolves_from_species_id']) for i in SP if SP[i]['evolves_from_species_id']}
if __name__ == '__main__':
    for i, t in EVO.items(): print(i, NAMES[i], '|', t)
