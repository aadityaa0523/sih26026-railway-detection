# RAIL-N.E.D. control-room dashboard (prototype)

Offline, dependency-free web app (no framework, no CDN). `index.html` is a **single self-contained bundle** (CSS + JS inlined) so it opens anywhere, including previewers that only load one file.
Open it directly, or `node server.js` and visit http://localhost:8845.

Sources live in `src/` (`index.src.html`, `css/`, `js/`). After editing them run `node build.js` to regenerate `index.html`.

**All data is fictional or simulated**: fictional stations, scripted events, simulated HEAT
curves and device signatures. Every page carries a SAMPLE / DEMO banner. No official emblem or
logo is used; this is not an official system.

## Pages
| Page | What it shows |
|---|---|
| Command Centre | KPIs, 24 h alert chart, tier donut, priority queue, route-agreement (two-route rule), station risk ranking, live feed |
| Alert Register | search + filters (tier, station, status, route), CSV export, event detail |
| Event detail | three routes (SNIFF / HEAT / SEE), sensor trace, simulated HEAT NO2-vs-temperature curve, workflow (acknowledge -> dispatch -> FSL -> confirmed / false positive), notes, chain check, memo generator |
| Stations & Zones | station schematic with event markers, robot position, 25 kV no-go zones, per-zone alert thresholds |
| Device Fleet | handhelds and quadrupeds: battery, sync, firmware, model version, heater / MQ / NO2 health, robot commands |
| Robot Patrol | simulated patrol loop, hold / resume / dock / e-stop, last-clean-scan baseline per coach or track segment |
| Evidence & Custody | hash-linked, signed (simulated) records with "verify all"; one record is deliberately tampered |
| FSL Learning Loop | lab-pending queue, confirmed vs false-positive, model versions, simulated signed update rollout |
| Reports & Analytics | hour x zone heatmap, class mix, median time to acknowledge, CSV / print |
| Admin & Audit | role permission matrix, audit log, honesty notes, reset demo data |

Also: English / Hindi (navigation, headings, tables, statuses, zones, labels), role selector
(Constable, Inspector, Control Room, FSL Liaison, Bomb Disposal) that changes allowed actions,
text-size and high-contrast controls, notification bell, live event simulation (toggle in header).

## Honest limits
- No broker or backend: nothing is real-time from devices. A real build would subscribe to
  `rpf/railned/<deviceId>/events` over MQTT-over-WebSocket.
- The classifier behind these results was trained on synthetic data; no accuracy is claimed.
- BNSS s.105 / BSA s.63 alignment is a design goal whose wording is still to be verified.
- Hindi covers the main UI; some secondary phrases (e.g. a few table headers) remain English.
