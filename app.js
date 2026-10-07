/* Platinum Living Dex — all state lives in localStorage under one key, so updating the site never touches it. */
(() => {
'use strict';
const DEX = window.DEX, TIERS = window.TIERS;
const BY = new Map(DEX.map(d => [d.id, d]));
const SPRITE = id => `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-iv/platinum/${id}.png`;
const KEY = 'pld-v1';
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const pad = n => String(n).padStart(3, '0');
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat()) if (k != null) e.append(k);
  return e;
};
const img = (id, cls = 'px') => el('img', { class: cls, src: SPRITE(id), alt: '', loading: 'lazy', decoding: 'async', width: 64, height: 64 });

/* ---------------- state ---------------- */
let S = { boxed: {}, have: {}, notes: {}, timers: {}, seen: {}, caught: {} };
const fresh = () => ({ boxed: {}, have: {}, notes: {}, timers: {}, seen: {}, caught: {} });
let storageOK = true;
function load() {
  try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); }
  catch (e) { storageOK = false; }
}
let saveT;
function save() {
  clearTimeout(saveT);
  saveT = setTimeout(() => { try { localStorage.setItem(KEY, JSON.stringify(S)); storageOK = true; } catch (e) { storageOK = false; toast('This browser is blocking saving — download a backup from More.'); } }, 120);
}
const isGot = id => !!S.boxed[id];
const gotCount = () => Object.keys(S.boxed).length;

/* ---------------- derived data ---------------- */
const REGIONS = [['Kanto', 1, 151], ['Johto', 152, 251], ['Hoenn', 252, 386], ['Sinnoh', 387, 493]];
const regionOf = id => REGIONS.find(r => id >= r[1] && id <= r[2])[0];
const GAMES = [
  { name: 'Platinum', note: 'Everything you catch, evolve or breed on the Platinum cart itself.', test: d => d.tr === 'Native to Platinum' && d.c !== 'EVENT' && !/Diamond|Pearl|HG\/SS|HeartGold|SoulSilver|FireRed|LeafGreen|R\/S\/E|Ruby|Sapphire|Emerald|Gen 3/.test(d.src) },
  { name: 'Diamond', note: 'Murkrow and Stunky, plus fallbacks for Clamperl, Trapinch, Seel and the Skull Fossil. Trade to Platinum.', test: d => /Diamond|D\/P/.test(d.src) },
  { name: 'Pearl', note: 'Misdreavus and Glameow, plus fallbacks for Clamperl, Trapinch, Spheal and the Armor Fossil. Trade to Platinum.', test: d => /Pearl|D\/P/.test(d.src) },
  { name: 'HeartGold / SoulSilver', note: 'Legendaries, starters and Snorlax — and Pal Park with no daily limit. Trade to Platinum.', test: d => /HG\/SS|HeartGold|SoulSilver/.test(d.src) },
  { name: 'FireRed / LeafGreen', note: 'Dual-slot spawns (cart in the GBA slot) and Pal Park sources like Kanto starters and Snorlax.', test: d => /FireRed|LeafGreen|FR\/LG|Any Gen 3/.test(d.src) },
  { name: 'Ruby / Sapphire / Emerald', note: 'Dual-slot spawns and the Gen 3 legendaries via Pal Park.', test: d => /Ruby|Sapphire|Emerald|R\/S\/E|Any Gen 3/.test(d.src) },
  { name: 'Spin-offs', note: 'Pokémon Ranger (Manaphy → Phione) and My Pokémon Ranch on Wii (Mew, Phione).', test: d => d.c === 'Spin-off' },
  { name: 'Events', note: 'Event-only. Fan-run WFC servers still hand these out.', test: d => d.c === 'EVENT' },
];
const TIER_NOTES = [
  'Available while you play through the story.',
  'Needs the Good Rod (Route 209, after the 3rd badge).',
  'Needs Surf (5th badge).',
  'Victory Road — needs all 8 badges.',
  'Unlocks after you enter the Hall of Fame (Battle Zone, Route 224+, Super Rod, Stark Mountain).',
  'Unlocks after the National Dex (Poké Radar, swarms, Trophy Garden, dual-slot, older fossils).',
  'Comes from one of your other carts — check its steps.',
  'Event distribution only.',
];
// copies: each evolved species consumes one of its nearest obtainable ancestor
const COPY = new Map(); // source id -> [kids]
for (const d of DEX) {
  if ((d.c === 'Evolve' || d.c === 'Trade evolution') && d.id !== 292) {
    let j = d.id;
    while (BY.get(j).pre && (BY.get(j).c === 'Evolve' || BY.get(j).c === 'Trade evolution')) j = BY.get(j).pre;
    if (!COPY.has(j)) COPY.set(j, []);
    COPY.get(j).push(d.id);
  }
}

/* ---------------- toast + confetti ---------------- */
let toastT;
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), 1800); }
function confetti() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const c = $('#confetti'), x = c.getContext('2d');
  c.width = innerWidth * devicePixelRatio; c.height = innerHeight * devicePixelRatio; x.scale(devicePixelRatio, devicePixelRatio);
  const cols = ['#e2b23c', '#4fcf86', '#6aa3ff', '#ff6b6b', '#c69cff'];
  const ps = Array.from({ length: 140 }, () => ({ x: innerWidth / 2, y: innerHeight / 3, vx: (Math.random() - .5) * 12, vy: Math.random() * -12 - 2, r: Math.random() * 6 + 3, c: cols[Math.random() * cols.length | 0], a: Math.random() * 6 }));
  let f = 0;
  (function tick() {
    x.clearRect(0, 0, innerWidth, innerHeight);
    for (const p of ps) { p.vy += .35; p.x += p.vx; p.y += p.vy; p.a += .2; x.save(); x.translate(p.x, p.y); x.rotate(p.a); x.fillStyle = p.c; x.fillRect(-p.r / 2, -p.r / 4, p.r, p.r / 2); x.restore(); }
    if (++f < 110) requestAnimationFrame(tick); else x.clearRect(0, 0, innerWidth, innerHeight);
  })();
}

