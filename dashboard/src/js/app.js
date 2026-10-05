'use strict';
/* App shell: state, routing, live simulation, actions. Views are in views.js; data in data.js. */
const store = {
  get(k, d) { try { const v = localStorage.getItem('rn_' + k); return v === null ? d : v; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem('rn_' + k, v); } catch (e) { /* storage blocked: UI still works */ } },
};
const S = {
  events: [], audit: [], role: 'inspector', route: 'overview', sel: null, selChainOk: true, stationSel: 'RMP', live: true, queue: 3, bell: [], bellCount: 0,
  filters: { q: '', tier: '', station: '', status: '', route: '' }, thresholds: {}, patrolTick: 0, rollout: {}, online: false,
  robots: [
    { id: 'quadruped-01', station: 'RMP', mode: 'patrolling', progress: 0.0, battery: 68, x: 0, y: 0 },
    { id: 'quadruped-02', station: 'DHN', mode: 'patrolling', progress: 0.5, battery: 92, x: 0, y: 0 },
  ],
};
Object.keys(ZONES).forEach((z) => { S.thresholds[z] = z === 'Parcel Office' ? 0.85 : 0.75; });
const $ = (id) => document.getElementById(id);
const liveRng = mulberry32(777);

/* ---------- helpers ---------- */
function logAudit(act) { S.audit.unshift({ t: Date.now(), who: 'RPF-' + (S.role === 'control' ? 'CR01' : S.role === 'fsl' ? 'FSL1' : '1042'), role: T(ROLES[S.role].name), act }); }
function toast(msg, cls = '', openId = '') {
  const el = document.createElement('div'); el.className = 'toast ' + cls; el.textContent = msg; if (openId) el.onclick = () => openDetail(openId);
  $('toasts').appendChild(el); setTimeout(() => el.remove(), 5500);
}
function download(name, text, type = 'text/csv') { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); }
function toCsv(list) {
  const q = (v) => '"' + String(v).replace(/"/g, '""') + '"';
  const rows = [['id', 'time', 'station', 'zone', 'device', 'tier', 'label', 'confidence', 'routes_agreeing', 'status', 'officer', 'hash']];
  list.forEach((e) => rows.push([e.id, e.time, stName(e.station), e.zone, e.deviceId, e.tier, e.label, e.confidence, e.agree, e.status, e.officer, e.hash]));
  return rows.map((r) => r.map(q).join(',')).join('\n');
}
const openOverlay = () => !$('overlay').hidden;

/* ---------- static text / nav ---------- */
const STATIC = {
  appTitle: 'RAIL-N.E.D. Control Room', appSub: 'Railway Narcotics & Explosives Detection · Prototype · SIH 2026', liveSim: 'Live simulation', contrast: 'Contrast', crumbHome: 'Home',
  sampleBanner: 'SAMPLE / DEMO DATA — no live sensors connected. Every station, device and event here is fictional or scripted, not a real detection.',
  footerNote: 'RAIL-N.E.D. is a presumptive field screen, not confirmatory lab analysis. Every positive must be verified by FSL / IMS lab confirmation and NDPS Act 1985 Sec. 50 procedure before any legal action.',
};
function applyStatic() {
  document.querySelectorAll('[data-t]').forEach((el) => { el.textContent = T(STATIC[el.dataset.t]); });
  $('connStatusText').textContent = T(S.online ? 'Online' : 'Offline (Demo Mode)') + (S.queue ? ` · ${S.queue} ${T('events queued')}` : '');
  $('roleSel').innerHTML = Object.entries(ROLES).map(([k, r]) => `<option value="${k}" ${k === S.role ? 'selected' : ''}>${esc(T(r.name))}</option>`).join('');
  $('skipLink').textContent = RN.lang === 'hi' ? 'मुख्य सामग्री पर जाएँ' : 'Skip to main content';
  document.documentElement.lang = RN.lang;
}
function renderNav() {
  let last = '', html = '';
  for (const [k, v] of Object.entries(VIEWS)) {
    if (v.sec !== last) { html += `<div class="sec">${esc(T(v.sec))}</div>`; last = v.sec; }
    const cnt = k === 'alerts' ? S.events.filter((e) => e.tier === 'alert' && ['new', 'ack'].includes(e.status)).length : 0;
    html += `<a href="#/${k}" class="${S.route === k ? 'active' : ''}" ${S.route === k ? 'aria-current="page"' : ''}><span class="ico" aria-hidden="true">${v.ico}</span>${esc(T(v.t))}${cnt ? `<span class="cnt">${cnt}</span>` : ''}</a>`;
  }
  $('side').innerHTML = html;
}

/* ---------- rendering ---------- */
function render(keepFocus = false) {
  const v = VIEWS[S.route] || VIEWS.overview;
  let focusKey = null, caret = 0;
  const ae = document.activeElement;
  if (keepFocus && ae && ae.dataset && ae.dataset.filter) { focusKey = ae.dataset.filter; caret = ae.selectionStart; }
  $('view').innerHTML = v.f();
  $('crumbPage').textContent = T(v.t);
  $('refreshed').textContent = (RN.lang === 'hi' ? 'अंतिम ताज़ा: ' : 'Last refreshed ') + new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata' });
  renderNav();
  if (focusKey) { const el = document.querySelector(`[data-filter="${focusKey}"]`); if (el) { el.focus(); try { el.setSelectionRange(caret, caret); } catch (e) { /* select has no caret */ } } }
}
function route() {
  const r = (location.hash.replace(/^#\//, '') || 'overview');
  S.route = VIEWS[r] ? r : 'overview';
  $('side').classList.remove('open');
  render();
  window.scrollTo(0, 0);
}

/* ---------- robots ---------- */
function perimeter() { let L = 0; for (let i = 0; i < PATROL_PATH.length; i++) { const a = PATROL_PATH[i], b = PATROL_PATH[(i + 1) % PATROL_PATH.length]; L += Math.hypot(b[0] - a[0], b[1] - a[1]); } return L; }
function pointAt(prog) {
  const L = perimeter(); let d = ((prog % 1) + 1) % 1 * L;
  for (let i = 0; i < PATROL_PATH.length; i++) {
    const a = PATROL_PATH[i], b = PATROL_PATH[(i + 1) % PATROL_PATH.length], seg = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (d <= seg) return { x: a[0] + ((b[0] - a[0]) * d) / seg, y: a[1] + ((b[1] - a[1]) * d) / seg };
    d -= seg;
  }
  return { x: DOCK.x, y: DOCK.y };
}
function tickRobots() {
  S.patrolTick += 0.05;
  S.robots.forEach((r) => {
    if (r.mode === 'patrolling') { r.progress += 0.006; r.battery = Math.max(0, r.battery - 0.004); if (r.battery < 20) { r.mode = 'docking'; toast(`${r.id}: low battery, returning to dock`); logAudit(`${r.id} auto-return to dock (low battery)`); } }
    if (r.mode === 'docking') { r.progress += (Math.round(r.progress) - r.progress) * 0.08 + 0.001; if (Math.abs(r.progress - Math.round(r.progress)) < 0.01) { r.progress = Math.round(r.progress); r.mode = 'hold'; } }
    const p = r.mode === 'docking' || r.mode === 'hold' || r.mode === 'estop' || r.mode === 'patrolling' ? pointAt(r.progress) : DOCK; r.x = p.x; r.y = p.y;
  });
  if (S.route === 'patrol' && $('patrolMap')) $('patrolMap').innerHTML = patrolMapSvg();
  if (S.route === 'stations' && document.querySelector('.maphold svg')) { /* positions refresh on next render */ }
}

/* ---------- live simulation ---------- */
async function pushLiveEvent() {
  if (!S.live || document.hidden) return;
  let e = makeEvent(liveRng, Date.now());
  for (let i = 0; i < 6 && e.tier === 'clean' && liveRng() < 0.6; i++) e = makeEvent(liveRng, Date.now());
  await linkEvent(e, S.events[0] ? S.events[0].hash : '0'.repeat(64));
  S.events.unshift(e);
  S.queue = Math.max(0, S.queue + (liveRng() < 0.5 ? 1 : -1));
  if (e.tier !== 'clean') { S.bell.unshift(e.id); S.bell = S.bell.slice(0, 8); S.bellCount++; toast(`${e.tier.toUpperCase()}: ${T(e.label)} · ${stName(e.station)}`, e.tier === 'alert' ? 'alert' : '', e.id); }
  updateBell(); applyStatic();
  const ae = document.activeElement;
  if (!openOverlay() && !(ae && /INPUT|SELECT|TEXTAREA/.test(ae.tagName)) && ['overview', 'alerts', 'stations'].includes(S.route)) render();
  else renderNav();
}
function updateBell() { const c = $('bellCount'); c.hidden = !S.bellCount; c.textContent = S.bellCount; }
function renderBell() {
  $('bellPanel').innerHTML = S.bell.length ? S.bell.map((id) => { const e = S.events.find((x) => x.id === id); return e ? `<div class="bi" data-open="${e.id}">${tierPill(e.tier)} ${esc(T(e.label))}<div class="muted mono" style="font-size:.72rem">${esc(stName(e.station))} · ${fmtShort(e.time)}</div></div>` : ''; }).join('') : `<div class="bi muted">No new alerts.</div>`;
}

/* ---------- actions ---------- */
const PERM = { ack: 'ack', dispatched: 'dispatch', fsl: 'fsl', confirmed: 'confirm', fp: 'fp', closed: 'close' };
const ACT = {
  resetFilters() { S.filters = { q: '', tier: '', station: '', status: '', route: '' }; render(); },
  exportCsv() { download('rail-ned-events-DEMO.csv', toCsv(S.route === 'alerts' ? filteredEvents() : S.events)); logAudit('Exported event CSV'); },
  closeDetail() { $('overlay').hidden = true; render(); },
  wf(el) {
    const e = S.events.find((x) => x.id === S.sel), to = el.dataset.wf, need = PERM[to === 'ack' ? 'ack' : to];
    if (!e || !can(need)) { toast(T('Your role cannot perform this action.')); return; }
    e.status = to === 'ack' ? 'ack' : to; if (!e.ackAt && to === 'ack') e.ackAt = Date.now();
    logAudit(`${T(STATUS[e.status].text)}: ${e.id}`); toast(`${e.id} → ${T(STATUS[e.status].text)}`); openDetail(e.id);
  },
  addNote() { const e = S.events.find((x) => x.id === S.sel), v = $('noteIn').value.trim(); if (!e || !v) return; e.notes.push({ t: Date.now(), who: T(ROLES[S.role].name), text: v }); logAudit(`Note on ${e.id}`); openDetail(e.id); },
  memo() { const e = S.events.find((x) => x.id === S.sel); $('memoText').value = buildMemo(e, S.selChainOk); logAudit(`Memo generated for ${e.id}`); },
  async copyMemo() { const t = $('memoText').value; if (!t) return; try { await navigator.clipboard.writeText(t); } catch (e) { $('memoText').select(); document.execCommand('copy'); } $('copyFb').textContent = T('Copied.'); },
  printDetail() { window.print(); }, printPage() { window.print(); },
  rescan(el) { logAudit(`Re-scan + swab requested: ${el.dataset.seg}`); toast(`Re-scan requested: ${el.dataset.seg}`); },
  async verifyAll() {
    let bad = 0; const list = S.events.slice(0, 24);
    for (const e of list) { const ok = await verifyEvent(e); if (!ok) bad++; const c = $('chk-' + e.id); if (c) { c.textContent = ok ? '✓' : '✗ broken'; c.style.color = ok ? 'var(--clean)' : 'var(--alert)'; c.style.fontWeight = 700; } }
    $('verifySummary').textContent = `${list.length - bad}/${list.length} intact, ${bad} broken`; logAudit(`Verified ${list.length} records (${bad} broken)`);
  },
  rollout() {
    S.rollout = {}; logAudit('Started simulated signed model update rollout');
    const steps = setInterval(() => { DEVICES.forEach((d, i) => { if (d.online) S.rollout[d.id] = Math.min(100, (S.rollout[d.id] || 0) + 8 + i * 2); }); if (S.route === 'fsl' && $('rollout')) $('rollout').innerHTML = rolloutHtml(); if (DEVICES.filter((d) => d.online).every((d) => S.rollout[d.id] >= 100)) clearInterval(steps); }, 350);
  },
  async resetDemo() { S.events = await generateEvents(); S.audit = seedAudit(S.events); S.bell = []; S.bellCount = 0; updateBell(); logAudit('Demo data reset'); render(); toast('Demo data reset'); },
};
function robotCmd(id, cmd) {
  const r = S.robots.find((x) => x.id === id); if (!r || !can('robot')) { toast(T('Your role cannot perform this action.')); return; }
  r.mode = { hold: 'hold', resume: 'patrolling', dock: 'docking', estop: 'estop' }[cmd];
  logAudit(`${id}: ${cmd.toUpperCase()}`); toast(`${id}: ${T({ hold: 'Holding', resume: 'Patrolling', dock: 'Docking', estop: 'E-STOP' }[cmd])}`, cmd === 'estop' ? 'alert' : ''); render();
}

/* ---------- events ---------- */
document.addEventListener('click', (ev) => {
  const t = ev.target;
  if (!t.closest('.bell-wrap')) $('bellPanel').hidden = true;
  if (t === $('overlay')) { ACT.closeDetail(); return; }
  const open = t.closest('[data-open]'); if (open) { $('bellPanel').hidden = true; openDetail(open.dataset.open); return; }
  const st = t.closest('[data-station]'); if (st) { S.stationSel = st.dataset.station; if (S.route !== 'stations') location.hash = '#/stations'; else render(); return; }
  const rb = t.closest('[data-robot]'); if (rb) { robotCmd(rb.dataset.robot, rb.dataset.cmd); return; }
  const a = t.closest('[data-act]'); if (a && ACT[a.dataset.act]) ACT[a.dataset.act](a);
});
document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape' && openOverlay()) ACT.closeDetail();
  if (ev.key === 'Enter' && ev.target.matches && ev.target.matches('[data-open],[data-station]')) ev.target.click();
});
document.addEventListener('input', (ev) => {
  const f = ev.target.dataset && ev.target.dataset.filter; if (f && ev.target.tagName === 'INPUT') { S.filters[f] = ev.target.value; render(true); }
  const z = ev.target.dataset && ev.target.dataset.thr; if (z) { S.thresholds[z] = +ev.target.value; logAudit(`Threshold ${z} = ${(+ev.target.value).toFixed(2)}`); render(); }
});
document.addEventListener('change', (ev) => { const f = ev.target.dataset && ev.target.dataset.filter; if (f && ev.target.tagName === 'SELECT') { S.filters[f] = ev.target.value; render(true); } });
window.addEventListener('hashchange', route);

function setLang(l) { RN.lang = l; store.set('lang', l); $('langEn').classList.toggle('active', l === 'en'); $('langHi').classList.toggle('active', l === 'hi'); applyStatic(); render(); renderBell(); if (openOverlay() && S.sel) openDetail(S.sel); }
function setFont(n) { const px = { '-1': 13, '0': 14, '1': 16 }[n] || 14; document.documentElement.style.setProperty('--fs', px + 'px'); store.set('fs', n); document.querySelectorAll('[data-fs]').forEach((b) => b.classList.toggle('active', b.dataset.fs === String(n))); }
function setContrast(on) { document.documentElement.classList.toggle('hc', on); $('contrastBtn').setAttribute('aria-pressed', on); store.set('hc', on ? '1' : '0'); }

/* ---------- init ---------- */
(async function init() {
  S.events = await generateEvents(); S.audit = seedAudit(S.events);
  S.role = store.get('role', 'inspector'); if (!ROLES[S.role]) S.role = 'inspector';
  RN.lang = store.get('lang', 'en'); $('langEn').classList.toggle('active', RN.lang === 'en'); $('langHi').classList.toggle('active', RN.lang === 'hi');
  setFont(store.get('fs', '0')); setContrast(store.get('hc', '0') === '1');
  tickRobots(); applyStatic(); route(); updateBell();
  $('langEn').onclick = () => setLang('en'); $('langHi').onclick = () => setLang('hi');
  document.querySelectorAll('[data-fs]').forEach((b) => { b.onclick = () => setFont(b.dataset.fs); });
  $('contrastBtn').onclick = () => setContrast(!document.documentElement.classList.contains('hc'));
  $('roleSel').onchange = (e) => { S.role = e.target.value; store.set('role', S.role); logAudit('Switched role (demo)'); applyStatic(); render(); if (openOverlay() && S.sel) openDetail(S.sel); };
  $('liveToggle').onchange = (e) => { S.live = e.target.checked; };
  $('bellBtn').onclick = () => { renderBell(); $('bellPanel').hidden = !$('bellPanel').hidden; S.bellCount = 0; updateBell(); };
  $('menuBtn').onclick = () => $('side').classList.toggle('open');
  const clock = () => { $('clock').textContent = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', dateStyle: 'medium', timeStyle: 'medium' }) + ' IST'; }; clock(); setInterval(clock, 1000);
  setInterval(tickRobots, 400);
  setInterval(pushLiveEvent, 14000);
  // No broker in this prototype: a real MQTT-over-WebSocket client would subscribe to rpf/railned/<deviceId>/events here.
})();
