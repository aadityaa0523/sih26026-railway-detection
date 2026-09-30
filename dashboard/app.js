'use strict';

/* ---------- i18n ---------- */
// ponytail: a plain string table is plenty for two languages — no i18n library needed.
const I18N = {
  en: {
    appTitle: 'RAIL-N.E.D. Control Room',
    appSub: 'Railway Narcotics & Explosives Detection · Prototype · SIH 2026',
    feedHead: 'Live Alert Register', mapHead: 'Station Zone Map',
    kpiScans: 'Total Scans', kpiAlert: 'Alerts', kpiReview: 'Under Review', kpiClean: 'Clean', kpiDevices: 'Devices Reporting',
    statusOnline: 'Online', statusOffline: 'Offline (Demo Mode)',
    queued: 'events queued',
    sampleBanner: 'SAMPLE / DEMO DATA — no live sensors connected. Every event below is a scripted example, not a real detection.',
    tabFeed: 'Alert Feed', tabMap: 'Station Map',
    colTime: 'Time', colLocation: 'Location', colTier: 'Tier', colLabel: 'Predicted Label', colConfidence: 'Confidence', colDevice: 'Device',
    tierClean: 'Clean', tierReview: 'Review', tierAlert: 'Alert',
    footerNote: 'RAIL-N.E.D. is a presumptive field screen, not confirmatory lab analysis. All results here must be verified by FSL / IMS lab confirmation and NDPS Act 1985 Sec. 50 procedure before any legal action.',
    sample: 'SAMPLE',
    detailTitle: 'Event Detail', close: 'Close',
    sensorTrace: 'Sensor Trace', gpsLocation: 'GPS / Station Location',
    chainVerify: 'Chain Verification', chainOk: 'Chain intact', chainBad: 'Chain broken — tampering suspected',
    officerId: 'Officer ID', officerIdPlaceholder: 'e.g. RPF-1042',
    generateMemo: 'Generate Seizure Memo', copyMemo: 'Copy to Clipboard', copied: 'Copied to clipboard.',
    device: 'Device', zone: 'Zone', coords: 'Coordinates',
  },
  hi: {
    appTitle: 'RAIL-N.E.D. नियंत्रण कक्ष',
    appSub: 'रेलवे नशीले पदार्थ एवं विस्फोटक पहचान · प्रोटोटाइप · SIH 2026',
    feedHead: 'लाइव अलर्ट रजिस्टर', mapHead: 'स्टेशन क्षेत्र मानचित्र',
    kpiScans: 'कुल स्कैन', kpiAlert: 'चेतावनी', kpiReview: 'समीक्षाधीन', kpiClean: 'स्वच्छ', kpiDevices: 'रिपोर्टिंग डिवाइस',
    statusOnline: 'ऑनलाइन', statusOffline: 'ऑफ़लाइन (डेमो मोड)',
    queued: 'इवेंट कतार में',
    sampleBanner: 'नमूना / डेमो डेटा — कोई लाइव सेंसर कनेक्ट नहीं है। नीचे हर घटना एक तैयार उदाहरण है, वास्तविक पहचान नहीं।',
    tabFeed: 'अलर्ट फ़ीड', tabMap: 'स्टेशन मानचित्र',
    colTime: 'समय', colLocation: 'स्थान', colTier: 'स्तर', colLabel: 'अनुमानित लेबल', colConfidence: 'विश्वास', colDevice: 'डिवाइस',
    tierClean: 'स्वच्छ', tierReview: 'समीक्षा', tierAlert: 'चेतावनी',
    footerNote: 'RAIL-N.E.D. एक प्रारंभिक फ़ील्ड जांच है, पुष्टिकारक प्रयोगशाला विश्लेषण नहीं। किसी भी कानूनी कार्रवाई से पहले FSL / IMS प्रयोगशाला पुष्टि तथा एनडीपीएस अधिनियम 1985 धारा 50 प्रक्रिया के अनुसार सत्यापन आवश्यक है।',
    sample: 'नमूना',
    detailTitle: 'घटना विवरण', close: 'बंद करें',
    sensorTrace: 'सेंसर ट्रेस', gpsLocation: 'जीपीएस / स्टेशन स्थान',
    chainVerify: 'चेन सत्यापन', chainOk: 'चेन बरकरार', chainBad: 'चेन टूटी — छेड़छाड़ की आशंका',
    officerId: 'अधिकारी आईडी', officerIdPlaceholder: 'उदा. RPF-1042',
    generateMemo: 'ज़ब्ती ज्ञापन बनाएं', copyMemo: 'क्लिपबोर्ड पर कॉपी करें', copied: 'क्लिपबोर्ड पर कॉपी हो गया।',
    device: 'डिवाइस', zone: 'क्षेत्र', coords: 'निर्देशांक',
  },
};