/* ---------------- toggling ---------------- */
const MILESTONES = [25, 50, 100, 150, 200, 250, 300, 350, 400, 450, 484, 493];
function setGot(id, on) {
  const before = gotCount();
  if (on) S.boxed[id] = Date.now(); else delete S.boxed[id];
  save();
  const d = BY.get(id), n = gotCount();
  toast(on ? `${d.n} boxed! ${n}/493` : `${d.n} unchecked`);
  if (on) {
    const reg = REGIONS.find(r => id >= r[1] && id <= r[2]);
    const regDone = DEX.filter(x => x.id >= reg[1] && x.id <= reg[2]).every(x => isGot(x.id));
    const box = Math.ceil(id / 30), boxDone = DEX.filter(x => Math.ceil(x.id / 30) === box).every(x => isGot(x.id));
    if (MILESTONES.includes(n) && n > before) { confetti(); setTimeout(() => toast(n === 493 ? 'LIVING DEX COMPLETE! All 493!' : `Milestone: ${n} Pokémon boxed!`), 400); }
    else if (regDone) { confetti(); setTimeout(() => toast(`${reg[0]} complete!`), 400); }
    else if (boxDone) { confetti(); setTimeout(() => toast(`Box ${box} is full!`), 400); }
  }
  refresh();
}

/* ---------------- header ---------------- */
function header() {
  const n = gotCount();
  $('#gotCount').textContent = n;
  $('#gotPct').textContent = (n / 493 * 100).toFixed(1) + '%';
  $('#ring').style.strokeDashoffset = 113.1 * (1 - n / 493);
}

