'use strict';
/* All EVENTS here are scripted demo data: scripted detections, simulated HEAT curves and signatures. Nothing is a real
   detection. The station is Tiruchirappalli Jn; platform numbers follow public sources but the train-to-platform board is mostly scripted. */

function mulberry32(seed) {
  return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

const STATIONS = [
  { id: 'TPJ', name: 'Tiruchirappalli Jn', code: 'TPJ', division: 'Tiruchirappalli Division, Southern Railway', lat: 10.8155, lon: 78.6874 },
];

// Schematic of the station. Platform NUMBERS follow the public live-status board for TPJ (1, 1A, 2-7) and the island pairing
// (2/3, 4/5, 6/7) follows the station lift/escalator plan. Positions of entrances, foot overbridge, parcel office and yard are
// PLACEHOLDERS, not surveyed. Public sources also mention 9 platforms in total; the extra ones are not drawn. viewBox 0 0 760 380.
const PLATFORMS = ['1', '1A', '2', '3', '4', '5', '6', '7'];
const ZONES = {
  'Platform 1': { x: 130, y: 36, w: 430, h: 22 }, 'Platform 1A': { x: 130, y: 62, w: 200, h: 22 },
  'Platform 2': { x: 130, y: 100, w: 430, h: 22 }, 'Platform 3': { x: 130, y: 124, w: 430, h: 22 },
  'Platform 4': { x: 130, y: 164, w: 430, h: 22 }, 'Platform 5': { x: 130, y: 188, w: 430, h: 22 },
  'Platform 6': { x: 130, y: 228, w: 430, h: 22 }, 'Platform 7': { x: 130, y: 252, w: 430, h: 22 },
  'Foot Overbridge': { x: 614, y: 30, w: 24, h: 250 }, 'Parcel Office': { x: 20, y: 36, w: 90, h: 50 },
  'Entry Gate A': { x: 20, y: 120, w: 90, h: 40 }, 'Entry Gate B': { x: 20, y: 190, w: 90, h: 40 },
  'Coach Yard': { x: 140, y: 312, w: 410, h: 44 },
};
const ISLANDS = [['Island 2/3', 98, 148], ['Island 4/5', 162, 212], ['Island 6/7', 226, 276]];
const NOGO_25KV = [{ x: 660, y: 120, w: 80, h: 230 }, { x: 20, y: 260, w: 90, h: 100 }];
const PATROL_PATH = [[130, 300], [560, 300], [560, 362], [130, 362]];     // loop around the coach yard
const DOCK = { x: 130, y: 300 };

// Train board: mostly SCRIPTED. Names/numbers are real services that call at Tiruchirappalli Jn. src 'obs' = platform seen on a
// public live-status sample (Vaigai on PF-5; real allocation changes daily); 'script' = made up. Timings are all made up.
// arrMin = minutes from "now" to arrival. Not the live timetable.
const TRAINS = [
  { no: '12605/06', name: 'Pallavan Express', route: 'Chennai Egmore ⇄ Karaikudi', platform: '1', arrMin: 8, dwell: 10, src: 'script' },
  { no: '12633/34', name: 'Kanyakumari Express', route: 'Chennai Egmore ⇄ Kanyakumari', platform: '2', arrMin: 70, dwell: 10, src: 'script' },
  { no: '12653/54', name: 'Rockfort Express', route: 'Chennai Egmore ⇄ Tiruchirappalli', platform: '3', arrMin: 12, dwell: 15, src: 'script' },
  { no: '22675/76', name: 'Cholan Express', route: 'Chennai Egmore ⇄ Tiruchirappalli', platform: '3', arrMin: 40, dwell: 20, src: 'script' },
  { no: '12631/32', name: 'Nellai Express', route: 'Chennai Egmore ⇄ Tirunelveli', platform: '4', arrMin: 6, dwell: 10, src: 'script' },
  { no: '12635/36', name: 'Vaigai Express', route: 'Chennai Egmore ⇄ Madurai', platform: '5', arrMin: -8, dwell: 12, src: 'obs' },
  { no: '12637/38', name: 'Pandian Express', route: 'Chennai Egmore ⇄ Madurai', platform: '5', arrMin: 40, dwell: 10, src: 'script' },
  { no: '12663/64', name: 'Howrah Superfast Express', route: 'Howrah ⇄ Tiruchirappalli', platform: '6', arrMin: -20, dwell: 45, src: 'script' },
];
function trainState(t, nowMs = Date.now()) {
  const arr = nowMs + t.arrMin * 60000, dep = arr + t.dwell * 60000;
  if (nowMs < arr) return { k: 'arriving', arr, dep, text: 'Arriving in ' + Math.max(1, Math.round((arr - nowMs) / 60000)) + ' min' };
  if (nowMs <= dep) return { k: 'at', arr, dep, text: 'On platform, departs in ' + Math.max(1, Math.round((dep - nowMs) / 60000)) + ' min' };
  return { k: 'left', arr, dep, text: 'Departed' };
}
const platformTrains = (n) => TRAINS.filter((t) => t.platform === String(n));
const currentTrain = (n) => { const l = platformTrains(n), now = Date.now(); return l.find((t) => trainState(t, now).k === 'at') || l.find((t) => trainState(t, now).k === 'arriving') || l[0] || null; };

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
  { id: 'handheld-01', type: 'handheld', station: 'TPJ', battery: 86, online: true, syncMin: 1, fw: 'v0.3.1', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '12 min ago' },
  { id: 'handheld-02', type: 'handheld', station: 'TPJ', battery: 54, online: true, syncMin: 3, fw: 'v0.3.1', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '40 min ago' },
  { id: 'handheld-03', type: 'handheld', station: 'TPJ', battery: 31, online: true, syncMin: 7, fw: 'v0.3.0', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warming (2 min)', no2: 'OK', bake: '1 h ago' },
  { id: 'handheld-04', type: 'handheld', station: 'TPJ', battery: 12, online: false, syncMin: 190, fw: 'v0.3.0', model: 'rf-v0.1 (synthetic)', heater: 'OFF', mq: 'idle', no2: 'baseline drift', bake: '5 h ago' },
  { id: 'handheld-05', type: 'handheld', station: 'TPJ', battery: 77, online: true, syncMin: 2, fw: 'v0.3.1', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '25 min ago' },
  { id: 'quadruped-01', type: 'quadruped', station: 'TPJ', battery: 68, online: true, syncMin: 1, fw: 'v0.2.4', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '18 min ago' },
  { id: 'quadruped-02', type: 'quadruped', station: 'TPJ', battery: 92, online: true, syncMin: 4, fw: 'v0.2.4', model: 'rf-v0.1 (synthetic)', heater: 'OK', mq: 'warmed up', no2: 'OK', bake: '50 min ago' },
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
  const station = STATIONS[0];
  const device = DEVICES[Math.floor(rng() * DEVICES.length)];
  const platforms = PLATFORMS.map((p) => 'Platform ' + p);
  const others = ['Foot Overbridge', 'Parcel Office', 'Entry Gate A', 'Entry Gate B', 'Coach Yard'];
  const zone = device.type === 'quadruped' && rng() < 0.7 ? 'Coach Yard'
    : rng() < 0.72 ? platforms[Math.floor(rng() * platforms.length)] : others[Math.floor(rng() * others.length)];
  const pm = /^Platform (\w+)$/.exec(zone), tl = pm ? platformTrains(pm[1]) : [];
  const tr = tl.length ? tl[Math.floor(rng() * tl.length)] : null;
  const coach = tr ? ['S1', 'S4', 'S7', 'B2', 'A1', 'D3', 'GS-1', 'GS-2'][Math.floor(rng() * 8)] : (zone === 'Coach Yard' ? 'Bay A' + (1 + Math.floor(rng() * 5)) : null);
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
    train: tr ? { no: tr.no, name: tr.name } : null, coach,
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
