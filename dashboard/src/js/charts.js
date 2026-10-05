'use strict';
/* Dependency-free inline-SVG charts. Colours come from CSS variables so the contrast toggle applies. */
const TIER_COLOR = { clean: 'var(--clean)', review: 'var(--review)', alert: 'var(--alert)' };
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const svg = (w, h, inner, extra = '') => `<svg viewBox="0 0 ${w} ${h}" width="100%" role="img" ${extra} xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;

function stackedBars(labels, series, { h = 200, step = 1 } = {}) {
  const w = 640, padL = 30, padB = 22, padT = 8, plotH = h - padB - padT, plotW = w - padL - 6;
  const totals = labels.map((_, i) => series.reduce((a, s) => a + s.data[i], 0)), max = Math.max(1, ...totals);
  const bw = plotW / labels.length;
  let g = '';
  for (let k = 0; k <= 4; k++) { const y = padT + plotH - (k / 4) * plotH; g += `<line x1="${padL}" x2="${w - 6}" y1="${y}" y2="${y}" stroke="var(--line)" stroke-width=".6"/><text x="${padL - 4}" y="${y + 3}" font-size="9" text-anchor="end" fill="var(--ink-dim)">${Math.round((k / 4) * max)}</text>`; }
  labels.forEach((lb, i) => {
    let y = padT + plotH;
    series.forEach((s) => { const bh = (s.data[i] / max) * plotH; y -= bh; if (bh > 0) g += `<rect x="${padL + i * bw + 1}" y="${y}" width="${bw - 2}" height="${bh}" fill="${s.color}"><title>${esc(lb)} · ${esc(s.name)}: ${s.data[i]}</title></rect>`; });
    if (i % step === 0) g += `<text x="${padL + i * bw + bw / 2}" y="${h - 7}" font-size="9" text-anchor="middle" fill="var(--ink-dim)">${esc(lb)}</text>`;
  });
  return svg(w, h, g);
}

function donut(parts, { size = 170, centre = '' } = {}) {
  const total = parts.reduce((a, p) => a + p.value, 0) || 1, r = 60, c = 2 * Math.PI * r;
  let off = 0, g = '';
  parts.forEach((p) => { const len = (p.value / total) * c; g += `<circle r="${r}" cx="90" cy="90" fill="none" stroke="${p.color}" stroke-width="26" stroke-dasharray="${len} ${c - len}" stroke-dashoffset="${-off}" transform="rotate(-90 90 90)"><title>${esc(p.label)}: ${p.value}</title></circle>`; off += len; });
  g += `<text x="90" y="88" text-anchor="middle" font-size="26" font-weight="700" fill="var(--ink)">${total}</text><text x="90" y="106" text-anchor="middle" font-size="10" fill="var(--ink-dim)">${esc(centre)}</text>`;
  return `<div style="max-width:${size}px;margin:auto">${svg(180, 180, g)}</div>`;
}

function hbars(items, { color = 'var(--accent)' } = {}) {
  const max = Math.max(1, ...items.map((i) => i.value));
  return items.map((i) => `<div style="display:grid;grid-template-columns:130px 1fr 34px;gap:8px;align-items:center;font-size:.84rem;margin:5px 0"><span>${esc(i.label)}</span><div class="bar"><i style="width:${(i.value / max) * 100}%;background:${i.color || color}"></i></div><b class="mono">${i.value}</b></div>`).join('');
}

function heatmap(rowLabels, colLabels, m, { cell = 17 } = {}) {
  const padL = 112, padT = 16, w = padL + colLabels.length * cell + 4, h = padT + rowLabels.length * cell + 4;
  const max = Math.max(1, ...m.flat());
  let g = '';
  colLabels.forEach((c, j) => { if (j % 3 === 0) g += `<text x="${padL + j * cell + cell / 2}" y="11" font-size="8" text-anchor="middle" fill="var(--ink-dim)">${esc(c)}</text>`; });
  rowLabels.forEach((r, i) => {
    g += `<text x="${padL - 6}" y="${padT + i * cell + cell * 0.7}" font-size="9" text-anchor="end" fill="var(--ink)">${esc(r)}</text>`;
    colLabels.forEach((c, j) => { const v = m[i][j]; g += `<rect x="${padL + j * cell}" y="${padT + i * cell}" width="${cell - 2}" height="${cell - 2}" fill="${v ? `rgba(179,38,30,${0.15 + 0.85 * v / max})` : 'var(--surface-2)'}" stroke="var(--line)" stroke-width=".4"><title>${esc(r)} ${esc(c)}:00 — ${v}</title></rect>`; });
  });
  return svg(w, h, g);
}

function lineChart(points, { w = 460, h = 170, xLabel = '', yLabel = '', stamp = '', color = 'var(--accent)', band = null } = {}) {
  const padL = 40, padB = 28, padT = 10, padR = 8, pw = w - padL - padR, ph = h - padB - padT;
  const xs = points.map((p) => p[0]), ys = points.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(0, ...ys), y1 = Math.max(0.5, ...ys) * 1.1;
  const X = (x) => padL + ((x - x0) / (x1 - x0 || 1)) * pw, Y = (y) => padT + ph - ((y - y0) / (y1 - y0 || 1)) * ph;
  let g = '';
  for (let k = 0; k <= 4; k++) { const v = y0 + (k / 4) * (y1 - y0), y = Y(v); g += `<line x1="${padL}" x2="${w - padR}" y1="${y}" y2="${y}" stroke="var(--line)" stroke-width=".6"/><text x="${padL - 4}" y="${y + 3}" font-size="9" text-anchor="end" fill="var(--ink-dim)">${v.toFixed(1)}</text>`; }
  if (band) g += `<rect x="${X(band[0])}" y="${padT}" width="${X(band[1]) - X(band[0])}" height="${ph}" fill="var(--review-soft)" opacity=".8"/><text x="${X(band[0]) + 3}" y="${padT + 10}" font-size="8" fill="var(--review)">${esc(band[2] || '')}</text>`;
  for (let k = 0; k <= 4; k++) { const v = x0 + (k / 4) * (x1 - x0); g += `<text x="${X(v)}" y="${h - 12}" font-size="9" text-anchor="middle" fill="var(--ink-dim)">${Math.round(v)}</text>`; }
  g += `<polyline fill="none" stroke="${color}" stroke-width="2" points="${points.map((p) => `${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)}`).join(' ')}"/>`;
  g += `<text x="${padL + pw / 2}" y="${h - 1}" font-size="9" text-anchor="middle" fill="var(--ink-dim)">${esc(xLabel)}</text><text x="10" y="${padT + ph / 2}" font-size="9" fill="var(--ink-dim)" transform="rotate(-90 10 ${padT + ph / 2})" text-anchor="middle">${esc(yLabel)}</text>`;
  if (stamp) g += `<text x="${padL + pw / 2}" y="${padT + ph / 2 + 8}" font-size="22" font-weight="700" text-anchor="middle" fill="var(--alert)" opacity=".18" transform="rotate(-12 ${padL + pw / 2} ${padT + ph / 2})">${esc(stamp)}</text>`;
  return svg(w, h, g);
}

function zoneBase(highlight) {
  let s = '';
  NOGO_25KV.forEach((n) => { s += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" fill="url(#hatch)" stroke="var(--alert)" stroke-dasharray="4 3"/>`; });
  for (const [name, z] of Object.entries(ZONES)) {
    s += `<rect x="${z.x}" y="${z.y}" width="${z.w}" height="${z.h}" rx="3" fill="${name === highlight ? 'var(--accent-soft)' : 'var(--surface)'}" stroke="var(--navy)" stroke-width="1.2"/>`;
    const pm = /^Platform (\w+)$/.exec(name), tr = pm ? currentTrain(pm[1]) : null;
    if (pm) { s += `<text x="${z.x + 8}" y="${z.y + z.h / 2 + 4}" font-size="11" font-weight="700" fill="var(--navy)">${esc(RN.T(name).replace('Platform ', 'P'))}</text>${tr ? `<text x="${z.x + z.w - 8}" y="${z.y + z.h / 2 + 4}" font-size="10" fill="var(--ink-dim)" text-anchor="end">${esc(tr.no.split('/')[0] + ' ' + tr.name)}</text>` : ''}`; }
    else if (z.h > z.w * 3) s += `<text transform="translate(${z.x + z.w / 2 + 4},${z.y + z.h / 2}) rotate(-90)" font-size="10" font-weight="600" fill="var(--navy)" text-anchor="middle">${esc(RN.T(name))}</text>`;
    else s += `<text x="${z.x + z.w / 2}" y="${z.y + z.h / 2 + 4}" font-size="11" font-weight="600" fill="var(--navy)" text-anchor="middle">${esc(RN.T(name))}</text>`;
  }
  ISLANDS.forEach((i) => { s += `<text x="566" y="${(i[1] + i[2]) / 2 + 3}" font-size="8" fill="var(--ink-dim)">${esc(i[0])}</text>`; });
  return s;
}
const HATCH = `<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="var(--alert-soft)"/><line x1="0" y1="0" x2="0" y2="8" stroke="var(--alert)" stroke-width="2" opacity=".5"/></pattern></defs>`;

