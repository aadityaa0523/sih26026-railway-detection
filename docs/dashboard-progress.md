# RPF Control-Room Dashboard — Progress Notes

**Status: complete and verified live in-browser by the building agent. NOT yet merged into the main working tree.**
Location right now: `C:\Users\Aadityaa\iqoo\.claude\worktrees\agent-a4bf48d97a758e4cd\dashboard\`
(a background subagent's isolated git worktree, branch `worktree-agent-a4bf48d97a758e4cd`).
Merging it into `C:\Users\Aadityaa\iqoo\dashboard\` on `master` is the next step, deliberately left for later.

## What this is

The RPF control-room + handheld-companion web dashboard from the project plan — a local,
dependency-free static web app (no framework, no build step, no CDN/internet dependency —
it has to work on a station LAN). Three files:

| File | Lines | Purpose |
|---|---|---|
| `dashboard/index.html` | 155 | Markup + all CSS (dark control-room theme, system font stack only — no Google Fonts, since it must work offline on a station LAN) |
| `dashboard/app.js` | 331 | All behavior — rendering, i18n, MQTT stub, memo generation |
| `dashboard/server.js` | 20 | Zero-dependency static file server on port 8845, same minimal pattern as this repo's existing `demo-production/serve.js` |

## Features implemented

- **Live alert feed** — table of events (time, zone, tier pill, predicted label, confidence, device ID), newest first. `id`, `zone`, `deviceId` fields distinguish handheld vs. quadruped sources.
- **Event detail view** — click a row to open an overlay with: sensor trace rendered as an inline SVG sparkline (`sensorTraceSvg()`), a mini station-zone SVG, a **real** hash-chain verify badge (SHA-256 via `crypto.subtle`, with a plain-hash fallback for non-secure-context LAN `http://` access where Web Crypto is unavailable), an officer-ID input, and a **Generate seizure memo** button (`buildMemo()`) producing a formatted, copyable text block (timestamp, zone, GPS, substance class, confidence, officer ID, NDPS-Sec.50-style fields) with working copy-to-clipboard. One sample event (`evt-004`) is deliberately tampered post-hash so the chain check visibly shows **✗**, proving verification isn't just a decorative always-✓ badge.
- **Station map tab** — SVG schematic with named zones (Platform 1/2, Parcel Office, Foot Overbridge, Entry Gates A/B) and alert markers colored by tier.
- **Connection/sync status bar** — an online/offline pill and a queued-events counter.
- **Language toggle** — full EN/हिन्दी string table (`I18N` object, `applyI18n()`), covering every visible label, not just a few — this was a real PS requirement (multilingual interface), not decorative.
- **`connectMqtt()` stub** — attempts a real WebSocket handshake, falls back to demo mode on any error/timeout. Commented with what production would actually use (`mqtt.connect('wss://broker:8083/mqtt')`, per-device topics like `rpf/senseguard/<deviceId>/events`). The architecture is real; there's no broker running yet.
- **Honesty banner** — a persistent, translated "SAMPLE / DEMO DATA — no live sensors connected" banner, plus a footer disclaimer: *"SenseGuard is a tier-1 presumptive screen (volatile marker compounds), not confirmatory lab analysis. All results here must be verified per NDPS Act 1985 Sec. 50 procedure before any legal action."* — directly carries forward this project's core honesty principle into the UI itself, not just the docs.

## Sample data

Six scripted `SAMPLE_ALERTS` events spanning all three tiers, using the project's actual
marker-compound framing rather than generic placeholders — e.g. *"Cannabis (terpene profile
match)," "Acetic-acid marker (heroin-processing proxy)," "Methyl-benzoate marker
(cocaine-processing proxy)," "Unknown VOC — needs confirmation."* Every row is visibly a demo
event (banner + no live connection), never presented as real.

## Verified by the building agent

- No JS syntax errors; checked live in-browser (not just static-parsed).
- Bug caught and fixed during verification: table rows originally used `class="row"`, which collided with an unrelated `.row{display:flex}` utility class also used elsewhere in the page, breaking the table layout. Renamed to `.feed-row`.
- Confirmed to run both via `node dashboard/server.js` → `http://localhost:8845/`, and by opening `dashboard/index.html` directly as a `file://` URL.

## Left for "continue later"

1. **Merge** `dashboard/` from the worktree above into the main tree and commit.
2. Decide whether `server.js` is actually needed for the demo (the page also opens fine as a plain `file://` URL) or only matters once real MQTT/WebSocket wiring needs a same-origin host.
3. Wire `connectMqtt()` to a real broker once the handheld/Pi `sync.py` (MQTT publisher, built by a separate subagent) has something to connect to.
4. Take one real screenshot for the PPT once merged and opened.