/* ---------------- DEX view ---------------- */
let show = 'all';
const grid = $('#grid'); const cards = new Map();
function chip(text, cls) { return el('span', { class: 'chip ' + (cls || ''), text }); }
function buildGrid() {
  const frag = document.createDocumentFragment();
  for (const d of DEX) {
    const tick = el('input', { type: 'checkbox', class: 'tick', 'aria-label': 'Boxed: ' + d.n });
    tick.addEventListener('click', e => e.stopPropagation());
    tick.addEventListener('change', () => setGot(d.id, tick.checked));
    const li = el('li', { class: 'card', tabindex: 0, 'data-id': d.id },
      el('div', { class: 'spr' }, img(d.id)),
      el('div', { class: 'info' },
        el('div', { class: 'l1' }, el('span', { class: 'num', text: '#' + pad(d.id) }), el('span', { class: 'nm', text: d.n })),
        el('div', { class: 'chips' }, chip(d.c), chip(TIERS[d.rank], 'tier' + d.rank), d.cp ? chip('catch ×' + d.cp, 'cp') : null)),
      tick);
    li.addEventListener('click', () => openDrawer(d.id));
    li.addEventListener('keydown', e => { if (e.key === 'Enter') openDrawer(d.id); });
    cards.set(d.id, { li, tick });
    frag.append(li);
  }
  grid.append(frag, el('li', { class: 'empty', id: 'noRes', hidden: true, text: 'No Pokémon match that.' }));
}
const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/♀/g, ' f').replace(/♂/g, ' m');
DEX.forEach(d => d.key = norm(d.n));
function matches(d) {
  const q = norm($('#q').value.trim());
  if (q) { if (/^#?\d+$/.test(q)) { const n = q.replace('#', ''); if (!pad(d.id).startsWith(n.padStart(Math.min(n.length, 3), '0')) && String(d.id) !== n) return false; } else if (!d.key.includes(q)) return false; }
  if (show === 'need' && isGot(d.id)) return false;
  if (show === 'got' && !isGot(d.id)) return false;
  const m = $('#fMethod').value; if (m && d.c !== m) return false;
  const t = $('#fTier').value; if (t !== '' && d.rank !== +t) return false;
  const g = $('#fGame').value; if (g !== '' && !GAMES[+g].test(d)) return false;
  const r = $('#fRegion').value; if (r && regionOf(d.id) !== r) return false;
  return true;
}
function renderGrid() {
  let shown = 0;
  for (const d of DEX) {
    const { li, tick } = cards.get(d.id), got = isGot(d.id), ok = matches(d);
    tick.checked = got; li.classList.toggle('got', got); li.hidden = !ok; if (ok) shown++;
  }
  $('#noRes').hidden = shown > 0;
  $('#resultLine').textContent = shown === 493 ? 'Showing all 493 — tap a card for details, tap the box to check it off.' : `Showing ${shown} of 493`;
}
function initFilters() {
  [...new Set(DEX.map(d => d.c))].forEach(m => $('#fMethod').append(new Option(m, m)));
  TIERS.forEach((t, i) => $('#fTier').append(new Option(t, i)));
  GAMES.forEach((g, i) => $('#fGame').append(new Option(g.name, i)));
  REGIONS.forEach(r => $('#fRegion').append(new Option(r[0], r[0])));
  ['#q', '#fMethod', '#fTier', '#fGame', '#fRegion'].forEach(s => $(s).addEventListener(s === '#q' ? 'input' : 'change', renderGrid));
  $('#qClear').addEventListener('click', () => { $('#q').value = ''; renderGrid(); $('#q').focus(); });
  $$('[data-show]').forEach(b => b.addEventListener('click', () => { show = b.dataset.show; $$('[data-show]').forEach(x => x.setAttribute('aria-pressed', x === b)); renderGrid(); }));
}

/* ---------------- BOXES view ---------------- */
let box = 1;
function renderBoxes() {
  const start = (box - 1) * 30 + 1, end = Math.min(box * 30, 493);
  $('#boxName').textContent = 'Box ' + box;
  const filled = DEX.filter(d => d.id >= start && d.id <= end && isGot(d.id)).length;
  $('#boxRange').textContent = `#${pad(start)}–#${pad(end)} · ${filled}/${end - start + 1} filled`;
  const pc = $('#pcbox'); pc.replaceChildren();
  for (let i = start; i < start + 30; i++) {
    if (i > 493) { pc.append(el('div', { class: 'slot blank' })); continue; }
    const d = BY.get(i);
    pc.append(el('button', { type: 'button', class: 'slot' + (isGot(i) ? ' got' : ''), title: `#${pad(i)} ${d.n}`, 'aria-label': `#${pad(i)} ${d.n}${isGot(i) ? ', boxed' : ''}`, onclick: () => openDrawer(i) },
      el('span', { class: 'sn', text: pad(i) }), img(i)));
  }
  const dots = $('#boxDots'); dots.replaceChildren();
  for (let b = 1; b <= 17; b++) {
    const s = (b - 1) * 30 + 1, e = Math.min(b * 30, 493);
    const full = DEX.filter(d => d.id >= s && d.id <= e).every(d => isGot(d.id));
    dots.append(el('button', { type: 'button', class: full ? 'full' : '', 'aria-current': b === box ? 'true' : 'false', 'aria-label': 'Box ' + b, text: b, onclick: () => { box = b; renderBoxes(); } }));
  }
}
function initBoxes() {
  $('#boxPrev').addEventListener('click', () => { box = box === 1 ? 17 : box - 1; renderBoxes(); });
  $('#boxNext').addEventListener('click', () => { box = box === 17 ? 1 : box + 1; renderBoxes(); });
  let sx = null;
  $('#pcbox').addEventListener('touchstart', e => sx = e.touches[0].clientX, { passive: true });
  $('#pcbox').addEventListener('touchend', e => { if (sx == null) return; const dx = e.changedTouches[0].clientX - sx; sx = null; if (Math.abs(dx) > 50) { box = dx < 0 ? (box === 17 ? 1 : box + 1) : (box === 1 ? 17 : box - 1); renderBoxes(); } });
}

/* ---------------- PLAN view ---------------- */
let plan = 'game';
const openGroups = new Set();
function group(key, name, note, ids) {
  const got = ids.filter(isGot).length;
  const det = el('details', { class: 'group' });
  if (openGroups.has(key)) det.open = true;
  det.addEventListener('toggle', () => { det.open ? openGroups.add(key) : openGroups.delete(key); if (det.open && !det.querySelector('.minis')) det.append(minis(ids)); });
  det.append(el('summary', {},
    el('span', { class: 'gname', text: name }),
    el('span', { class: 'gcount', text: `${got}/${ids.length}` }),
    el('span', { class: 'bar' }, el('i', { style: `width:${ids.length ? got / ids.length * 100 : 0}%` })),
    el('span', { class: 'gnote', text: note })));
  if (det.open) det.append(minis(ids));
  return det;
}
function minis(ids) {
  const sorted = [...ids].sort((a, b) => isGot(a) - isGot(b) || a - b);
  return el('div', { class: 'minis' }, sorted.map(id => el('button', { type: 'button', class: 'mini' + (isGot(id) ? ' got' : ''), title: `#${pad(id)} ${BY.get(id).n}`, 'aria-label': `#${pad(id)} ${BY.get(id).n}`, onclick: () => openDrawer(id) }, img(id))));
}
function renderPlan() {
  const body = $('#planBody'); body.replaceChildren();
  if (plan === 'game') GAMES.forEach((g, i) => body.append(group('g' + i, g.name, g.note, DEX.filter(g.test).map(d => d.id))));
  if (plan === 'tier') TIERS.forEach((t, i) => { const ids = DEX.filter(d => d.rank === i).map(d => d.id); if (ids.length) body.append(group('t' + i, t, TIER_NOTES[i], ids)); });
  if (plan === 'region') REGIONS.forEach(([r, a, b]) => body.append(group('r' + r, r, `#${pad(a)}–#${pad(b)}`, DEX.filter(d => d.id >= a && d.id <= b).map(d => d.id))));
}
function initPlan() { $$('[data-plan]').forEach(b => b.addEventListener('click', () => { plan = b.dataset.plan; $$('[data-plan]').forEach(x => x.setAttribute('aria-pressed', x === b)); renderPlan(); })); }

/* ---------------- TODAY view ---------------- */
const H = 3600e3;
const TIMERS = [
  { k: 'honey', name: 'Honey trees', who: 'Combee, Burmy, Cherubi, Aipom, Heracross, Wurmple', how: 'Slather every tree you pass. Come back 6+ real hours later — the honey is gone after 24 hours. The Pokémon is decided when you slather.', kind: 'window', ready: 6 * H, expire: 24 * H, btn: 'Slathered now' },
  { k: 'swarm', name: 'Swarm', who: '22 species incl. Beldum, Larvitar, Corsola, Pinsir', how: 'Ask Dawn\'s/Lucas\' sister in Sandgem Town. Needs the National Dex + Hall of Fame. Changes at midnight.', kind: 'daily', btn: 'Checked today' },
  { k: 'trophy', name: 'Trophy Garden', who: 'Ditto, Eevee, Happiny, Bonsly, Mime Jr., Azurill, Castform, Plusle, Minun…', how: 'Talk to Mr. Backlot (Pokémon Mansion, Route 212). Save first — soft-reset to get a different Pokémon.', kind: 'daily', btn: 'Checked today' },
  { k: 'marsh', name: 'Great Marsh rotation', who: 'Paras, Exeggcute, Kangaskhan, Shroomish, Gulpin, Kecleon, Skorupi, Croagunk, Carnivine, Drapion, Toxicroak', how: 'Look through the binoculars on the 2nd floor of the Great Marsh building to see today\'s Pokémon.', kind: 'daily', btn: 'Checked today' },
  { k: 'feebas', name: 'Feebas tiles', who: 'Feebas ×2 → Milotic', how: 'Mt. Coronet B1F lake. The 4 Feebas tiles move every day.', kind: 'daily', btn: 'Fished today' },
  { k: 'palpark', name: 'Pal Park (Platinum)', who: 'Anything from your Gen 3 carts', how: 'Each Gen 3 save can migrate once per 24 hours in Platinum. HG/SS has no limit — use that instead when you can.', kind: 'window', ready: 24 * H, btn: 'Migrated now' },
  { k: 'drifloon', name: 'Drifloon', who: 'Drifloon (→ Drifblim)', how: 'Fridays only, by the Valley Windworks gate.', kind: 'friday', btn: 'Caught this Friday' },
];
const fmt = ms => { const h = Math.floor(ms / H), m = Math.round((ms % H) / 60e3); return h ? `${h}h ${m}m` : `${m}m`; };
function timerStatus(t) {
  const last = S.timers[t.k], now = Date.now();
  if (t.kind === 'window') {
    if (!last) return ['Not started', ''];
    const age = now - last;
    if (age < t.ready) return [`Ready in ${fmt(t.ready - age)}`, 'wait'];
    if (t.expire && age > t.expire) return ['Expired — slather again', ''];
    return [t.expire ? `Ready! Gone in ${fmt(t.expire - age)}` : 'Ready', 'ready'];
  }
  if (t.kind === 'daily') {
    const done = last && new Date(last).toDateString() === new Date().toDateString();
    return done ? ['Done today', 'ready'] : ['Not checked today', 'wait'];
  }
  if (t.kind === 'friday') {
    const d = new Date(); const isFri = d.getDay() === 5;
    const done = last && (now - last) < 6 * 24 * H && new Date(last).getDay() === 5;
    if (done) return ['Got this week', 'ready'];
    if (isFri) return ['It\'s Friday — go get it!', 'wait'];
    const days = (5 - d.getDay() + 7) % 7; return [`Next Friday in ${days} day${days === 1 ? '' : 's'}`, ''];
  }
}
function renderToday() {
  const wrap = $('#timers'); wrap.replaceChildren();
  for (const t of TIMERS) {
    const [st, cls] = timerStatus(t);
    wrap.append(el('div', { class: 'timer' },
      el('div', { class: 'th' }, el('span', { class: 'tn', text: t.name }), el('span', { class: 'ts ' + cls, text: st })),
      el('div', { class: 'who', text: t.who }), el('p', { text: t.how }),
      el('div', { class: 'row' },
        el('button', { type: 'button', text: t.btn, onclick: () => { S.timers[t.k] = Date.now(); save(); renderToday(); toast(t.name + ' logged'); } }),
        S.timers[t.k] ? el('button', { type: 'button', class: 'ghost', text: 'Reset', onclick: () => { delete S.timers[t.k]; save(); renderToday(); } }) : null)));
  }
}

/* ---------------- COPIES view ---------------- */
let dshow = 'need';
function renderDupes() {
  const ul = $('#dupes'); ul.replaceChildren();
  const rows = [...COPY.entries()].map(([src, kids]) => ({ src, kids, need: kids.length + 1 })).sort((a, b) => b.need - a.need || a.src - b.src);
  let shown = 0;
  for (const r of rows) {
    const have = S.have[r.src] || 0, done = have >= r.need;
    if (dshow === 'need' && done) continue;
    shown++;
    const out = el('output', { text: `${have}/${r.need}` });
    const bump = n => { S.have[r.src] = Math.max(0, Math.min(r.need, (S.have[r.src] || 0) + n)); save(); renderDupes(); };
    const d = BY.get(r.src);
    ul.append(el('li', { class: 'dupe' + (done ? ' done' : '') },
      el('img', { class: 'px', src: SPRITE(r.src), alt: '', loading: 'lazy', width: 52, height: 52, onclick: () => openDrawer(r.src) }),
      el('div', {}, el('div', { class: 'dn', text: `${d.n} ×${r.need}` }),
        el('div', { class: 'dw', text: `1 stays ${d.n} + evolves into ${r.kids.map(k => BY.get(k).n + (BY.get(k).c === 'Trade evolution' ? ' (trade)' : '')).join(', ')}` })),
      el('div', { class: 'stepper' }, el('button', { type: 'button', 'aria-label': 'One fewer', text: '−', onclick: () => bump(-1) }), out, el('button', { type: 'button', 'aria-label': 'One more', text: '+', onclick: () => bump(1) }))));
  }
  if (!shown) ul.append(el('li', { class: 'empty', text: 'Every duplicate is caught. Nice.' }));
}
function initDupes() { $$('[data-dshow]').forEach(b => b.addEventListener('click', () => { dshow = b.dataset.dshow; $$('[data-dshow]').forEach(x => x.setAttribute('aria-pressed', x === b)); renderDupes(); })); }

/* ---------------- MORE view: badges, codes, backup ---------------- */
function badges() {
  const n = gotCount();
  const legends = DEX.filter(d => d.c === 'Legendary' || d.c === 'EVENT').map(d => d.id);
  const trades = DEX.filter(d => d.c === 'Trade evolution').map(d => d.id);
  const starters = [1, 4, 7, 152, 155, 158, 252, 255, 258, 387, 390, 393];
  const B = [
    ...REGIONS.map(([r, a, b]) => { const ids = DEX.filter(d => d.id >= a && d.id <= b).map(d => d.id); return ['★', `${r} complete`, ids.filter(isGot).length, ids.length]; }),
    ['◆', 'First 100', Math.min(n, 100), 100], ['◆', 'Halfway (247)', Math.min(n, 247), 247], ['◆', 'Diploma (484)', Math.min(n, 484), 484], ['♛', 'Living dex (493)', n, 493],
    ['⚡', 'Every legendary', legends.filter(isGot).length, legends.length], ['⇄', 'Every trade evo', trades.filter(isGot).length, trades.length],
    ['✿', 'All 12 starters', starters.filter(isGot).length, 12],
    ['👁', 'Sinnoh Dex seen', SIN.filter(s => isSeen(s.id)).length, 210], ['◓', 'Sinnoh Dex caught', SIN.filter(s => isCaughtR(s.id)).length, 210],
  ];
  $('#badges').replaceChildren(...B.map(([i, name, got, tot]) => el('div', { class: 'badge' + (got >= tot ? ' earned' : '') }, el('div', { class: 'bi', text: i }), el('b', { text: name }), el('span', { text: `${got}/${tot}` }))));
}
function encode() {
  const bytes = new Uint8Array(62 * 3);
  [S.boxed, S.seen, S.caught].forEach((set, k) => { for (const id of Object.keys(set)) { const i = +id - 1; bytes[k * 62 + (i >> 3)] |= 1 << (i & 7); } });
  return 'PLD2-' + btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function decode(code) {
  const m = code.trim().match(/^PLD([12])-([A-Za-z0-9_-]+)$/); if (!m) return null;
  let b = m[2].replace(/-/g, '+').replace(/_/g, '/'); while (b.length % 4) b += '=';
  const s = atob(b); const sets = [[], [], []];
  const n = m[1] === '2' ? 3 : 1;
  for (let k = 0; k < n; k++) for (let i = 0; i < 493; i++) if (s.charCodeAt(k * 62 + (i >> 3)) & (1 << (i & 7))) sets[k].push(i + 1);
  sets.v2 = n === 3;
  return sets;
}
function initMore() {
  $('#copyCode').addEventListener('click', async () => {
    const code = encode(); $('#codeBox').value = code;
    try { await navigator.clipboard.writeText(code); toast('Progress code copied'); } catch (e) { $('#codeBox').select(); toast('Code is in the box — copy it from there'); }
  });
  $('#showCode').addEventListener('click', () => { $('#codeBox').value = encode(); $('#codeBox').select(); });
  $('#loadCode').addEventListener('click', () => {
    let sets; try { sets = decode($('#codeBox').value); } catch (e) { sets = null; }
    if (!sets) { toast('That isn\'t a progress code — it starts with PLD'); return; }
    const now = Date.now(); S.boxed = {}; sets[0].forEach(id => S.boxed[id] = now);
    if (sets.v2) { S.seen = {}; S.caught = {}; sets[1].forEach(id => S.seen[id] = now); sets[2].forEach(id => S.caught[id] = now); }
    save(); refresh(); toast(`Loaded ${sets[0].length} boxed · ${sets[1].length} seen · ${sets[2].length} caught`);
  });
  $('#exportBtn').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({ app: 'platinum-living-dex', v: 1, saved: new Date().toISOString(), ...S }, null, 1)], { type: 'application/json' });
    const a = el('a', { href: URL.createObjectURL(blob), download: `living-dex-backup-${new Date().toISOString().slice(0, 10)}.json` });
    document.body.append(a); a.click(); a.remove(); toast('Backup downloaded');
  });
  $('#importFile').addEventListener('change', async e => {
    const f = e.target.files[0]; if (!f) return;
    try {
      const v = JSON.parse(await f.text());
      if (v.app !== 'platinum-living-dex' && !Array.isArray(v.caught)) throw 0;
      if (Array.isArray(v.caught)) { S.boxed = {}; v.caught.forEach(id => S.boxed[id] = Date.now()); }
      else S = Object.assign(fresh(), v); delete S.app; delete S.v; delete S.saved;
      save(); refresh(); toast(`Restored ${gotCount()} boxed Pokémon`);
    } catch (err) { toast('That file isn\'t a tracker backup'); }
    e.target.value = '';
  });
  $('#resetBtn').addEventListener('click', () => { $('#resetConfirm').hidden = false; });
  $('#resetNo').addEventListener('click', () => { $('#resetConfirm').hidden = true; });
  $('#resetYes').addEventListener('click', () => { S = fresh(); save(); refresh(); $('#resetConfirm').hidden = true; toast('Progress cleared'); });
  $('#version').textContent = 'Data version ' + window.DATA_VERSION;
}


