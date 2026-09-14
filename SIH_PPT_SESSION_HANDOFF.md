# SIH26026 PPT Session Handoff

**Purpose:** This session's PPT-planning work never got saved to a file — it only exists in
chat. If you're continuing on a different Claude account (or a fresh session), paste this
whole file in first so the new session has full context without re-deriving it.

**Team:** CONGNIVISTA · **PS:** SIH26026 · Ministry of Railways ·
"Development of Mobile (Quadruped)/Handheld Device/System for Real-Time Detection of
Narcotics and Explosives across Indian Railways" · Category: Hardware

**Other docs in this repo from the same session** (all in the repo root):
- `RAIL-N.E.D._FEASIBILITY_REPORT.md` — v2, corrected. Has the physics/cost/legal basis for
  every claim on the slides.
- `RAIL-N.E.D._DEPLOYMENT_WORKFLOW.md` — **has known errors, not yet fixed**: says drugs
  produce NO₂ when heated (only nitro/nitrate explosives do), still says "SenseGuard"
  in places, says the robot can go under power lines (it must stay out of 25kV zones),
  and has invented accuracy numbers. Use for the *scenario structure* only, not for exact
  figures or claims.
- `RAIL-N.E.D._TESTING_PLAN.md` — user didn't ask for this, has some unrealistic sensor
  targets (e.g. >100 ppm NO₂). Low priority; wasn't asked for.

---

## Hard rules for this deck (from user feedback, saved to memory as `sih-ppt-style`)

1. **No icons anywhere.** User called icons "not professional."
2. **No AI-generated images or invented renders.** Only real CAD renders (from
   `quadruped/cad/renders/`), real component photos, or native PowerPoint
   shapes/tables/SmartArt. User is worried about rejection in the SIH screening round if
   evaluators spot AI imagery.
3. **Content must be unique vs ~500 competing teams.** Every slide should pass the test:
   "would a typical team write this?" — if yes, replace it. Generic "better sensor +
   dashboard" pitches get rejected by the user.
