'use strict';
const T = (s) => RN.T(s);
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const p2 = (n) => String(n).padStart(2, '0');
const fmtShort = (t) => { const d = new Date(t); return `${p2(d.getDate())}-${MON[d.getMonth()]} ${p2(d.getHours())}:${p2(d.getMinutes())}`; };
const fmtFull = (t) => { const d = new Date(t); return `${p2(d.getDate())}-${MON[d.getMonth()]}-${d.getFullYear()} ${p2(d.getHours())}:${p2(d.getMinutes())}:${p2(d.getSeconds())}`; };
const stName = (id) => (STATIONS.find((s) => s.id === id) || {}).name || id;
const pct = (x) => (x * 100).toFixed(1) + '%';
const tierPill = (t) => `<span class="pill tier-${t}">${esc(T(t[0].toUpperCase() + t.slice(1)))}</span>`;
const statusPill = (s) => `<span class="pill ${STATUS[s].cls}">${esc(T(STATUS[s].text))}</span>`;
const can = (a) => ROLES[S.role].can.includes(a);
const isOpen = (e) => e.tier !== 'clean' && ['new', 'ack', 'dispatched'].includes(e.status);
const routeChips = (e) => {
  const c = (on, n) => `<span class="pill ${on ? 'bad' : 'neutral'}" title="${n}">${n[0]}</span>`;
  return `<span style="display:inline-flex;gap:3px">${c(e.routes.sniff !== 'clean', 'SNIFF')}${c(e.routes.heat === 'nitro_class', 'HEAT')}${e.routes.seeChecked ? c(e.routes.see, 'SEE') : ''}</span> <span class="muted mono">${e.agree}/${e.routes.seeChecked ? 3 : 2}</span>`;
};
const kpi = (n, l, cls = '', d = '') => `<div class="kpi ${cls}"><div class="n mono">${n}</div><div class="l">${esc(T(l))}</div>${d ? `<div class="d muted">${d}</div>` : ''}</div>`;
const panel = (title, body, { flush = false, extra = '' } = {}) => `<section class="panel"><div class="panel-head">${esc(T(title))}${extra}</div><div class="panel-body ${flush ? 'flush' : ''}">${body}</div></section>`;

const locCell = (e) => `${esc(T(e.zone))}${e.train ? `<div class="muted" style="font-size:.72rem">${esc(e.train.no.split('/')[0])} ${esc(e.train.name)}${e.coach ? ' · ' + esc(e.coach) : ''}</div>` : e.coach ? `<div class="muted" style="font-size:.72rem">${esc(e.coach)}</div>` : ''}`;
function eventRows(list, { limit = 100, compact = false } = {}) {
  return list.slice(0, limit).map((e) => `<tr class="clickable" tabindex="0" data-open="${e.id}">
    <td class="mono">${fmtShort(e.time)}</td><td>${locCell(e)}</td><td>${tierPill(e.tier)}</td>
    <td>${esc(T(e.label))}<span class="tag">${T('SAMPLE')}</span></td><td>${routeChips(e)}</td>${compact ? '' : `<td class="mono">${pct(e.confidence)}</td><td class="mono">${e.deviceId}</td>`}<td>${statusPill(e.status)}</td></tr>`).join('');
}
const eventHead = (compact = false) => `<tr>${['Time', 'Platform / Train', 'Tier', 'Predicted Label', 'Routes', ...(compact ? [] : ['Confidence', 'Device']), 'Status'].map((h) => `<th>${esc(T(h))}</th>`).join('')}</tr>`;