/* ---------------- SINNOH DEX view ---------------- */
const BALL = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M2 12h20" stroke="currentColor" stroke-width="2.2"/><circle cx="12" cy="12" r="3.4" fill="var(--surface)" stroke="currentColor" stroke-width="2.2"/></svg>';
const SIN = window.SINNOH, SINBY = new Map(SIN.map(s => [s.id, s]));
const isSeen = id => !!(S.seen[id] || S.caught[id]);
const isCaughtR = id => !!S.caught[id];
let sshow = 'all';
const srows = new Map(), sopen = new Set();
SIN.forEach(s => s.key = norm(BY.get(s.id).n));
function seenHint(s) {
  if (s.tip) return s.tip;
  if (s.how === 'catch') return 'Wild: ' + s.wild.split('; ').slice(0, 2).join('; ');
  if (s.tr.length) return 'Battle: ' + s.tr[0] + (s.trAll > 1 ? ` (+${s.trAll - 1} more)` : '');
  if (s.how === 'evolve') return 'Evolve: ' + s.wild;
  return 'See details';
}
function sinFlags(s) {
  const f = [];
  if (s.how !== 'catch' && !s.tip && s.trN <= 1) f.push(['Rare sighting', 'warn']);
  if (s.how !== 'catch' && !s.tip && s.trN === 0 && s.trAll > 0) f.push(['Post-game trainer only', 'warn']);
  if (s.how === 'special' || s.tip) f.push(['Special', 'tier7']);
  if (s.how === 'catch') f.push(['Catchable in story', 'tier0']);
  else if (s.how === 'evolve') f.push(['Evolve or battle', 'tier1']);
  return f;
}
function setSeen(id, on) { if (on) S.seen[id] = Date.now(); else { delete S.seen[id]; delete S.caught[id]; } save(); afterSin(id, on ? 'seen' : null); }
function setCaughtR(id, on) { if (on) { S.caught[id] = Date.now(); S.seen[id] = S.seen[id] || Date.now(); } else delete S.caught[id]; save(); afterSin(id, on ? 'caught' : null); }
function afterSin(id, what) {
  const n = BY.get(id).n, seenN = SIN.filter(s => isSeen(s.id)).length, caughtN = SIN.filter(s => isCaughtR(s.id)).length;
  if (what === 'seen') toast(`${n} seen · ${seenN}/210`);
  else if (what === 'caught') toast(`${n} caught · ${caughtN}/210`);
  if (what && seenN === 210 && !afterSin.done) { afterSin.done = true; confetti(); setTimeout(() => toast('All 210 seen! Go see Prof. Rowan for the National Dex.'), 400); }
  if (what === 'caught' && [50, 100, 150, 210].includes(caughtN)) { confetti(); setTimeout(() => toast(`${caughtN} Sinnoh Pokémon caught!`), 400); }
  refresh();
  if (drawerId === id) openDrawer(id);
}
function sinDetail(s, inDrawer) {
  const d = BY.get(s.id);
  return el('div', { class: 'sdetail' },
    s.tip ? el('div', {}, el('h5', { text: 'How to see it' }), el('p', { style: 'margin:2px 0 0', text: s.tip })) : null,
    s.how === 'catch' ? el('div', {}, el('h5', { text: 'Catch it during the story' }), el('ul', {}, s.wild.split('; ').map(w => el('li', { text: w })))) : null,
    s.how === 'evolve' ? el('div', {}, el('h5', { text: 'Evolve' }), el('p', { style: 'margin:2px 0 0', text: s.wild })) : null,
    s.tr.length ? el('div', {}, el('h5', { text: `Trainers who use it (${s.trAll}) — battling them counts as seen` }), el('ul', {}, s.tr.map(t => el('li', { text: t })), s.more ? el('li', { text: `+${s.more} more` }) : null)) : null,
    !s.tip && !s.tr.length && s.how === 'special' ? el('p', { text: d.w }) : null,
    inDrawer ? null : el('div', { class: 'row' }, el('button', { type: 'button', class: 'ghost', text: 'Full details', onclick: () => openDrawer(s.id) })));
}
function buildSin() {
  const ul = $('#slist'), frag = document.createDocumentFragment();
  for (const s of SIN) {
    const d = BY.get(s.id);
    const eye = el('button', { type: 'button', class: 'sbtn eye', 'aria-label': 'Seen: ' + d.n, title: 'Seen', text: '👁' });
    const ball = el('button', { type: 'button', class: 'sbtn ball', 'aria-label': 'Caught: ' + d.n, title: 'Caught' }); ball.innerHTML = BALL;
    eye.addEventListener('click', () => setSeen(s.id, !isSeen(s.id)));
    ball.addEventListener('click', () => setCaughtR(s.id, !isCaughtR(s.id)));
    const hint = el('div', { class: 'shint' }), chipsEl = el('div', { class: 'chips' });
    const main = el('div', { class: 'sm', tabindex: 0 }, el('span', { class: 'snm', text: d.n }), hint, chipsEl);
    const li = el('li', { class: 'srow' }, el('span', { class: 'rn', text: String(s.rn).padStart(3, '0') }), img(s.id), main, el('div', { class: 'sbtns' }, eye, ball));
    const toggle = () => { if (sopen.has(s.id)) { sopen.delete(s.id); li.querySelector('.sdetail')?.remove(); } else { sopen.add(s.id); li.append(sinDetail(s)); } };
    main.addEventListener('click', toggle);
    main.addEventListener('keydown', e => { if (e.key === 'Enter') toggle(); });
    hint.textContent = seenHint(s);
    sinFlags(s).forEach(([t, c]) => chipsEl.append(chip(t, c)));
    srows.set(s.id, { li, eye, ball });
    frag.append(li);
  }
  ul.append(frag, el('li', { class: 'empty', id: 'sNoRes', hidden: true, text: 'Nothing matches that.' }));
  $('#sq').addEventListener('input', renderSin);
  $('#sHow').addEventListener('change', renderSin);
  $('#sqClear').addEventListener('click', () => { $('#sq').value = ''; renderSin(); $('#sq').focus(); });
  $$('[data-sshow]').forEach(b => b.addEventListener('click', () => { sshow = b.dataset.sshow; $$('[data-sshow]').forEach(x => x.setAttribute('aria-pressed', x === b)); renderSin(); }));
}
function sinMatch(s) {
  const q = norm($('#sq').value.trim());
  if (q) { if (/^\d+$/.test(q)) { if (!String(s.rn).padStart(3, '0').startsWith(q.padStart(Math.min(q.length, 3), '0')) && String(s.rn) !== q) return false; } else if (!s.key.includes(q)) return false; }
  if (sshow === 'unseen' && isSeen(s.id)) return false;
  if (sshow === 'seen' && (!isSeen(s.id) || isCaughtR(s.id))) return false;
  if (sshow === 'caught' && !isCaughtR(s.id)) return false;
  const h = $('#sHow').value;
  if (h === 'trainer' && s.how === 'catch') return false;
  if (h === 'rare' && !(s.how !== 'catch' && s.trN <= 2 && s.trAll > 0)) return false;
  if (h === 'special' && !(s.how === 'special' || s.tip)) return false;
  return true;
}
function renderSin() {
  let shown = 0;
  for (const s of SIN) {
    const { li, eye, ball } = srows.get(s.id), se = isSeen(s.id), ca = isCaughtR(s.id), ok = sinMatch(s);
    li.classList.toggle('seen', se && !ca); li.classList.toggle('caught', ca);
    eye.setAttribute('aria-pressed', se); ball.setAttribute('aria-pressed', ca);
    li.hidden = !ok; if (ok) shown++;
  }
  $('#sNoRes').hidden = shown > 0;
  const seenN = SIN.filter(s => isSeen(s.id)).length, caughtN = SIN.filter(s => isCaughtR(s.id)).length;
  $('#sSeen').textContent = seenN; $('#sCaught').textContent = caughtN;
  $('#sSeenBar').style.width = seenN / 2.1 + '%'; $('#sCaughtBar').style.width = caughtN / 2.1 + '%';
  $('#sGoal').textContent = seenN === 210 ? 'All 210 seen! After the Hall of Fame, talk to Prof. Rowan in Sandgem Town to get the National Dex.' :
    `${210 - seenN} left to see. See all 210, then talk to Prof. Rowan after the Hall of Fame to unlock the National Dex. Seeing is enough — battling a trainer's Pokémon counts.`;
}

