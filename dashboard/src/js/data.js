'use strict';
/* All data here is FICTIONAL / scripted demo data: fictional stations, scripted events, simulated
   HEAT curves. Nothing is a real detection and no real station is named. */

function mulberry32(seed) {
  return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

const STATIONS = [
  { id: 'RMP', name: 'Rampur Jn', division: 'Demo Division A', lat: 28.64, lon: 77.22, risk: 0.82 },
  { id: 'KVN', name: 'Kaveri Nagar', division: 'Demo Division A', lat: 12.97, lon: 77.59, risk: 0.64 },
  { id: 'SRD', name: 'Sarasvati Road', division: 'Demo Division B', lat: 23.02, lon: 72.57, risk: 0.55 },
  { id: 'DHN', name: 'Dhanpur Cantt', division: 'Demo Division B', lat: 26.85, lon: 80.95, risk: 0.71 },
  { id: 'LKM', name: 'Lakshmipur', division: 'Demo Division C', lat: 22.57, lon: 88.36, risk: 0.48 },
  { id: 'NLG', name: 'Nilgiri Halt', division: 'Demo Division C', lat: 11.41, lon: 76.69, risk: 0.22 },
];

// Station schematic (shared by the map views). viewBox 0 0 760 380.
const ZONES = {
  'Platform 1': { x: 130, y: 110, w: 300, h: 34 }, 'Platform 2': { x: 130, y: 210, w: 300, h: 34 },
  'Foot Overbridge': { x: 330, y: 40, w: 120, h: 26 }, 'Parcel Office': { x: 560, y: 70, w: 140, h: 70 },
  'Entry Gate A': { x: 40, y: 300, w: 90, h: 40 }, 'Entry Gate B': { x: 640, y: 300, w: 90, h: 40 },
  'Coach Yard': { x: 200, y: 296, w: 300, h: 48 },
};
const NOGO_25KV = [{ x: 520, y: 270, w: 100, h: 90 }, { x: 40, y: 150, w: 70, h: 120 }];
const PATROL_PATH = [[215, 276], [485, 276], [485, 262], [215, 262]];       // closed loop along Platform 2 / Coach Yard edge
const DOCK = { x: 215, y: 276 };

const ROLES = {
  constable: { name: 'RPF Constable', can: ['ack', 'note', 'memo'] },
  inspector: { name: 'Inspector / Post In-charge', can: ['ack', 'dispatch', 'fsl', 'fp', 'close', 'note', 'memo', 'robot'] },
  control: { name: 'Control Room Supervisor', can: ['ack', 'dispatch', 'fsl', 'fp', 'close', 'note', 'memo', 'robot', 'admin'] },
  fsl: { name: 'FSL Liaison', can: ['confirm', 'fp', 'note'] },
  bds: { name: 'Bomb Disposal Squad', can: ['ack', 'dispatch', 'note'] },
};

const SNIFF_LABELS = [
  'Cannabis (terpene profile match)', 'Acetic-acid marker (heroin-processing proxy)',
  'Methyl-benzoate marker (cocaine-processing proxy)', 'Unknown VOC — needs confirmation',
];
const HEAT_LABEL = 'Nitro/nitrate-class residue (stand-in signature)';
const SEE_LABEL = 'Object changed vs last clean scan';

const STATUS = {
  new: { text: 'New', cls: 'bad' }, ack: { text: 'Acknowledged', cls: 'warn' }, dispatched: { text: 'Dispatched', cls: 'info' },
  fsl: { text: 'FSL pending', cls: 'info' }, confirmed: { text: 'Lab confirmed', cls: 'ok' },
  fp: { text: 'False positive', cls: 'neutral' }, closed: { text: 'Closed', cls: 'neutral' },
};

const DEVICES = [
  { id: 'handheld-01', type: 'handheld', station: 'RMP', battery: 86, online: true, syncMin: 1, fw: 'v0.3.1', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '12 min ago' },
  { id: 'handheld-02', type: 'handheld', station: 'RMP', battery: 54, online: true, syncMin: 3, fw: 'v0.3.1', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '40 min ago' },
  { id: 'handheld-03', type: 'handheld', station: 'KVN', battery: 31, online: true, syncMin: 7, fw: 'v0.3.0', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warming (2 min)', no2: 'OK', bake: '1 h ago' },
  { id: 'handheld-04', type: 'handheld', station: 'DHN', battery: 12, online: false, syncMin: 190, fw: 'v0.3.0', model: 'rf-v0.1 (synthetic)', heater: 'OFF', mq: 'idle', no2: 'baseline drift', bake: '5 h ago' },
  { id: 'handheld-05', type: 'handheld', station: 'SRD', battery: 77, online: true, syncMin: 2, fw: 'v0.3.1', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '25 min ago' },
  { id: 'quadruped-01', type: 'quadruped', station: 'RMP', battery: 68, online: true, syncMin: 1, fw: 'v0.2.4', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '18 min ago' },
  { id: 'quadruped-02', type: 'quadruped', station: 'DHN', battery: 92, online: true, syncMin: 4, fw: 'v0.2.4', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '50 min ago' },
];

const COACH_SEGMENTS = [
  { id: 'Coach bay A1', min: 14, changed: false }, { id: 'Coach bay A2', min: 14, changed: false },
  { id: 'Coach bay A3', min: 26, changed: true }, { id: 'Coach bay A4', min: 26, changed: false },
  { id: 'Coach bay A5', min: 41, changed: false }, { id: 'Yard track 1 (under-frame)', min: 58, changed: false },
  { id: 'Yard track 2 (under-frame)', min: 58, changed: false }, { id: 'Yard track 3 (under-frame)', min: 95, changed: false },
];

const MODEL_VERSIONS = [
  { v: 'rf-v0.1', date: '2026-09-12', data: 'SYNTHETIC placeholder traces (architecture check only)', status: 'deployed' },
  { v: 'rf-v0.2', date: 'planned', data: 'Real sensor recordings of legal stand-ins + distractors (not yet collected)', status: 'planned' },
  { v: 'rf-v0.3', date: 'planned', data: 'Adds FSL-confirmed field labels via RPF pilot / MoU (not yet agreed)', status: 'planned' },
];

/* ---- two-route rule (JS port of handheld/handheld/routes.py) ---- */
function fuseRoutes(sniffTier, heatLabel, seeChanged) {
  const flags = [sniffTier === 'review' || sniffTier === 'alert', heatLabel === 'nitro_class', !!seeChanged].filter(Boolean).length;
  if (flags >= 2) return { tier: 'alert', agree: flags };
  if (flags === 1) return { tier: 'review', agree: 1 };
  if (heatLabel === 'unknown') return { tier: 'review', agree: 0 };
  return { tier: 'clean', agree: 0 };
}

/* ---- simulated signal generators ---- */
function sniffTrace(rng, peak) {
  const n = 20, pk = 7 + Math.floor(rng() * 3), out = [];
  for (let i = 0; i < n; i++) { const f = i <= pk ? i / pk : Math.max(0, 1 - (i - pk) / (n - pk)); out.push(+(1 + (peak - 1) * f + (rng() - 0.5) * 0.06).toFixed(3)); }
  return out;
}
function heatCurve(rng, kind) {
  const out = [];
  const bump = kind === 'nitro_class' ? [185 + (rng() - 0.5) * 16, 14, 0.9 + rng() * 0.6]
    : kind === 'unknown' ? [120 + rng() * 80, 18, 0.28 + rng() * 0.15] : null;
  for (let i = 0; i <= 30; i++) {
    const temp = 50 + (200 * i) / 30;
    let v = 0.05 + 0.0002 * (temp - 50) + (rng() - 0.5) * 0.04;
    if (bump) v += bump[2] * Math.exp(-((temp - bump[0]) ** 2) / (2 * bump[1] ** 2));
    out.push([temp, +v.toFixed(3)]);
  }
  return out;
}

/* ---- hash chain (SHA-256 via Web Crypto when available, djb2 fallback on plain-http LAN) ---- */
async function hashOf(str) {
  if (window.crypto && window.crypto.subtle) {
    const buf = await window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
    return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
  }
  let h = 5381; for (let i = 0; i < str.length; i++) h = ((h * 33) ^ str.charCodeAt(i)) >>> 0;
  return h.toString(16).padStart(8, '0');
}
const payloadOf = (e) => JSON.stringify({ id: e.id, time: e.time, st: e.station, z: e.zone, tier: e.tier, label: e.label, c: e.confidence, d: e.deviceId, r: e.routes });
async function linkEvent(e, prevHash) { e.prevHash = prevHash; e.hash = await hashOf(prevHash + payloadOf(e)); e.sig = 'ATECC608-SIM:' + e.hash.slice(0, 24); return e.hash; }
async function verifyEvent(e) { return (await hashOf(e.prevHash + payloadOf(e))) === e.hash; }

/* ---- event generation ---- */
let EVT_SEQ = 0;
function makeEvent(rng, time) {
  const station = STATIONS[Math.floor(rng() * STATIONS.length)];
  const dev = DEVICES.filter((d) => d.station === station.id);
  const device = (dev.length ? dev : DEVICES)[Math.floor(rng() * (dev.length || DEVICES.length))];
  const zoneNames = Object.keys(ZONES);
  const zone = device.type === 'quadruped' && rng() < 0.7 ? 'Coach Yard' : zoneNames[Math.floor(rng() * zoneNames.length)];
  const r = rng();
  let scn = r < 0.60 ? 'clean' : r < 0.78 ? 'sniff_only' : r < 0.86 ? 'unknown' : r < 0.93 ? 'heat_only' : 'two_route';
  if (device.type === 'quadruped' && scn === 'sniff_only') scn = 'see_only';
  let sniff = 'clean', heat = 'clean', see = false, label = 'No marker detected';
  if (scn === 'sniff_only') { sniff = rng() < 0.4 ? 'alert' : 'review'; label = SNIFF_LABELS[Math.floor(rng() * 3)]; }
  if (scn === 'unknown') { heat = 'unknown'; label = 'Unknown VOC — needs confirmation'; if (rng() < 0.5) sniff = 'review'; }
  if (scn === 'heat_only') { heat = 'nitro_class'; label = HEAT_LABEL; }
  if (scn === 'see_only') { see = true; label = SEE_LABEL; }
  if (scn === 'two_route') { heat = 'nitro_class'; label = HEAT_LABEL; if (device.type === 'quadruped') see = true; else sniff = 'review'; }
  const fused = fuseRoutes(sniff, heat, see);
  const conf = fused.tier === 'clean' ? 0.9 + rng() * 0.09 : fused.tier === 'alert' ? 0.82 + rng() * 0.13 : 0.5 + rng() * 0.3;
  const peak = fused.tier === 'clean' ? 1.0 + rng() * 0.06 : sniff === 'clean' ? 1.1 + rng() * 0.2 : 1.8 + rng() * 2;
  const ageH = (Date.now() - time) / 3.6e6;
  let status = 'closed';
  if (fused.tier !== 'clean') {
    const s = rng();
    if (ageH < 0.4) status = 'new';
    else if (fused.tier === 'alert') status = s < 0.2 ? 'ack' : s < 0.4 ? 'dispatched' : s < 0.7 ? 'fsl' : s < 0.85 ? 'confirmed' : 'fp';
    else status = s < 0.35 ? 'ack' : s < 0.55 ? 'closed' : s < 0.7 ? 'fsl' : s < 0.85 ? 'fp' : 'new';
  }
  const jit = () => (rng() - 0.5) * 0.004;
  return {
    id: 'EVT-' + String(++EVT_SEQ).padStart(4, '0'), time: new Date(time).toISOString(), station: station.id, zone, deviceId: device.id,
    tier: fused.tier, agree: fused.agree, label, confidence: +conf.toFixed(3), scenario: scn,
    routes: { sniff, heat, see, seeChecked: device.type === 'quadruped' },
    lat: +(station.lat + jit()).toFixed(4), lon: +(station.lon + jit()).toFixed(4),
    trace: sniffTrace(rng, peak), heatCurve: heatCurve(rng, heat === 'nitro_class' ? 'nitro_class' : heat === 'unknown' ? 'unknown' : 'clean'),
    status, officer: 'RPF-' + (1000 + Math.floor(rng() * 90)), notes: [],
    ackAt: status === 'new' || status === 'closed' ? null : time + (3 + Math.floor(rng() * 25)) * 60000,
  };
}

async function generateEvents(seed = 2026, n = 64) {
  EVT_SEQ = 0;
  const rng = mulberry32(seed), now = Date.now(), list = [];
  for (let i = 0; i < n; i++) list.push(makeEvent(rng, now - (n - i) * (24 * 60 * 60000 / n) * (0.7 + rng() * 0.6)));
  list.sort((a, b) => new Date(a.time) - new Date(b.time));
  let prev = '0'.repeat(64);
  for (const e of list) prev = await linkEvent(e, prev);
  const tamper = list.slice(-18).find((e) => e.tier === 'review') || list.slice(-18).find((e) => e.tier !== 'clean');
  if (tamper) { tamper.confidence = 0.912; tamper.tampered = true; }   // demo: breaks this record's hash on purpose
  return list.reverse();   // newest first
}

function seedAudit(events) {
  const out = [];
  events.filter((e) => e.ackAt).slice(0, 14).forEach((e) => out.push({ t: e.ackAt, who: 'RPF-' + (1000 + (e.id.length * 7) % 90), role: 'RPF Constable', act: 'Acknowledged ' + e.id }));
  return out.sort((a, b) => b.t - a.t);
}