/* ============================= 1. COMMAND CENTRE ============================= */
function viewOverview() {
  const ev = S.events, by = (t) => ev.filter((e) => e.tier === t).length;
  const hours = [...Array(24)].map((_, i) => { const d = new Date(Date.now() - (23 - i) * 3.6e6); return d.getHours(); });
  const bucket = (tier) => { const out = Array(24).fill(0); ev.forEach((e) => { const age = Math.floor((Date.now() - new Date(e.time)) / 3.6e6); if (age < 24 && e.tier === tier) out[23 - age]++; }); return out; };
  const online = DEVICES.filter((d) => d.online).length, patrolling = S.robots.filter((r) => r.mode === 'patrolling').length;
  const risk = Object.keys(ZONES).map((z) => { const l = ev.filter((e) => e.zone === z); return { z, a: l.filter((e) => e.tier === 'alert').length, r: l.filter((e) => e.tier === 'review').length }; })
    .map((x) => ({ ...x, score: x.a * 3 + x.r })).sort((a, b) => b.score - a.score);
  const maxScore = Math.max(1, risk[0].score);
  const agree = [0, 1, 2, 3].map((k) => ev.filter((e) => e.agree === k).length);
  const queue = ev.filter((e) => isOpen(e)).sort((a, b) => (b.tier === 'alert') - (a.tier === 'alert') || new Date(b.time) - new Date(a.time)).slice(0, 6);
  return `
  <div class="kpis">
    ${kpi(ev.length, 'Scans (24 h)')}${kpi(by('alert'), 'Alerts', 'k-alert')}${kpi(by('review'), 'Under Review', 'k-review')}${kpi(by('clean'), 'Clean', 'k-clean')}
    ${kpi(ev.filter(isOpen).length, 'Open Alerts', 'k-alert')}${kpi(online + '/' + DEVICES.length, 'Devices Online')}${kpi(patrolling + '/' + S.robots.length, 'Robots Patrolling')}
    ${kpi(ev.filter((e) => e.status === 'fsl').length, 'Awaiting FSL')}${kpi(S.queue, 'Sync Queue', S.queue ? 'k-review' : '')}
  </div>
  <div class="grid g-main">
    ${panel('Alerts, last 24 hours', stackedBars(hours.map((h) => p2(h)), [{ name: 'Alert', color: 'var(--alert)', data: bucket('alert') }, { name: 'Review', color: 'var(--review)', data: bucket('review') }, { name: 'Clean', color: 'var(--clean)', data: bucket('clean') }], { step: 2 }) +
      `<div class="legend"><span><i style="background:var(--alert)"></i>${T('Alert')}</span><span><i style="background:var(--review)"></i>${T('Review')}</span><span><i style="background:var(--clean)"></i>${T('Clean')}</span></div>`)}
    ${panel('Alert tiers', donut([{ label: 'Alert', value: by('alert'), color: 'var(--alert)' }, { label: 'Review', value: by('review'), color: 'var(--review)' }, { label: 'Clean', value: by('clean'), color: 'var(--clean)' }], { centre: 'scans' }) + `<div class="legend" style="justify-content:center"><span><i style="background:var(--alert)"></i>${T('Alert')} ${by('alert')}</span><span><i style="background:var(--review)"></i>${T('Review')} ${by('review')}</span><span><i style="background:var(--clean)"></i>${T('Clean')} ${by('clean')}</span></div>`)}
  </div>
  <div class="grid g-main">
    ${panel('Priority queue', `<div class="tscroll"><table class="tbl"><thead>${eventHead(true)}</thead><tbody>${eventRows(queue, { compact: true })}</tbody></table></div>${queue.length ? '' : '<p class="muted" style="padding:10px">No open items.</p>'}`, { flush: true })}
    ${panel('Route agreement (two-route rule)', hbars([{ label: '0 routes flag', value: agree[0], color: 'var(--clean)' }, { label: '1 route flags', value: agree[1], color: 'var(--review)' }, { label: '2+ routes agree', value: agree[2] + agree[3], color: 'var(--alert)' }]) +
      `<p class="note">An <b>Alert</b> needs two independent routes (SNIFF, HEAT, SEE) to agree. One route alone only raises <b>Review</b>. Swabbing the same bag twice is not two routes.</p>`)}
  </div>
  <div class="grid g-main">
    ${panel('Platform risk ranking', `<div class="tscroll"><table class="tbl"><thead><tr><th>${T('Zone')}</th><th>${T('Alert')}</th><th>${T('Review')}</th><th style="width:34%">Risk score</th></tr></thead><tbody>${risk.slice(0, 8).map((x) => `<tr class="clickable" tabindex="0" data-zonefilter="${esc(x.z)}"><td>${esc(T(x.z))}</td><td class="mono">${x.a}</td><td class="mono">${x.r}</td><td><div class="bar"><i style="width:${(x.score / maxScore) * 100}%;background:${x.a ? 'var(--alert)' : 'var(--review)'}"></i></div></td></tr>`).join('')}</tbody></table></div>`, { flush: true })}
    <div>${panel('Trains at platforms', trainBoard(true))}<div style="height:12px"></div>${panel('Live event feed', `<div id="liveFeed">${liveFeed()}</div>`)}</div>
  </div>`;
}
function liveFeed() {
  return S.events.slice(0, 8).map((e) => `<div class="stat" style="cursor:pointer" data-open="${e.id}"><span>${tierPill(e.tier)} ${esc(T(e.zone))}${e.train ? ' · ' + esc(e.train.name) : ''}</span><span class="mono muted">${fmtShort(e.time)}</span></div>`).join('');
}

/* ============================= 2. ALERT REGISTER ============================= */
function filteredEvents() {
  const f = S.filters, q = f.q.trim().toLowerCase();
  return S.events.filter((e) => (!f.tier || e.tier === f.tier) && (!f.zone || e.zone === f.zone) && (!f.status || e.status === f.status)
    && (!f.route || (f.route === 'sniff' ? e.routes.sniff !== 'clean' : f.route === 'heat' ? e.routes.heat === 'nitro_class' : e.routes.see))
    && (!q || (e.id + ' ' + e.label + ' ' + e.zone + ' ' + e.deviceId + ' ' + (e.train ? e.train.name + ' ' + e.train.no : '') + ' ' + (e.coach || '') + ' ' + e.officer).toLowerCase().includes(q)));
}
function viewAlerts() {
  const f = S.filters, opt = (v, l, cur) => `<option value="${v}" ${cur === v ? 'selected' : ''}>${esc(l)}</option>`;
  const list = filteredEvents();
  return panel('Alert Register', `
    <div class="toolbar no-print">
      <input data-filter="q" placeholder="${T('Search')}…" value="${esc(f.q)}" aria-label="${T('Search')}">
      <select data-filter="tier" aria-label="${T('Tier')}">${opt('', T('All') + ' · ' + T('Tier'), f.tier)}${['alert', 'review', 'clean'].map((t) => opt(t, T(t[0].toUpperCase() + t.slice(1)), f.tier)).join('')}</select>
      <select data-filter="zone" aria-label="${T('Zone')}">${opt('', T('All') + ' · ' + T('Zone'), f.zone)}${Object.keys(ZONES).map((z) => opt(z, T(z), f.zone)).join('')}</select>
      <select data-filter="status" aria-label="${T('Status')}">${opt('', T('All') + ' · ' + T('Status'), f.status)}${Object.keys(STATUS).map((k) => opt(k, T(STATUS[k].text), f.status)).join('')}</select>
      <select data-filter="route" aria-label="${T('Routes')}">${opt('', T('All') + ' · ' + T('Routes'), f.route)}${opt('sniff', 'SNIFF flagged', f.route)}${opt('heat', 'HEAT flagged', f.route)}${opt('see', 'SEE flagged', f.route)}</select>
      <button class="btn ghost" data-act="resetFilters">${T('Reset filters')}</button><span class="grow"></span>
      <span class="muted">${list.length} / ${S.events.length}</span>
      <button class="btn ghost" data-act="exportCsv">${T('Export CSV')}</button>
    </div>
    <div class="tscroll"><table class="tbl"><thead>${eventHead()}</thead><tbody id="alertRows">${eventRows(list)}</tbody></table></div>
    ${list.length ? '' : '<p class="muted">No events match the filters.</p>'}`, { flush: false });
}