/* ---------------- drawer ---------------- */
let drawerId = null, lastFocus = null;
function whereList(text) {
  const parts = text.split(/ · /);
  const main = parts[0].split(/; (?=[A-Z+])/);
  return el('div', { class: 'where' }, el('ul', {}, main.map(p => el('li', { text: p })), parts.slice(1).map(p => el('li', { text: p.charAt(0).toUpperCase() + p.slice(1) }))));
}
function openDrawer(id) {
  drawerId = id; lastFocus = lastFocus || document.activeElement;
  const d = BY.get(id), got = isGot(id);
  const tick = el('input', { type: 'checkbox', class: 'tick', checked: got || null, 'aria-label': 'Boxed' });
  tick.addEventListener('change', () => { setGot(id, tick.checked); openDrawer(id); });
  const fam = d.fam.length > 1 ? el('div', { class: 'dsec' }, el('h4', { text: 'Evolution family' }),
    el('div', { class: 'fam' }, d.fam.map(f => el('button', { type: 'button', class: (isGot(f) ? 'got ' : '') + (f === id ? 'me' : ''), onclick: () => openDrawer(f) },
      img(f), el('span', {}, BY.get(f).n, el('br'), el('span', { class: 'fs', text: isGot(f) ? '✓ boxed' : 'needed' })))))) : null;
  const copies = COPY.get(id);
  const note = el('textarea', { class: 'dnote', id: 'note' + id, placeholder: 'Your notes (nickname, which box, where you left it…)' });
  note.value = S.notes[id] || '';
  note.addEventListener('input', () => { if (note.value) S.notes[id] = note.value; else delete S.notes[id]; save(); });
  const isEvo = d.c === 'Evolve' || d.c === 'Trade evolution';
  let steps = d.steps;
  if (isEvo && d.pre) {
    let src = d.pre; while (BY.get(src).pre && (BY.get(src).c === 'Evolve' || BY.get(src).c === 'Trade evolution')) src = BY.get(src).pre;
    const s = BY.get(src);
    steps = [`First get ${s.n} — ${s.c === 'Wild' ? 'catch it in Platinum' : 'source: ' + s.src} (tap it in the family below).`, ...d.steps];
  }
  const body = $('#drawerBody');
  body.replaceChildren(...[
    el('button', { type: 'button', class: 'ghost dclose', text: 'Close ✕', onclick: closeDrawer }),
    el('div', { class: 'dhead' }, el('div', { class: 'big' }, el('img', { class: 'px', src: SPRITE(id), alt: d.n, width: 120, height: 120 })),
      el('div', {}, el('span', { class: 'num', text: '#' + pad(id) + ' · ' + regionOf(id) }), el('h3', { text: d.n }),
        el('div', { class: 'chips', style: 'margin-top:6px' }, chip(d.c), chip(TIERS[d.rank], 'tier' + d.rank), d.cp ? chip('catch ×' + d.cp, 'cp') : null))),
    el('label', { class: 'boxit' + (got ? ' got' : '') }, tick, got ? `Boxed ${new Date(S.boxed[id]).toLocaleDateString()}` : 'Mark as boxed'),
    SINBY.has(id) ? el('div', { class: 'dsec' }, el('h4', { text: `Sinnoh Dex #${String(SINBY.get(id).rn).padStart(3, '0')}` }),
      el('div', { class: 'row' },
        el('button', { type: 'button', class: isSeen(id) ? '' : 'ghost', text: isSeen(id) ? '👁 Seen' : '👁 Mark seen', onclick: () => setSeen(id, !isSeen(id)) }),
        el('button', { type: 'button', class: isCaughtR(id) ? '' : 'ghost', text: isCaughtR(id) ? '✓ Caught' : 'Mark caught', onclick: () => setCaughtR(id, !isCaughtR(id)) })),
      sinDetail(SINBY.get(id), true)) : null,
    el('dl', { class: 'dl' },
      el('dt', { text: 'Source game' }), el('dd', { text: d.src }),
      el('dt', { text: 'Gets to Platinum' }), el('dd', { text: d.tr }),
      el('dt', { text: 'Unlocks' }), el('dd', { text: TIER_NOTES[d.rank] }),
      d.need ? el('dt', { text: 'Needs' }) : null, d.need ? el('dd', { text: d.need }) : null),
    steps.length ? el('div', { class: 'dsec' }, el('h4', { text: 'How to get it' }), el('ol', { class: 'steps' }, steps.map(s => el('li', { text: s })))) : null,
    isEvo && !d.w.includes(' · ') ? null : el('div', { class: 'dsec' }, el('h4', { text: isEvo ? 'Also catchable' : 'Where / rates' }), whereList(isEvo ? d.w.split(' · ').slice(1).join(' · ') : d.w)),
    copies ? el('div', { class: 'dsec' }, el('h4', { text: 'Copies' }), el('p', { class: 'sub', text: `Catch or breed ${copies.length + 1}: one stays ${d.n}, the rest become ${copies.map(c => BY.get(c).n).join(', ')}. Track them on the Copies tab.` })) : null,
    fam,
    el('div', { class: 'dsec' }, el('h4', { text: 'Notes' }), note)].filter(Boolean));
  $('#scrim').hidden = false;
  const dr = $('#drawer'); dr.classList.add('open'); dr.setAttribute('aria-hidden', 'false'); dr.scrollTop = 0; dr.focus({ preventScroll: true });
}
function closeDrawer() {
  drawerId = null; $('#scrim').hidden = true;
  const dr = $('#drawer'); dr.classList.remove('open'); dr.setAttribute('aria-hidden', 'true');
  if (lastFocus && document.contains(lastFocus)) lastFocus.focus({ preventScroll: true }); lastFocus = null;
}