const state = { lang: 'en', queued: 3, online: false };
const t = (key) => I18N[state.lang][key] || key;
const fmtDateTime = (iso) => {
  const d = new Date(iso), p = (n) => String(n).padStart(2, '0');
  const mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()];
  return `${p(d.getDate())}-${mon}-${d.getFullYear()} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
};

/* ---------- station schematic (shared by map view and event detail) ---------- */
// Fixed layout, not a real surveyed map — just enough geography to place alerts by zone.
const ZONES = {
  'Platform 1': { x: 130, y: 110, w: 300, h: 34 },
  'Platform 2': { x: 130, y: 210, w: 300, h: 34 },
  'Foot Overbridge': { x: 330, y: 40, w: 120, h: 26 },
  'Parcel Office': { x: 560, y: 70, w: 140, h: 70 },
  'Entry Gate A': { x: 40, y: 300, w: 90, h: 40 },
  'Entry Gate B': { x: 640, y: 300, w: 90, h: 40 },
};
const TIER_COLOR = { clean: 'var(--clean)', review: 'var(--review)', alert: 'var(--alert)' };

function zoneCenter(zoneName) {
  const z = ZONES[zoneName];
  return { x: z.x + z.w / 2, y: z.y + z.h / 2 };
}

function stationBaseSvgParts() {
  let s = '';
  for (const [name, z] of Object.entries(ZONES)) {
    s += `<rect x="${z.x}" y="${z.y}" width="${z.w}" height="${z.h}" rx="4" fill="var(--surface)" stroke="var(--navy)" stroke-width="1.2"/>`;
    s += `<text x="${z.x + z.w / 2}" y="${z.y + z.h / 2 + 4}" font-size="11" fill="var(--navy)" font-weight="600" text-anchor="middle">${name}</text>`;
  }
  return s;
}

function renderStationMap(alerts) {
  const holder = document.getElementById('mapSvgHolder');
  let markers = '';
  alerts.forEach((ev) => {
    const c = zoneCenter(ev.zone);
    markers += `<circle cx="${c.x}" cy="${c.y - 20}" r="7" fill="${TIER_COLOR[ev.tier]}" stroke="var(--surface)" stroke-width="2"><title>${ev.label} (${ev.zone})</title></circle>`;
  });
  holder.innerHTML = `<svg viewBox="0 0 760 380" width="100%" height="360" xmlns="http://www.w3.org/2000/svg">${stationBaseSvgParts()}${markers}</svg>`;
}

function miniStationSvg(zoneName) {
  const c = zoneCenter(zoneName);
  return `<svg viewBox="0 0 760 380" width="100%" height="220" xmlns="http://www.w3.org/2000/svg">${stationBaseSvgParts()}
    <circle cx="${c.x}" cy="${c.y - 20}" r="9" fill="var(--accent)" stroke="var(--surface)" stroke-width="2"/></svg>`;
}

/* ---------- sensor trace mini line chart (inline SVG, no charting library) ---------- */
function sensorTraceSvg(trace) {
  const w = 560, h = 140, pad = 10;
  const max = Math.max(...trace), min = Math.min(...trace);
  const span = max - min || 1;
  const pts = trace.map((v, i) => {
    const x = pad + (i / (trace.length - 1)) * (w - 2 * pad);
    const y = h - pad - ((v - min) / span) * (h - 2 * pad);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="140" xmlns="http://www.w3.org/2000/svg">
    <polyline points="${pts}" fill="none" stroke="var(--accent)" stroke-width="2"/>
  </svg>`;
}

/* ---------- hash chain (real SHA-256 via Web Crypto when available; a plain fallback
   hash otherwise, e.g. plain-http on a LAN IP where crypto.subtle is not exposed) ---------- */