/* ---- event detail modal ---- */
const WORKFLOW = [['new', 'New'], ['ack', 'Acknowledged'], ['dispatched', 'Dispatched'], ['fsl', 'FSL pending'], ['confirmed', 'Lab confirmed']];
function actionButtons(e) {
  const b = (act, label, cls, ok, show = true) => show ? `<button class="btn ${cls}" data-act="wf" data-wf="${act}" ${ok ? '' : 'disabled title="' + T('Your role cannot perform this action.') + '"'}>${T(label)}</button>` : '';
  const s = e.status, nc = e.tier !== 'clean';
  return [
    b('ack', 'Acknowledge', '', can('ack'), s === 'new'),
    b('dispatched', 'Dispatch team', '', can('dispatch'), s === 'ack' && nc),
    b('fsl', 'Send sample to FSL', 'warn', can('fsl'), ['ack', 'dispatched'].includes(s) && nc),
    b('confirmed', 'Mark lab confirmed', 'danger', can('confirm'), s === 'fsl'),
    b('fp', 'Mark false positive', 'ghost', can('fp'), nc && !['fp', 'closed', 'confirmed'].includes(s)),
    b('closed', 'Close (clean)', 'ghost', can('close'), s === 'ack' && e.tier === 'review'),
  ].join('') || '<span class="muted">No further actions.</span>';
}
async function openDetail(id) {
  const e = S.events.find((x) => x.id === id); if (!e) return;
  S.sel = id;
  const ok = await verifyEvent(e);
  const heatBand = [150, 230, 'expected band'];
  const route = (name, on, body) => `<div class="route ${on ? 'flag' : ''}"><h4>${T(name)} ${on ? '<span class="pill bad">flagged</span>' : '<span class="pill ok">clear</span>'}</h4><div style="font-size:.84rem;margin-top:4px">${body}</div></div>`;
  const wfIdx = WORKFLOW.findIndex((w) => w[0] === e.status);
  const tl = [[e.time, `Scan by ${e.deviceId} at ${stName(e.station)} · ${T(e.zone)}${e.train ? ' · ' + e.train.name : ''}`], [e.time, 'Routes evaluated: ' + e.agree + ' flagged → tier ' + e.tier.toUpperCase()]]
    .concat(e.ackAt ? [[e.ackAt, 'Acknowledged by control room']] : []).concat(e.notes.map((n) => [n.t, `${n.who}: ${n.text}`]));
  document.getElementById('overlay').innerHTML = `<div class="detail" role="dialog" aria-modal="true" aria-label="${T('Event Detail')}">
    <div class="dh"><div><h2>${T('Event Detail')} · <span class="mono">${e.id}</span> <span class="tag">${T('SAMPLE')}</span></h2><div style="margin-top:6px">${tierPill(e.tier)} ${statusPill(e.status)} <span class="pill neutral">${e.agree}/${e.routes.seeChecked ? 3 : 2} ${T('routes agree')}</span></div></div>
      <button class="btn ghost" data-act="closeDetail">${T('Close')}</button></div>
    <dl class="kv">
      <dt>${T('Time')}</dt><dd class="mono">${fmtFull(e.time)}</dd><dt>${T('Station')}</dt><dd>${esc(stName(e.station))}</dd><dt>${T('Zone')}</dt><dd>${esc(T(e.zone))}</dd><dt>Train</dt><dd>${e.train ? esc(e.train.no + ' ' + e.train.name) + ' <span class="tag">SCRIPTED</span>' : '—'}</dd><dt>Coach / bay</dt><dd>${esc(e.coach || '—')}</dd>
      <dt>${T('Device')}</dt><dd class="mono">${e.deviceId}</dd><dt>${T('Coordinates')}</dt><dd class="mono">${e.lat.toFixed(4)}, ${e.lon.toFixed(4)}</dd>
      <dt>${T('Predicted Label')}</dt><dd>${esc(T(e.label))}</dd><dt>${T('Confidence')}</dt><dd class="mono">${pct(e.confidence)}</dd><dt>${T('Officer')}</dt><dd class="mono">${e.officer}</dd></dl>
    <div><h3>${T('Three routes')}</h3><div class="routes">
      ${route('SNIFF', e.routes.sniff !== 'clean', 'Vapour screen (MQ array + BME688): ' + (e.routes.sniff === 'clean' ? 'no marker' : 'marker profile flagged'))}
      ${route('HEAT', e.routes.heat === 'nitro_class', 'Heated-swab NO₂ release: ' + (e.routes.heat === 'nitro_class' ? 'nitro-class signature in band' : e.routes.heat === 'unknown' ? 'weak, unfamiliar response → review' : 'no signature'))}
      ${route('SEE', !!e.routes.see, e.routes.seeChecked ? (e.routes.see ? 'Change vs last clean scan' : 'Matches last clean scan') : 'Not used (handheld)')}</div></div>
    <div class="grid g2"><div><h3>${T('Sensor trace (SNIFF)')} <span class="tag">SIMULATED</span></h3>${lineChart(e.trace.map((v, i) => [i, v]), { h: 150, xLabel: 'sample', yLabel: 'ratio vs baseline' })}</div>
      <div><h3>${T('HEAT ramp: NO2 vs temperature')} <span class="tag">SIMULATED</span></h3>${lineChart(e.heatCurve, { h: 150, xLabel: 'chamber temp (°C)', yLabel: 'NO₂ (ppm-equiv)', stamp: 'SIMULATED', band: heatBand, color: 'var(--navy)' })}</div></div>
    <div class="grid g2"><div><h3>${T('Workflow')}</h3><div class="chips" style="margin-bottom:8px">${WORKFLOW.map((w, i) => `<span class="chip ${i <= wfIdx ? 'on' : ''}">${T(w[1])}</span>`).join('')}${['fp', 'closed'].includes(e.status) ? `<span class="chip on">${T(STATUS[e.status].text)}</span>` : ''}</div><div class="actions" id="wfBtns">${actionButtons(e)}</div>
      <h3 style="margin-top:12px">${T('Timeline')}</h3><ul class="timeline">${tl.map((x) => `<li><span class="mono muted">${fmtShort(x[0])}</span> ${esc(x[1])}</li>`).join('')}</ul></div>
      <div><h3>${T('Station map')}</h3><div class="maphold">${stationMap({ events: [e], highlight: e.zone })}</div></div></div>
    <div><h3>${T('Chain verification')}</h3><span class="chain ${ok ? 'ok' : 'bad'}">${ok ? '✓ ' + T('Chain intact') : '✗ ' + T('Chain broken — tampering suspected')}</span>
      <dl class="kv" style="margin-top:8px"><dt>${T('Hash')}</dt><dd class="mono" style="word-break:break-all">${e.hash.slice(0, 40)}…</dd><dt>${T('Device signature')}</dt><dd class="mono" style="word-break:break-all">${e.sig} <span class="tag">SIMULATED</span></dd></dl></div>
    <div><h3>${T('Notes')}</h3><div class="rowflex"><input class="in" id="noteIn" style="flex:1" placeholder="${T('Add note')}…" ${can('note') ? '' : 'disabled'}><button class="btn" data-act="addNote" ${can('note') ? '' : 'disabled'}>${T('Add note')}</button></div></div>
    <div><h3>${T('Generate seizure memo')}</h3><div class="rowflex" style="margin-bottom:8px"><button class="btn" data-act="memo" ${can('memo') ? '' : 'disabled'}>${T('Generate seizure memo')}</button><button class="btn ghost" data-act="copyMemo">${T('Copy to clipboard')}</button><button class="btn ghost" data-act="printDetail">${T('Print')}</button><span id="copyFb" class="muted"></span></div><textarea class="memo" id="memoText" readonly></textarea></div></div>`;
  document.getElementById('overlay').hidden = false;
  document.getElementById('overlay').scrollTop = 0;
  S.sel = id; S.selChainOk = ok;
}
function buildMemo(e, ok) {
  return ['---- DETECTION / SEIZURE MEMORANDUM (DEMO) ----', `Generated: ${fmtFull(Date.now())}`, `Event ID: ${e.id}`, `Station / Zone: ${stName(e.station)} / ${e.zone}`, `Train / coach (scripted demo): ${e.train ? e.train.no + ' ' + e.train.name : '-'} / ${e.coach || '-'}`, `Device: ${e.deviceId}`,
    `GPS: ${e.lat.toFixed(4)}, ${e.lon.toFixed(4)}`, `Tier: ${e.tier.toUpperCase()}   Routes agreeing: ${e.agree}`, `Routes: SNIFF=${e.routes.sniff} HEAT=${e.routes.heat} SEE=${e.routes.see ? 'changed' : 'clear'}`,
    `Predicted class: ${e.label}   Confidence: ${pct(e.confidence)}`, `Record chain: ${ok ? 'VALID' : 'BROKEN - DO NOT RELY ON THIS RECORD'}`, `Device signature (SIMULATED): ${e.sig}`, '',
    'NDPS Act 1985 / BNSS preliminary field report', `Officer ID: ${e.officer}`, 'Witnesses present: ____   Video recorded (Y/N): ___', 'Sample retained for FSL: ___   FSL ref: __________', '',
    'NOTE: presumptive field screen only. Must be confirmed by FSL / IMS lab analysis', 'and NDPS Act Sec. 50 procedure before any legal action.', '---- DEMO MEMO - SAMPLE DATA, NOT A REAL SEIZURE ----'].join('\n');
}