/* ---------------- views + refresh ---------------- */
let view = 'dex';
const RENDER = { sinnoh: renderSin, dex: renderGrid, boxes: renderBoxes, plan: renderPlan, today: renderToday, dupes: renderDupes, more: badges };
function setView(v) {
  view = v;
  $$('.view').forEach(s => s.hidden = s.id !== 'view-' + v);
  $$('[data-view]').forEach(b => b.dataset.view === v ? b.setAttribute('aria-current', 'page') : b.removeAttribute('aria-current'));
  RENDER[v]();
  try { localStorage.setItem('pld-view', v); } catch (e) {}
  if (location.hash.slice(1) !== v) history.replaceState(null, '', '#' + v);
}
function refresh() { header(); RENDER[view](); }

function init() {
  load(); buildSin(); buildGrid(); initFilters(); initBoxes(); initPlan(); initDupes(); initMore();
  $$('[data-view]').forEach(b => b.addEventListener('click', () => { setView(b.dataset.view); scrollTo({ top: 0 }); }));
  $('#scrim').addEventListener('click', closeDrawer);
  addEventListener('keydown', e => { if (e.key === 'Escape' && drawerId) closeDrawer(); });
  $('#surprise').addEventListener('click', () => {
    const need = DEX.filter(d => !isGot(d.id) && d.rank < 7);
    if (!need.length) { toast('Nothing left to catch!'); return; }
    const pick = need[Math.random() * need.length | 0]; openDrawer(pick.id); toast(`Go get ${pick.n}!`);
  });
  setInterval(() => { if (view === 'today') renderToday(); }, 60e3);
  addEventListener('storage', e => { if (e.key === KEY) { load(); refresh(); } });
  let start = location.hash.slice(1);
  if (!RENDER[start]) { try { start = localStorage.getItem('pld-view') || 'sinnoh'; } catch (e) { start = 'sinnoh'; } }
  header(); setView(RENDER[start] ? start : 'sinnoh');
}
init();
})();