4. **SIH template constraints** (from the official template screenshots the user shared):
   - Max 6 slides including title.
   - Points/diagrams/pictures only, no paragraphs.
   - Must use the provided template without changing the idea-detail pointers already on
     each slide (i.e. don't remove the template's own bullet headings like "Detailed
     explanation of the proposed solution").
   - Submit as PDF only — no PPT/Word accepted on the portal.
5. **Tone:** clear, humanized, professional wording — not stiff corporate-speak, not overly
   casual. Judges read this cold with no presenter, so it has to be self-explanatory.

---

## The core idea: RAIL-N.E.D. | Sense Sync Secure

**One detection system, two bodies, three ways to catch a threat, matched to how each
threat actually behaves physically** — this is the differentiator vs. generic pitches.

### Why the "three routes" design exists
Early in this session we ran a physics reality-check: RDX/PETN/C4 have vapour pressure in
the **parts-per-trillion** range — no vapour sensor (MQ array, PID, even lab-grade) can
smell them from a distance. This kills the naive "better gas sensor" pitch that ~most
competing teams will submit. The fix: **three physically distinct detection routes**, not
one universal sensor.

| Route | Physical principle | Catches | Method |
|---|---|---|---|
| **SNIFF** | Substance gives off vapour | Cannabis, TATP, dynamite, tagged plastic explosives (DMNB tracer), heroin/cocaine breakdown markers | Gas sensor array (MQ-3, MQ-135, MQ-2) + BME688, heater-sweep fingerprinting, ~3–5 sec, no contact |
| **HEAT** (the core innovation) | Non-volatile residue releases decomposition gas when heated | RDX, PETN, TNT, C4, ammonium nitrate, gunpowder, pyrotechnics, opiates, meth, synthetic drugs | Swab wiped on the item (bag stays closed), retracted into a small (~5 mL) sealed chamber, heated 50→250°C, NO₂ sensor (**SGX MiCS-2714** — corrected from an earlier wrong part number, MQ-131) reads the gas released at a specific temperature. ~30 sec total. |
| **SEE** | Hidden/sealed objects give no vapour or residue signal at all | IEDs under a coach or on track | Thermal camera + video; each coach/track segment compared against its own last clean scan (change detection, not IED-photo training — avoids needing illegal training images) |

**Two-route rule:** no alert/search fires on one sensor's word alone. An alert requires two
*independent* methods to agree (e.g. Sniff + Heat, or See + Heat). Swabbing the same bag
twice does **not** count as two routes (this was a mistake in an earlier draft, corrected).

**The HEAT chamber physics (the single most defensible/differentiating claim):**
- RDX's vapour pressure is ~4×10⁻⁹ Torr (about 5 parts per trillion) at 25°C — undetectable
  by any vapour sensor, including expensive lab-grade PID sensors (~1 ppb floor, still
  >100× too insensitive).
- When heated near its decomposition point (~205°C), RDX's weakest bond (N–NO₂) breaks and
  releases NO₂ gas, which **is** detectable by a cheap sensor.
- Airport trace detectors (IMS, e.g. Smiths IONSCAN) already use this exact principle
  (thermal desorption of a swab) but then feed the released gas into an ion-mobility
  spectrometer costing several lakh rupees. RAIL-N.E.D. replaces the IMS stage with a
  cheap gas sensor + release-temperature fingerprint — much less specific, so **every
  positive still requires FSL/IMS lab confirmation** before any legal action. This is
  stated explicitly on the slides — never claim lab-grade certainty from the device alone.
- **Legal test sample:** dried nail **polish** (not polish remover — corrected mid-session;
  remover has no nitrocellulose, dried polish does). Nitrocellulose is a nitrate ester,
  same chemistry class as PETN/nitroglycerin, and is legal to test with in a lab. Never
  use real RDX, ammonium nitrate (regulated), or any NDPS/Explosives-Act-listed substance.
- **Bench test plan (gate before claiming this on stage):** heat the nail-polish stand-in
  and 7 distractors (vinegar, coffee, chilli, diesel, attar, agarbatti ash, sanitiser)
  through a 50→250°C ramp, 10 repeats each, and show the NO₂-vs-temperature plot where the
  stand-in clearly separates from every distractor. This plot is the single most convincing
  slide-4 visual — worth prioritizing over everything else in the physical build.

---

## Slide-by-slide final content (as agreed with the user)

### Slide 1 — Title
Standard SIH title slide. Team badge "CONGNIVISTA", deck title "RAIL-N.E.D. | Sense Sync
Secure", SIH 2026 logo. **Open question:** confirm actual theme — session notes have both
"Robotics and Drones" and "Blockchain & Cybersecurity" recorded at different points; verify
against the actual PS portal listing before submission.

### Slide 2 — Proposed Solution
**Opening lines (bold second line):**
> In 2025, RPF seized narcotics worth ₹300 crore in more than 2,100 cases, and in January
> 2026 an explosive blast damaged 600 m of track near Sirhind. *(Note: whether RDX was
> actually used at Sirhind is disputed — a BJP leader claimed it, but the Rupnagar Range
> DIG ruled it out. The PS text itself only says "high explosives such as RDX", so don't
> claim RDX specifically for Sirhind — say "an explosive blast".)* Yet RPF still has no
> field device that can detect either.
> **RAIL-N.E.D. closes this gap with one detection system in two forms: a handheld
> detector for every RPF post, and a four-legged robot for places that are unsafe for
> people and dogs.**

**▸ Detailed explanation of the proposed solution**
- Two devices, one system:
  - **Handheld (~₹9,000** — corrected up from an earlier ₹7,000 estimate once the Pi Zero
    2 W + ADC + speaker were priced in): entry gates, platforms, coaches, luggage points,
    parcel offices.
  - **Quadruped robot (~₹50,000** — corrected up from an earlier ₹23,000–31,000 estimate
    once real DS3225 servo prices, ~₹1,200–1,800 each not ₹250, were used): patrols
    under-frames, yards at night, tunnels. LiDAR mapping where GPS doesn't work, thermal +
    live video, watchlist face matching.
- Three routes table (Sniff/Heat/See — see table above).
- Screening flow: sniff every bag in seconds without touching it → swab flagged, random,
  and unattended items (30 sec, bag stays closed) → alert only when two independent routes
  agree.
- After a detection: sound/light/vibration/voice alert (Hindi + regional language) → GPS +
  timestamp logged automatically → sent to control-room dashboard → works offline, syncs
  when back online, AES-256 encrypted storage.
- Built for railway conditions: sealed against dust/heat/humidity, works at night on
  ballast; robot auto-sits on signal loss, returns to dock on low battery, stays out of
  marked 25kV overhead-line zones, has a physical + remote e-stop.

**▸ How it addresses the problem** (table)
| Today | With RAIL-N.E.D. |
|---|---|
| Only 416 dogs for 7,300+ stations | Affordable detector for every post; robot covers night shifts without tiring |
| RDX-class explosives give off almost no smell | HEAT reads the residue; SEE finds the hidden device itself |
| Yards/under-frames/suspicious bags put staff at risk | Robot goes in first; bomb squad stays back |
| Wrong stops and weak evidence weaken NDPS cases | Two-route rule before any search; signed court-ready record automatically |

**▸ Innovation and uniqueness**
1. **Heat, not just smell** — the HEAT chamber principle (see above), the single strongest
   unique claim.
2. **A robot that swabs** — nose pad touches a bag, retracts into the heater. Most
   competing robot designs only sniff.
3. **Every seizure trains the fleet** — FSL-confirmed results become training labels fed
   back into the model (see "learning loop" section below); real-world data instead of
   only lab stand-ins.
4. **Born legal** — every alert is a device-signed record (video + sensor trace + GPS +
   time + hash) aligned with BNSS §105 (video recording of search/seizure) and BSA §63
   (hash certificate for electronic evidence). **Unverified — see open questions below.**

**Visuals:** detection-flow diagram (Sniff/Heat/See → AI fusion → Alert, native shapes, no
icons) + real quadruped CAD render (currently only the v2 chassis exists — v3 leg rework
was not finished as of this session; use v2 render as placeholder, relabel captions in PPT).

### Slide 3 — Technical Approach
Modelled on a real SIH-finalist example the user shared (their PS: LEO satellite signals
of opportunity for GPS-denied nav) — it worked because every hardware line names a part +
model number + reason, the flowchart has real decision branches with a stated threshold
(not just a straight pipeline), there's one simple summary graphic, and a proof-of-work box
(GitHub link, video link, % complete).

**Hardware table** (handheld / robot / control room columns) — see full content already
drafted in chat; key corrected parts:
- Handheld MCU: **Raspberry Pi Zero 2 W** (user confirmed, over ESP32-S3 or Pi 4) — reuses
  the existing tested Python code in `handheld/handheld/` unchanged.
- Robot MCU: **Raspberry Pi 5** (user confirmed, over Jetson Orin Nano) — ROS 2 Humble runs
  in a Docker container since Pi 5 needs Ubuntu 24.04.
- NO₂ sensor: **SGX MiCS-2714** (corrected from MQ-131, which is an ozone sensor).
- Officer's phone: **no separate app needed** — the PS asks the *handheld itself* to have
  the multilingual/offline/GPS/alert interface; the phone just opens the same web
  dashboard (`dashboard/`) to record seizure video. User initially asked about a phone app
  design (PWA vs Flutter) — resolved as "no phone app, use what the PS actually asks for."

**Flowchart:** built as an SVG artifact in this session (three swim-lanes: handheld
screening / heated-swab analysis / robot patrol, converging on a Random Forest confidence
check at **75% threshold** — the actual value used in `handheld/handheld/classifier.py`'s
`reject_threshold`, confirmed by reading the code, not invented — then a two-route
agreement check, then alert → signed record → control room, with a dashed loop back through
FSL confirmation → model retraining). Reproduce this as native PowerPoint boxes/arrows,
color-coded by swim-lane, no icons.

**3-layer screening graphic:** Layer 1 (sniff everyone, seconds) → Layer 2 (heated swab or
robot scan for flagged/random/unattended items, ~30 sec) → Layer 3 (FSL lab confirmation,
required before any legal action).

**Fail-safes strip:** robot sits down on signal loss · returns to dock on low battery ·
never enters marked 25kV zones · e-stop on robot and operator screen.

**Proof-of-work box — BLOCKED, see open questions:**
- GitHub link: repo `aadityaa0523/sih26026-railway-detection` exists but is **PRIVATE** —
  judges would get a 404. Needs to be made public (user hasn't confirmed yet) AND pushed
  (last push was 12 Sep; chassis v3, handheld code, ROS2 package are all newer and unpushed).
- Demo video: not yet recorded, no date set.
- Prototype %: don't invent a number. User's own answer this session was "we will build it
  in a few days, leave that safe [i.e. as a placeholder] for now" — so slide 3's images row
  should say "Prototype under assembly" rather than a fabricated percentage, until real
  photos exist.

**Images row:** (1) robot CAD render — real, from `quadruped/cad/renders/`; (2) dashboard
screenshot — real once merged (dashboard currently only exists in an agent worktree at
`.claude/worktrees/agent-a4bf48d97a758e4cd/dashboard/`, not yet merged to `master`/main
tree — offered to merge it this session, user hadn't responded yet); (3) prototype photo —
placeholder until hardware build is done.

### Slide 4 — Feasibility and Viability
Not fully drafted as final slide bullets yet in this session — the **content basis** for it
is the full `RAIL-N.E.D._FEASIBILITY_REPORT.md` (v2, corrected), which has: HEAT chamber
signal-strength calculation (µg RDX → ~ppm NO₂ in a 5 mL chamber), bench-test gate criteria,
swab-mechanism risk table, FSL learning-loop governance (reports are **confidential**, not
public — corrected — shared only via an RPF MoU, substance class only, no personal data),
BNSS/BSA evidence-chain implementation (ATECC608 signing chip, ECDSA P-256 — explicitly
**not** blockchain, say so directly if a judge asks, since IONSCAN/blockchain buzzwords are
red flags with SIH judges), full cost breakdown (~₹6,870 handheld / ~₹49,450 robot,
itemized), and a phased timeline with go/no-go gates. **Next step when resuming:**
compress that report into slide-4 bullet points using the same "table + short bullets, no
paragraphs" format as slides 2–3.

### Slide 5 — Impact and Benefits (drafted, web-researched, sources verified)
**Top strip (4 numbers):** 2.3 crore passengers/day · 416 dogs for 7,300+ stations · ₹300
crore narcotics seized by RPF in 2025 · 2 explosive incidents on Punjab rail tracks in 2026
(Sirhind, Shambhu/Patiala).

**Potential impact on target audience** (table): RPF constables/inspectors, control
rooms/supervisors, bomb disposal squads, passengers, NCB/GRP/courts — full table already
drafted in chat.

**Benefits — Social / Economic / Environmental / Legal and scale** (full bullet content
already drafted in chat, with real cited sources — see Research/Sources section below).

Key researched facts (fully sourced, see bottom of this file):
- India: 3.1 crore cannabis users, 2.26 crore opioid users (AIIMS 2019 survey).
- Nasha Mukt Bharat Abhiyaan reached 29.68 crore citizens.
- NCB 2025: ₹1,980 crore seized, 66.8% conviction rate (up from 60.8% in 2024).
- RPF Operation Narcos, full year 2024: ₹227.5 crore seized, 1,489 arrests (this is a more
  complete/citable figure than the earlier session's partial Secunderabad-only numbers).
- Handheld commercial ETD: ₹22–31 lakh per unit (IndiaMART listing + a 2022 Kolkata Police
  tender). RAIL-N.E.D. handheld (~₹9k) buys 250+ units for the price of one imported ETD.
- IMS trace detectors commonly use a **Ni-63 radioactive source**, requiring safety
  licensing — RAIL-N.E.D.'s HEAT approach uses no radioactive source and no reagents.
- Startups for Railways policy: seed fund up to ₹1.5 crore, 50:50 matching, innovator
  retains IP (railways get a government-purpose license only).
- 1,337 stations under Amrit Bharat Station Scheme redevelopment — a real rollout path.
- Indian Railways target: net-zero carbon by 2030 — ties into "no chemical reagents,
  reusable swabs, low-power rechargeable devices" framing.
- Boston Dynamics Spot: $74,500 *2020 launch price*, real 2026 configured units run
  $150k–375k with no public pricing — cite the $74,500 figure carefully, note it's dated,
  don't overstate the cost gap using a stale number without the caveat.

### Slide 6 — Research and References
Compile the full sourced link list already gathered this session (NCB, AIIMS, PIB, Tribune,
ETV Bharat, IndiaMART, ScienceDirect/IMS, IEEE Spectrum, Business Standard) — see bottom of
this file for the complete list with URLs.

---

## Open questions / blockers for the next session to resolve

1. **GitHub repo visibility.** `aadityaa0523/sih26026-railway-detection` is private, last
   pushed 12 Sep 2026. Slide 3's proof-of-work box wants a working public link. Need user's
   explicit yes before making it public (it's a one-way, outward-facing action) and before
   pushing the newer unpushed work (chassis v3, handheld code, ROS2 package).
2. **Dashboard merge.** Built and verified in an agent worktree
   (`.claude/worktrees/agent-a4bf48d97a758e4cd/dashboard/`), never merged into the main
   tree. Needed to take a real screenshot for slide 3. Offered to merge this session, no
   response yet.
3. **BNSS §105 / BSA §63 exact wording.** Used on slide 2 and in the feasibility report as
   the legal basis for the evidence-chain claim. Never independently verified against the
   actual statute text or confirmed with an FSL/prosecutor — flagged repeatedly as a
   pre-submission verification task, not yet done.
4. **Physical build status.** As of this session, nothing is physically assembled yet
   (user's own words: "we will build it in a few days"). All CAD/renders/code are real;
   hardware bench tests (the NO₂-vs-distractors plot, the swab-mechanism cycle test) have
   NOT been run yet. Don't claim results that don't exist yet on slide 4.
5. **Quadruped v3 rework.** From an earlier phase of this overall project (before the PPT
   planning started): the v2 leg design was mechanics-checked and found unable to walk;
   a v3 (SpotMicro-scale) redesign was in progress via parallel Sonnet agents, interrupted
   by a usage-limit rate reset, never resumed after that. The chassis v3 is verified good
   on `master`; the leg v3 rework was never restarted. This affects which robot render is
   real/usable for slide 2/3 — currently only the outdated v2 render exists.
6. **Deck's actual theme field** — "Robotics and Drones" vs "Blockchain & Cybersecurity",
   recorded inconsistently across earlier session notes. Verify against the SIH portal.

---

## Style memory saved this session

File: `champ-leg-joints.md` (memory, from before this session) — CHAMP needs 3 actuated
joints/leg including hip ab/ad; leg CAD as of the last check couldn't walk; run
`quadruped/cad/check_mechanics.py` for any future leg-geometry change, not just a static
fit check.

File: `sih-ppt-style.md` (memory, written this session) — no icons, no AI-generated
images, content must be unique vs ~500 competing teams, evaluators judge by reading only
(no live presentation at the screening stage).

---

## Full source list gathered this session (for slide 6)

- [Business Today — 23 million passengers/day](https://www.businesstoday.in/latest/trends/photo/did-you-know-indian-railways-moves-23-million-passengers-daily-nearly-australias-entire-population-542039-2026-07-09)
- [DD News — 720+ crore passengers/year](https://www.newsonair.gov.in/indian-railways-provides-affordable-travel-to-over-720-crore-passengers-ashwini-vaishnaw)
- [ETV Bharat — ISS at 199 stations, ₹341 Cr, 416 dogs, 129 bomb-detection devices](https://www.etvbharat.com/en/!bharat/railways-to-install-iss-at-199-stations-ashwini-vaishnaw-enn24080805434)
- [Tribune — Sirhind blast, 24 Jan 2026 (RDX disputed by DIG)](https://www.tribuneindia.com/news/punjab/blast-on-railway-track-near-punjabs-sirhind-damages-600-metre-stretch-goods-train-engine-derails/)
- [IBTimes — BJP claims RDX at Sirhind (disputed claim, not confirmed)](https://www.ibtimes.co.in/republic-day-scare-punjab-bjp-claims-rdx-used-blast-near-railway-station-896721)
- [Tribune — Shambhu/Patiala detonation attempt, Apr 2026](https://www.tribuneindia.com/news/punjab/railway-track-blast-near-patiala-accused-died-in-detonation-attempt-says-police/)
- [DD News — NCB 2025: ₹1,980 Cr seized, 66.8% conviction rate](https://www.newsonair.gov.in/ncb-seizes-over-1-33-lakh-kg-narcotics-worth-%E2%82%B91980-crore-in-2025/)
- [Dinalipi — Odisha GRP: 3,352 kg ganja seized in 2025](https://www.dinalipi.com/odisha-grps-narcotics-crackdown-over-3300-kg-ganja-seized-299-arrested-in-2025/)
- [Kgp News — RPF Operation Narcos, Apr–Jul 2024: ₹21+ Cr, 522 arrests](https://www.kgpnews.in/2024/08/railway-protection-force-seizes-narcotics-worth-over-rs-21-crore-under-operation-narcos.html)
- [PIB — AIIMS "Magnitude of Substance Use in India" (2019)](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1565001&reg=48&lang=2)
- [PIB — Nasha Mukt Bharat Abhiyaan: 29.68 crore citizens reached](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2288262&reg=48&lang=2)
- [IndiaMART — handheld ETD at ₹31 lakh](https://www.indiamart.com/proddetail/explosive-trace-detector-10339406548.html)
- [ScienceDirect — IMS and Ni-63 radioactive sources](https://www.sciencedirect.com/topics/medicine-and-dentistry/ion-mobility-spectrometry)
- [Smiths Detection — IONSCAN 600, single-use swabs](https://www.smithsdetection.com/products/ionscan-600/)
- [Tribune — train halted 6 hours over a hoax bomb threat](https://www.tribuneindia.com/news/punjab/train-halted-for-six-hours-over-hoax-bomb-threat)
- [PIB — Indian Railways net-zero by 2030](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1907230)
- [DD News — 1,337 Amrit Bharat stations](https://www.newsonair.gov.in/1337-railway-stations-identified-for-development-under-amrit-bharat-station-scheme-in-country-centre)
- [Business Standard — Startups for Railways, up to ₹1.5 Cr, 50:50 matching, innovator keeps IP](https://www.business-standard.com/article/indian-railways/railways-policy-promises-up-to-rs-1-5-crore-seed-money-for-innovations-122042200914_1.html)
- [IEEE Spectrum — Boston Dynamics Spot, $74,500 (2020 launch price, dated)](https://spectrum.ieee.org/boston-dynamics-spot-robot-dog-now-available)
- From the PS text itself: RPF seized ₹300 Cr of narcotics in 2,100+ cases in 2025;
  15–20% of drug trafficking (per NCB) routes through rail.