async function hashOf(str) {
  if (window.crypto && window.crypto.subtle) {
    const buf = await window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
    return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
  }
  // ponytail: djb2 fallback, good enough to demo "chain breaks when tampered" without Web Crypto.
  let h = 5381;
  for (let i = 0; i < str.length; i++) h = ((h * 33) ^ str.charCodeAt(i)) >>> 0;
  return h.toString(16).padStart(8, '0');
}

function payloadOf(ev) {
  return JSON.stringify({ id: ev.id, time: ev.time, lat: ev.lat, lon: ev.lon, tier: ev.tier, label: ev.label, confidence: ev.confidence, deviceId: ev.deviceId });
}

async function buildChain(alerts) {
  let prev = '0'.repeat(64);
  for (const ev of alerts) {
    ev.prevHash = prev;
    ev.hash = await hashOf(prev + payloadOf(ev));
    prev = ev.hash;
  }
  // Demo tamper: after the legitimate chain is built, one event's displayed confidence
  // is nudged so its stored hash no longer matches — showing a broken-chain ✗ for real.
  const tampered = alerts.find((e) => e.id === 'evt-004');
  if (tampered) tampered.confidence = 91.2;
}

async function verifyChain(ev) {
  const recomputed = await hashOf(ev.prevHash + payloadOf(ev));
  return recomputed === ev.hash;
}

/* ---------- sample / demo data ---------- */
// Every field here is fabricated for the demo — see the SAMPLE/DEMO banner in the UI.
const SAMPLE_ALERTS = [
  { id: 'evt-006', time: '2026-09-12T09:41:12', lat: 28.6438, lon: 77.2201, zone: 'Platform 1', tier: 'alert', label: 'Cannabis (terpene profile match)', confidence: 88.4, deviceId: 'handheld-01', trace: [12,13,14,18,26,41,58,70,77,80,78,71,60,47,35,26,20,17,15,14] },
  { id: 'evt-005', time: '2026-09-12T09:22:05', lat: 28.6431, lon: 77.2205, zone: 'Parcel Office', tier: 'review', label: 'Unknown VOC — needs confirmation', confidence: 54.1, deviceId: 'quadruped-01', trace: [10,11,12,15,19,24,28,30,29,27,24,21,19,17,16,15,14,13,12,12] },
  { id: 'evt-004', time: '2026-09-12T08:58:47', lat: 28.6440, lon: 77.2190, zone: 'Foot Overbridge', tier: 'review', label: 'Acetic-acid marker (heroin-processing proxy)', confidence: 61.7, deviceId: 'handheld-01', trace: [11,12,13,16,22,30,37,40,39,35,30,25,21,18,16,14,13,12,11,11] },
  { id: 'evt-003', time: '2026-09-12T08:40:33', lat: 28.6425, lon: 77.2199, zone: 'Entry Gate A', tier: 'clean', label: 'No marker detected', confidence: 96.9, deviceId: 'handheld-01', trace: [9,10,9,10,11,10,9,10,11,10,9,9,10,10,9,10,11,10,9,10] },
  { id: 'evt-002', time: '2026-09-12T08:21:58', lat: 28.6444, lon: 77.2212, zone: 'Entry Gate B', tier: 'clean', label: 'No marker detected', confidence: 98.2, deviceId: 'quadruped-01', trace: [10,10,11,10,9,10,10,11,10,9,10,10,9,10,11,10,10,9,10,10] },
  { id: 'evt-001', time: '2026-09-12T08:05:14', lat: 28.6420, lon: 77.2188, zone: 'Platform 2', tier: 'alert', label: 'Methyl-benzoate marker (cocaine-processing proxy)', confidence: 82.6, deviceId: 'handheld-01', trace: [13,14,15,20,29,44,55,63,66,62,54,44,35,28,22,18,16,14,13,13] },
];

/* ---------- MQTT connection stub ---------- */
// Production would use a real MQTT.js client over a WebSocket transport
// (e.g. new Paho.MQTT.Client() or mqtt.connect('wss://broker:8083/mqtt')) subscribing to
// per-device topics like rpf/railned/<deviceId>/events. There is no broker running for
// this hackathon build, so this stub just attempts a plain WebSocket handshake and falls
// back to demo mode on any error or timeout — the architecture is real, the broker isn't yet.
function connectMqtt(brokerUrl, { onOnline, onOffline }) {
  let settled = false;
  const finish = (fn) => { if (!settled) { settled = true; fn(); } };
  try {
    const ws = new WebSocket(brokerUrl);
    const timer = setTimeout(() => { ws.close(); finish(onOffline); }, 2500);
    ws.onopen = () => { clearTimeout(timer); finish(onOnline); };
    ws.onerror = () => { clearTimeout(timer); finish(onOffline); };
  } catch (e) {
    finish(onOffline);
  }
}