/* ============================= 3. PLATFORMS & TRAINS ============================= */
function trainBoard(compact = false) {
  const now = Date.now();
  const rows = PLATFORMS.map((n) => {
    const t = currentTrain(n), cnt = S.events.filter((e) => e.zone === 'Platform ' + n && e.tier !== 'clean').length;
    if (!t) return `<tr class="clickable" tabindex="0" data-zonefilter="Platform ${n}"><td><b>${n}</b></td><td class="muted">No train in demo</td>${compact ? '' : '<td></td>'}<td></td><td class="mono">${cnt}</td></tr>`;
    const st = trainState(t, now);
    return `<tr class="clickable" tabindex="0" data-zonefilter="Platform ${n}"><td><b>${n}</b></td><td><b>${esc(t.name)}</b>${t.src === 'obs' ? ' <span class="tag">seen on live board</span>' : ''}${compact ? ` <span class="muted" style="font-size:.72rem">${esc(t.no.split('/')[0])}</span>` : `<div class="muted" style="font-size:.72rem">${esc(t.no)} · ${esc(t.route)}</div>`}</td>${compact ? '' : `<td class="mono">${fmtShort(st.arr).slice(-5)} → ${fmtShort(st.dep).slice(-5)}</td>`}<td><span class="pill ${st.k === 'at' ? 'ok' : st.k === 'arriving' ? 'info' : 'neutral'}">${esc(compact ? st.text.replace('Arriving in ', 'In ').replace('On platform, departs in ', 'At PF · ').replace(' min', 'm') : st.text)}</span></td><td class="mono">${cnt}</td></tr>`;
  }).join('');
  return `<div class="tscroll"><table class="tbl" style="min-width:0"><thead><tr><th>PF</th><th>Train</th>${compact ? '' : '<th>Arr → Dep</th>'}<th>Status</th><th>${T('Alerts')}</th></tr></thead><tbody>${rows}</tbody></table></div><p class="note"><b>Mostly scripted board:</b> train names and numbers are real services that call at Tiruchirappalli Jn. Only Vaigai Express on PF-5 was seen on a public live-status sample; every other platform allocation and all timings are made up. Real allocation changes daily. Not the live timetable.</p>`;
}
function viewStations() {
  const list = S.events;
  const zrows = Object.keys(ZONES).map((z) => { const l = list.filter((e) => e.zone === z); return `<tr class="clickable" tabindex="0" data-zonefilter="${esc(z)}"><td>${esc(T(z))}</td><td class="mono">${l.length}</td><td class="mono">${l.filter((e) => e.tier === 'alert').length}</td><td class="mono">${l.filter((e) => e.tier === 'review').length}</td>
    <td><input type="range" min="0.5" max="0.95" step="0.05" value="${S.thresholds[z]}" data-thr="${z}" ${can('admin') ? '' : 'disabled'} aria-label="${esc(z)} threshold" onclick="event.stopPropagation()"> <b class="mono">${S.thresholds[z].toFixed(2)}</b></td></tr>`; }).join('');
  return `<div class="grid g-main">
    ${panel('Platforms & Trains', `<div class="maphold">${stationMap({ events: list.slice(0, 40), robots: S.robots, showPath: true })}</div>
      <div class="legend"><span><i style="background:var(--clean)"></i>${T('Clean')}</span><span><i style="background:var(--review)"></i>${T('Review')}</span><span><i style="background:var(--alert)"></i>${T('Alert')}</span><span><i style="background:var(--navy)"></i>Robot</span></div>
      <p class="note">Schematic of ${esc(STATIONS[0].name)}, not a surveyed plan. <b>Platform numbers</b> (1, 1A, 2-7) follow the public live-status board and the <b>island pairs</b> (2/3, 4/5, 6/7) follow the station's lift/escalator plan. Public sources also mention 9 platforms in total; the others are not drawn. Positions of the entrances, foot overbridge, parcel office and coach yard are <b>placeholders</b>. Dots above a platform are its recent events.</p>`)}
    <div>${panel(STATIONS[0].name + ' (' + STATIONS[0].code + ')', `<dl class="kv"><dt>Division</dt><dd>${esc(STATIONS[0].division)}</dd><dt>Events (24 h)</dt><dd class="mono">${list.length}</dd><dt>Open alerts</dt><dd class="mono">${list.filter(isOpen).length}</dd>
      <dt>Devices</dt><dd>${DEVICES.map((d) => d.id).join(', ')}</dd></dl>`)}
    </div></div>
  <div style="height:12px"></div>
  ${panel('Trains at platforms', trainBoard(false))}
  <div style="height:12px"></div>
  ${panel('Zone alert thresholds', `<div class="tscroll"><table class="tbl" style="min-width:0"><thead><tr><th>${T('Zone')}</th><th>Events</th><th>${T('Alert')}</th><th>${T('Review')}</th><th>Threshold</th></tr></thead><tbody>${zrows}</tbody></table></div>
    <p class="note">Minimum confidence for a flagged result to escalate. A stricter zone (e.g. Parcel Office) can be set higher without changing code, as in <code>ZoneConfig</code>. ${can('admin') ? '' : 'Only the Control Room Supervisor can change thresholds.'}</p>`, { flush: true })}`;
}

/* ============================= 4. DEVICE FLEET ============================= */
function devCard(d) {
  const r = S.robots.find((x) => x.id === d.id), low = d.battery < 20;
  const modeText = r ? ({ patrolling: 'Patrolling', hold: 'Holding', docking: 'Docking', estop: 'E-STOP' }[r.mode]) : '';
  return `<div class="dev-card"><h4><span class="status-dot" style="background:${d.online ? 'var(--clean)' : 'var(--review)'}"></span>${d.id}${r ? ` <span class="pill ${r.mode === 'estop' ? 'bad' : r.mode === 'patrolling' ? 'ok' : 'warn'}">${T(modeText)}</span>` : ''}<span class="grow"></span>${d.online ? '<span class="pill ok">Online</span>' : '<span class="pill warn">Offline</span>'}</h4>
    <div class="muted" style="font-size:.78rem;margin-bottom:6px">${esc(stName(d.station))}</div>
    <div class="stat"><span>${T('Battery')}</span><span><div class="bar" style="width:90px;display:inline-block;vertical-align:middle"><i style="width:${r ? Math.round(r.battery) : d.battery}%;background:${low ? 'var(--alert)' : 'var(--clean)'}"></i></div> <b class="mono">${r ? Math.round(r.battery) : d.battery}%</b></span></div>
    <div class="stat"><span>${T('Last sync')}</span><span class="mono">${d.syncMin < 60 ? d.syncMin + ' min ago' : Math.round(d.syncMin / 60) + ' h ago'}</span></div>
    <div class="stat"><span>${T('Firmware')}</span><span class="mono">${d.fw}</span></div><div class="stat"><span>${T('Model version')}</span><span class="mono">${d.model}</span></div>
    <div class="stat"><span>Heater / thermal fuse</span><span>${d.heater}</span></div><div class="stat"><span>MQ array</span><span>${d.mq}</span></div><div class="stat"><span>NO₂ sensor</span><span>${d.no2}</span></div><div class="stat"><span>Last bake-out</span><span>${d.bake}</span></div>
    ${r ? `<div class="actions no-print" style="margin-top:8px"><button class="btn ghost" data-robot="${d.id}" data-cmd="hold" ${can('robot') ? '' : 'disabled'}>${T('Hold')}</button><button class="btn ghost" data-robot="${d.id}" data-cmd="resume" ${can('robot') ? '' : 'disabled'}>${T('Resume patrol')}</button><button class="btn ghost" data-robot="${d.id}" data-cmd="dock" ${can('robot') ? '' : 'disabled'}>${T('Return to dock')}</button><button class="btn danger" data-robot="${d.id}" data-cmd="estop" ${can('robot') ? '' : 'disabled'}>${T('Emergency stop')}</button></div>` : ''}</div>`;
}
function viewFleet() {
  return panel('Handheld units', `<div class="grid g3">${DEVICES.filter((d) => d.type === 'handheld').map(devCard).join('')}</div>`) + '<div style="height:12px"></div>' +
    panel('Quadruped robots', `<div class="grid g2">${DEVICES.filter((d) => d.type === 'quadruped').map(devCard).join('')}</div><p class="note">Fail-safes (design): robot sits down on signal loss, returns to dock on low battery, never enters marked 25 kV overhead-line zones, physical + remote e-stop.</p>`);
}

/* ============================= 5. ROBOT PATROL ============================= */
function viewPatrol() {
  const rows = COACH_SEGMENTS.map((s) => { const age = Math.round(s.min + S.patrolTick); return `<tr><td>${esc(s.id)}</td><td class="mono">${age < 60 ? age + ' min' : Math.round(age / 6) / 10 + ' h'} ago</td><td>${s.changed ? '<span class="pill bad">Changed</span>' : '<span class="pill ok">Matches baseline</span>'}</td><td>${s.changed ? `<button class="btn ghost no-print" data-act="rescan" data-seg="${esc(s.id)}" ${can('robot') ? '' : 'disabled'}>Request re-scan + swab</button>` : '—'}</td></tr>`; }).join('');
  return `<div class="grid g-main">
    ${panel('Patrol route', `<div class="maphold" id="patrolMap">${patrolMapSvg()}</div><div class="legend"><span><i style="background:var(--navy)"></i>Robot</span><span><i style="background:var(--alert)"></i>${T('No-go: 25 kV overhead zone')}</span></div>
      <p class="note">SEE route compares each coach / track segment with its own last clean scan, so no explosive training images are needed. Robot position is simulated.</p>`)}
    <div>${panel('Robot patrol', S.robots.map((r) => `<div style="margin-bottom:10px"><b>${r.id}</b> <span class="pill ${r.mode === 'estop' ? 'bad' : r.mode === 'patrolling' ? 'ok' : 'warn'}">${T({ patrolling: 'Patrolling', hold: 'Holding', docking: 'Docking', estop: 'E-STOP' }[r.mode])}</span>
      <div class="actions no-print" style="margin-top:6px"><button class="btn ghost" data-robot="${r.id}" data-cmd="hold" ${can('robot') ? '' : 'disabled'}>${T('Hold')}</button><button class="btn ghost" data-robot="${r.id}" data-cmd="resume" ${can('robot') ? '' : 'disabled'}>${T('Resume patrol')}</button><button class="btn ghost" data-robot="${r.id}" data-cmd="dock" ${can('robot') ? '' : 'disabled'}>${T('Return to dock')}</button><button class="btn danger" data-robot="${r.id}" data-cmd="estop" ${can('robot') ? '' : 'disabled'}>${T('Emergency stop')}</button></div></div>`).join('') + (can('robot') ? '' : '<p class="note">Robot commands need Inspector or Control Room role.</p>'))}</div></div>
  <div style="height:12px"></div>${panel('Last clean scan per segment', `<div class="tscroll"><table class="tbl"><thead><tr><th>Segment</th><th>Last clean scan</th><th>Compared with baseline</th><th></th></tr></thead><tbody id="segRows">${rows}</tbody></table></div>`, { flush: true })}`;
}
function patrolMapSvg() { return stationMap({ robots: S.robots.filter((r) => r.station === 'RMP'), showPath: true }); }

/* ============================= 6. EVIDENCE & CUSTODY ============================= */
function viewEvidence() {
  const list = S.events.slice(0, 24);
  return panel('Chain of custody', `<div class="toolbar no-print"><button class="btn" data-act="verifyAll">${T('Verify all records')}</button><span id="verifySummary" class="muted"></span></div>
    <div class="tscroll"><table class="tbl"><thead><tr><th>ID</th><th>${T('Time')}</th><th>${T('Device')}</th><th>${T('Hash')}</th><th>Prev</th><th>${T('Signature')}</th><th>Check</th></tr></thead><tbody>${list.map((e) => `<tr class="clickable" tabindex="0" data-open="${e.id}"><td class="mono">${e.id}</td><td class="mono">${fmtShort(e.time)}</td><td class="mono">${e.deviceId}</td><td class="mono">${e.hash.slice(0, 12)}…</td><td class="mono">${e.prevHash.slice(0, 8)}…</td><td class="mono">${e.sig.slice(0, 22)}…</td><td id="chk-${e.id}" class="mono muted">—</td></tr>`).join('')}</tbody></table></div>
    <p class="note"><b>How it works:</b> each alert record is signed on the device (ATECC608, ECDSA P-256 — <i>simulated here</i>) and chained to the previous record's SHA-256 hash, so editing any record breaks every later check. This is a signed, hash-linked log, <b>not blockchain</b>.</p>
    <p class="note">Legal alignment (BNSS §105 video recording of search and seizure, BSA §63 electronic-record certificate) is a design goal and its exact wording is <b>still to be verified</b> with a prosecutor / FSL before it is claimed.</p>
    <p class="note">One record in this demo was edited after signing on purpose, so you can see a broken chain.</p>`);
}

/* ============================= 7. FSL LEARNING LOOP ============================= */
function viewFsl() {
  const ev = S.events, c = (s) => ev.filter((e) => e.status === s).length, conf = c('confirmed'), fp = c('fp');
  const prec = conf + fp ? conf / (conf + fp) : null;
  const pending = ev.filter((e) => e.status === 'fsl');
  return `<div class="kpis">${kpi(pending.length, 'Awaiting FSL', 'k-review')}${kpi(conf, 'Lab confirmed', 'k-clean')}${kpi(fp, 'False positive')}${kpi(prec === null ? '—' : pct(prec), 'Share of lab-checked flags confirmed')}</div>
  <div class="grid g2">
    ${panel('Awaiting FSL', `<div class="tscroll"><table class="tbl"><thead>${eventHead(true)}</thead><tbody>${eventRows(pending, { limit: 8, compact: true })}</tbody></table></div>`, { flush: true })}
    ${panel('Model versions', `<div class="tscroll"><table class="tbl" style="min-width:0"><thead><tr><th>Version</th><th>Date</th><th>Trained on</th><th>Status</th></tr></thead><tbody>${MODEL_VERSIONS.map((m) => `<tr><td class="mono">${m.v}</td><td>${m.date}</td><td>${esc(m.data)}</td><td><span class="pill ${m.status === 'deployed' ? 'ok' : 'neutral'}">${m.status}</span></td></tr>`).join('')}</tbody></table></div>`, { flush: true })}</div>
  <div style="height:12px"></div>
  ${panel('Signed update rollout', `<div class="toolbar no-print"><button class="btn" data-act="rollout" ${can('admin') ? '' : 'disabled'}>Simulate signed update rollout</button><span class="muted">${can('admin') ? '' : 'Control Room Supervisor only'}</span></div>
    <div id="rollout">${rolloutHtml()}</div>
    <p class="note"><b>Prototype scope:</b> the loop is shown on stand-in data. Real FSL labels need an RPF pilot / MoU that has <b>not</b> been agreed. Only the substance <i>class</i> would be shared, never personal data. Devices verify a signature before installing any model update.</p>`)}`;
}
function rolloutHtml() { return DEVICES.map((d) => { const p = S.rollout[d.id] || 0; return `<div style="display:grid;grid-template-columns:120px 1fr 120px;gap:8px;align-items:center;margin:4px 0;font-size:.84rem"><span class="mono">${d.id}</span><div class="bar"><i style="width:${p}%"></i></div><span>${p >= 100 ? '<span class="pill ok">signature verified</span>' : p ? p + '%' : '<span class="muted">pending</span>'}</span></div>`; }).join(''); }

/* ============================= 8. REPORTS & ANALYTICS ============================= */
function viewReports() {
  const ev = S.events, zones = Object.keys(ZONES), hours = [...Array(24).keys()];
  const m = zones.map((z) => hours.map((h) => ev.filter((e) => e.zone === z && e.tier !== 'clean' && new Date(e.time).getHours() === h).length));
  const cls = {}; ev.filter((e) => e.tier !== 'clean').forEach((e) => { cls[e.label] = (cls[e.label] || 0) + 1; });
  const acks = ev.filter((e) => e.ackAt).map((e) => (e.ackAt - new Date(e.time)) / 60000).sort((a, b) => a - b), med = acks.length ? acks[Math.floor(acks.length / 2)] : 0;
  const flagged = ev.filter((e) => e.tier !== 'clean').length, fp = ev.filter((e) => e.status === 'fp').length;
  const byStation = zones.map((z) => ({ label: T(z), value: ev.filter((e) => e.zone === z && e.tier !== 'clean').length }));
  return `<div class="kpis">${kpi(flagged, 'Flagged scans')}${kpi(Math.round(med) + ' min', 'Median time to acknowledge')}${kpi(flagged ? pct(fp / flagged) : '—', 'False-positive share')}${kpi(pct(ev.filter((e) => e.agree >= 2).length / ev.length), 'Two-route alerts')}</div>
  <div class="toolbar no-print"><button class="btn ghost" data-act="exportCsv">${T('Export CSV')}</button><button class="btn ghost" data-act="printPage">${T('Print')}</button></div>
  <div class="grid g-main">${panel('Alerts by hour and zone', heatmap(zones.map((z) => T(z)), hours.map((h) => p2(h)), m))}${panel('Substance class mix', hbars(Object.entries(cls).map(([label, value]) => ({ label: T(label).slice(0, 22), value })).sort((a, b) => b.value - a.value)) || '<p class="muted">None</p>')}</div>
  <div style="height:12px"></div>${panel('Flagged scans by platform / zone', hbars(byStation, { color: 'var(--navy)' }))}`;
}

/* ============================= 9. ADMIN & AUDIT ============================= */
function viewAdmin() {
  const acts = ['ack', 'dispatch', 'fsl', 'confirm', 'fp', 'close', 'note', 'memo', 'robot', 'admin'];
  return `<div class="grid g2">${panel('Roles & permissions', `<div class="tscroll"><table class="tbl" style="min-width:0"><thead><tr><th>Role</th>${acts.map((a) => `<th>${a}</th>`).join('')}</tr></thead><tbody>${Object.entries(ROLES).map(([k, r]) => `<tr ${k === S.role ? 'style="background:var(--accent-soft)"' : ''}><td>${esc(T(r.name))}</td>${acts.map((a) => `<td>${r.can.includes(a) ? '✓' : ''}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p class="note">Use the role selector in the header to see how the screen changes. This is a demo; there is no real login.</p>`, { flush: true })}
    ${panel('About this prototype', `<p style="margin-top:0">Control-room view of the RAIL-N.E.D. system: a low-cost <b>handheld</b> and a <b>quadruped</b> that sniff vapour, heat a swab and look for changes, alerting only when <b>two routes agree</b>.</p>
      <ul style="margin:0;padding-left:18px;font-size:.88rem"><li>All events, HEAT curves and signatures are scripted or simulated. The train board (platform allocation, timings) is scripted, not the live timetable.</li><li>The model in use was trained on synthetic data; no accuracy is claimed.</li><li>Every positive needs FSL / IMS lab confirmation.</li><li>No official emblem or logo is used; this is not an official system.</li></ul>
      <div class="actions" style="margin-top:10px"><button class="btn ghost" data-act="resetDemo">${T('Reset demo data')}</button></div>`)}</div>
  <div style="height:12px"></div>${panel('Audit log', `<div class="tscroll"><table class="tbl"><thead><tr><th>${T('Time')}</th><th>User</th><th>Role</th><th>Action</th></tr></thead><tbody>${S.audit.slice(0, 60).map((a) => `<tr><td class="mono">${fmtFull(a.t)}</td><td class="mono">${esc(a.who)}</td><td>${esc(a.role)}</td><td>${esc(a.act)}</td></tr>`).join('')}</tbody></table></div>`, { flush: true })}`;
}

const VIEWS = {
  overview: { t: 'Command Centre', ico: '▣', sec: 'Operations', f: viewOverview },
  alerts: { t: 'Alert Register', ico: '⚑', sec: 'Operations', f: viewAlerts },
  stations: { t: 'Platforms & Trains', ico: '⌂', sec: 'Operations', f: viewStations },
  fleet: { t: 'Device Fleet', ico: '▤', sec: 'Operations', f: viewFleet },
  patrol: { t: 'Robot Patrol', ico: '◉', sec: 'Operations', f: viewPatrol },
  evidence: { t: 'Evidence & Custody', ico: '⛓', sec: 'Intelligence', f: viewEvidence },
  fsl: { t: 'FSL Learning Loop', ico: '⚗', sec: 'Intelligence', f: viewFsl },
  reports: { t: 'Reports & Analytics', ico: '▥', sec: 'Intelligence', f: viewReports },
  admin: { t: 'Admin & Audit', ico: '⚙', sec: 'Governance', f: viewAdmin },
};