function stationMap({ events = [], highlight = '', robots = [], showPath = false, showNogo = true } = {}) {
  let g = HATCH + (showNogo ? '' : '') + zoneBase(highlight);
  if (showPath) g += `<polygon points="${PATROL_PATH.map((p) => p.join(',')).join(' ')}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-dasharray="6 4"/>`;
  const seen = {};
  events.forEach((e) => { const z = ZONES[e.zone]; if (!z) return; const k = (seen[e.zone] = (seen[e.zone] || 0) + 1) - 1;
    const onPf = /^Platform/.test(e.zone), cx = onPf ? z.x + 50 + (k % 16) * 14 : z.x + 14 + (k % 8) * 16, cy = onPf ? z.y + z.h / 2 : z.y - 8 - Math.floor(k / 8) * 14;
    g += `<circle cx="${cx}" cy="${cy}" r="${onPf ? 5 : 6}" fill="${TIER_COLOR[e.tier]}" stroke="#fff" stroke-width="1.5"><title>${esc(RN.T(e.label))} (${esc(RN.T(e.zone))})</title></circle>`; });
  robots.forEach((r) => { g += `<g transform="translate(${r.x},${r.y})"><rect x="-9" y="-6" width="18" height="12" rx="3" fill="${r.estop ? 'var(--alert)' : 'var(--navy)'}"/><circle cx="-5" cy="8" r="2" fill="var(--navy)"/><circle cx="5" cy="8" r="2" fill="var(--navy)"/><text y="-11" font-size="9" text-anchor="middle" font-weight="700" fill="var(--navy)">${esc(r.id)}</text></g>`; });
  g += `<g font-size="9" fill="var(--alert)"><text x="525" y="368">${esc(RN.T('No-go: 25 kV overhead zone'))}</text></g>`;
  return svg(760, 380, g, 'class="maphold"');
}