/* ---------- rendering ---------- */
function applyI18n() {
  document.querySelectorAll('[data-t]').forEach((el) => { el.textContent = t(el.getAttribute('data-t')); });
  document.getElementById('connStatusText').textContent = state.online ? t('statusOnline') : t('statusOffline');
  document.getElementById('queuePill').textContent = `${state.queued} ${t('queued')}`;
  document.getElementById('queuePill').classList.toggle('has-queue', state.queued > 0);
  document.querySelector('input.officer-id')?.setAttribute('placeholder', t('officerIdPlaceholder'));
}

function renderKpis() {
  const n = (tier) => SAMPLE_ALERTS.filter((e) => e.tier === tier).length;
  const devices = new Set(SAMPLE_ALERTS.map((e) => e.deviceId)).size;
  const card = (cls, num, key) => `<div class="kpi ${cls}"><div class="n mono">${num}</div><div class="l">${t(key)}</div></div>`;
  document.getElementById('kpis').innerHTML =
    card('', SAMPLE_ALERTS.length, 'kpiScans') + card('k-alert', n('alert'), 'kpiAlert') +
    card('k-review', n('review'), 'kpiReview') + card('k-clean', n('clean'), 'kpiClean') +
    card('', devices, 'kpiDevices');
}

function tierLabel(tier) { return t('tier' + tier[0].toUpperCase() + tier.slice(1)); }

function renderFeed() {
  const body = document.getElementById('feedBody');
  body.innerHTML = SAMPLE_ALERTS.map((ev) => `
    <tr class="feed-row" data-id="${ev.id}">
      <td class="mono">${fmtDateTime(ev.time)}</td>
      <td>${ev.zone}</td>
      <td><span class="pill tier-${ev.tier}">${tierLabel(ev.tier)}</span></td>
      <td>${ev.label}<span class="sample-tag">${t('sample')}</span></td>
      <td class="mono">${ev.confidence.toFixed(1)}%</td>
      <td class="mono">${ev.deviceId}</td>
    </tr>`).join('');
  body.querySelectorAll('tr.feed-row').forEach((row) => {
    row.addEventListener('click', () => openDetail(row.getAttribute('data-id')));
  });
}

async function openDetail(id) {
  const ev = SAMPLE_ALERTS.find((e) => e.id === id);
  const chainOk = await verifyChain(ev);
  const overlay = document.getElementById('detailOverlay');
  overlay.innerHTML = `
    <div class="detail">
      <div class="detail-head">
        <h2>${t('detailTitle')} <span class="sample-tag">${t('sample')}</span></h2>
        <button class="close-btn" id="closeDetailBtn">${t('close')}</button>
      </div>
      <dl class="kv">
        <dt>${t('colTime')}</dt><dd class="mono">${fmtDateTime(ev.time)}</dd>
        <dt>${t('device')}</dt><dd class="mono">${ev.deviceId}</dd>
        <dt>${t('zone')}</dt><dd>${ev.zone}</dd>
        <dt>${t('coords')}</dt><dd class="mono">${ev.lat.toFixed(4)}, ${ev.lon.toFixed(4)}</dd>
        <dt>${t('colTier')}</dt><dd><span class="pill tier-${ev.tier}">${tierLabel(ev.tier)}</span></dd>
        <dt>${t('colLabel')}</dt><dd>${ev.label}</dd>
        <dt>${t('colConfidence')}</dt><dd class="mono">${ev.confidence.toFixed(1)}%</dd>
      </dl>

      <div>
        <h3>${t('sensorTrace')}</h3>
        ${sensorTraceSvg(ev.trace)}
      </div>

      <div>
        <h3>${t('gpsLocation')}</h3>
        ${miniStationSvg(ev.zone)}
      </div>

      <div>
        <h3>${t('chainVerify')}</h3>
        <span class="chain-badge ${chainOk ? 'ok' : 'bad'}">${chainOk ? '✓' : '✗'} ${chainOk ? t('chainOk') : t('chainBad')}</span>
      </div>

      <div>
        <h3>${t('generateMemo')}</h3>
        <div class="row" style="margin-bottom:8px;">
          <label class="mono" for="officerIdInput">${t('officerId')}</label>
          <input class="officer-id" id="officerIdInput" placeholder="${t('officerIdPlaceholder')}">
        </div>
        <div class="row" style="margin-bottom:8px;">
          <button class="btn" id="genMemoBtn">${t('generateMemo')}</button>
          <button class="btn ghost" id="copyMemoBtn">${t('copyMemo')}</button>
          <span class="copy-feedback" id="copyFeedback"></span>
        </div>
        <textarea class="memo" id="memoText" readonly></textarea>
      </div>
    </div>`;
  overlay.hidden = false;

  document.getElementById('closeDetailBtn').addEventListener('click', closeDetail);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeDetail(); }, { once: true });
  document.getElementById('genMemoBtn').addEventListener('click', () => {
    document.getElementById('memoText').value = buildMemo(ev, chainOk, document.getElementById('officerIdInput').value.trim());
  });
  document.getElementById('copyMemoBtn').addEventListener('click', async () => {
    const text = document.getElementById('memoText').value;
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
    } catch (e) {
      const ta = document.getElementById('memoText');
      ta.select(); document.execCommand('copy');
    }
    document.getElementById('copyFeedback').textContent = t('copied');
  });
}

function closeDetail() {
  document.getElementById('detailOverlay').hidden = true;
}

function buildMemo(ev, chainOk, officerId) {
  return [
    '---- SEIZURE / DETECTION MEMORANDUM (DEMO) ----',
    `Generated: ${new Date().toLocaleString()}`,
    `Event ID: ${ev.id}`,
    `Device ID: ${ev.deviceId}`,
    `Location: ${ev.zone} (${ev.lat.toFixed(4)}, ${ev.lon.toFixed(4)})`,
    `Detection Tier: ${ev.tier.toUpperCase()}`,
    `Predicted Substance Class: ${ev.label}`,
    `Confidence: ${ev.confidence.toFixed(1)}%`,
    `Chain Verification: ${chainOk ? 'VALID' : 'BROKEN — DO NOT RELY ON THIS RECORD'}`,
    '',
    'NDPS Act 1985 — Preliminary Field Report',
    `Officer ID: ${officerId || '___________'}`,
    'Officer Remarks: _______________________________________',
    'Witness Present (Y/N): ___',
    'Sample Retained for Lab Confirmation (Y/N): ___',
    '',
    'NOTE: This is a presumptive tier-1 screening result (volatile marker',
    'compound match), not confirmatory lab analysis. Must be verified per',
    'NDPS Act 1985 Sec. 50 procedure before any legal action.',
    '---- END OF DEMO MEMO — SAMPLE DATA, NOT A REAL SEIZURE ----',
  ].join('\n');
}

function switchTab(tab) {
  document.getElementById('viewFeed').hidden = tab !== 'feed';
  document.getElementById('viewMap').hidden = tab !== 'map';
  document.getElementById('tabFeedBtn').classList.toggle('active', tab === 'feed');
  document.getElementById('tabMapBtn').classList.toggle('active', tab === 'map');
  if (tab === 'map') renderStationMap(SAMPLE_ALERTS);
}

function setLang(lang) {
  state.lang = lang;
  document.getElementById('langEn').classList.toggle('active', lang === 'en');
  document.getElementById('langHi').classList.toggle('active', lang === 'hi');
  applyI18n();
  renderFeed();
  renderKpis();
}

function setConnStatus(online) {
  state.online = online;
  document.getElementById('connStatus').classList.toggle('online', online);
  document.getElementById('connStatus').classList.toggle('offline', !online);
  applyI18n();
}

/* ---------- init ---------- */
(async function init() {
  await buildChain(SAMPLE_ALERTS);
  renderFeed();
  renderKpis();
  applyI18n();

  document.getElementById('tabFeedBtn').addEventListener('click', () => switchTab('feed'));
  document.getElementById('tabMapBtn').addEventListener('click', () => switchTab('map'));
  document.getElementById('langEn').addEventListener('click', () => setLang('en'));
  document.getElementById('langHi').addEventListener('click', () => setLang('hi'));

  // No real broker for this hackathon build — this will time out and fall back to demo mode.
  connectMqtt('ws://localhost:9001/mqtt', {
    onOnline: () => setConnStatus(true),
    onOffline: () => setConnStatus(false),
  });
})();
