# SIH26026 — Narcotics & Explosives Detection: Session Notes

**PS:** Development of Mobile (Quadruped)/Handheld Device/System for Real-Time Detection of Narcotics and Explosives across Indian Railways
**PS ID:** SIH26026 · Ministry of Railways · Theme: Robotics and Drones

---

## 1. PS Analysis Summary

**Core problem:** RPF has no field-portable chemical-identification capability. Screening today = metal detectors, limited baggage X-ray, sniffer dogs (416 nationwide), manual searches after tip-offs. ~15–20% of drug trafficking (NCB) routes through rail; ₹300 Cr seized in 2,100+ cases (2025). Recent RDX track attacks in Punjab (Sirhind, Jan 2026; Shambhu/Patiala, Apr 2026) highlight explosives risk.

**Root causes:** open-access stations, throughput pressure, physics of trace detection (military explosives near-zero vapor pressure), cost of commercial detectors, dog fatigue/limits, fragmented data, legal cost of false stops (NDPS Sec. 50).

**Competitor landscape:** NanoSniffer (IIT-Bombay/Vehant, MEMS microsensor, explosives only), Smiths IONSCAN/Rapiscan Itemiser (IMS), Thermo TruNarc (Raman), 908 Devices MX908 (mass spec), FLIR Fido X4 (fluorescent polymer), Boston Dynamics Spot / Unitree / DEEP Robotics (quadrupeds, no chemical sensing), AeroArc MULE (Indian Army, 100 units), Addverb Trakr, DFCCIL/IISc MVIS (fixed trackside under-frame vision), Integrated Security System — 199 stations, 207 baggage scanners, 129 bomb-detection devices, 416 dogs.

**Verdict on the PS:** 🟡 Yellow Light — huge impact and ministry urgency, but the PS's full chemical-detection list (16 narcotics + 9 explosives) is not achievable with low-cost sensors; must be reframed as a tiered detection network, not a magic single-sensor box.

*(Full detailed breakdown — pain points, feasibility, impact, innovation scope, clarity, evaluator lens, team strategy, AI-buildability split, data availability, judge Q&A — covered in the original analysis message; not fully reproduced here for length.)*

---

## 2. How MQ Gas Sensors Actually Work (and their real limits)

- MQ sensors (MQ-3, MQ-135, MQ-2) are tin-dioxide (SnO₂) chemiresistors: a heater keeps the surface hot; reducing gases change its resistance. Output = one analog voltage, **no molecular specificity**.
- They **cannot** detect a "narcotic" directly. What they *can* pick up are **marker VOCs** correlated with narcotics:
  - Cannabis → terpenes (myrcene, limonene, caryophyllene) — strong, real signal
  - Heroin → acetic acid (acetylation byproduct)
  - Cocaine → trace methyl benzoate (processing residue)
- This is the same principle canine detection and IMS use: react to marker/decomposition compounds, not the pure banned molecule.
- Accuracy comes from: **multi-sensor fingerprinting** (ratios across MQ-3/MQ-135/MQ-2 + BME688), a trained classifier (random forest/SVM, not simple thresholds), and a mandatory **"unknown/uncertain — needs confirmation"** rejection class.
- Correct framing for judges: *"MQ sensors detect volatile marker compounds, not narcotics themselves. We fingerprint across sensors and classify; anything off-pattern is flagged for confirmation rather than guessed."*

---

## 3. How Airports Actually Detect Narcotics (without dogs)

| Method | Principle | Why it's not cheaply replicable |
|---|---|---|
| **IMS** (Smiths IONSCAN, Rapiscan Itemiser) | Swab surface residue → heat/vaporize → ionize → drift-tube time = molecular fingerprint | Needs ionization + drift-tube hardware; detects **particle residue**, not vapor |
| **X-ray / CT baggage scanners** | Dual-energy density/atomic-number mapping, or full 3D CT + AI shape/density classification | Needs an X-ray source + radiation licensing |
| **Raman spectroscopy** (TruNarc) | Laser light scattering = vibrational molecular fingerprint | Real Raman module cost alone exceeds hackathon budget |
| **Mass spectrometry** (MX908) | Ion mass-to-charge separation, most accurate portable method | ₹15–30 lakh+ |
| **Canine olfaction** | ~300M olfactory receptors, ppt sensitivity to marker compounds | Biological — unmatched, not replicable electronically |

**Conclusion:** cheap gas-sensor arrays are a legitimate **tier-1 presumptive screen**, not a substitute for any of the above. Real deployed systems already work in tiers (cheap screen → confirmatory instrument). This is the correct architecture to pitch, not a workaround.

---

## 4. "Satisfy Every PS Point" — How To Do It Honestly

Key distinction: **SIH judges evaluate architecture + a working proof-of-concept slice**, not certified lab-grade detection of every listed substance. The "Expected Solution" section is the deployed-product spec, not the hackathon-demo bar.

**The move — plug-in detection architecture:**
```
Detection Engine
 ├── Module: Gas-sensor array (MQ+BME688)      → built, demoed live
 ├── Module: IMS adapter (drift-time reference) → interface built, fed real NIST/SWGDRUG data, simulated
 ├── Module: Colorimetric strip + camera reader → built, demoed live
 ├── Module: Raman adapter                      → interface built, simulated
 └── Fusion layer → one alert pipeline, one dashboard, one evidence chain
```
This lets every chemical on the PS list route through the same real alert/GPS/evidence pipeline — live sensors for what's physically reachable (terpene/VOC classes), simulated-but-real-reference-data adapters for the rest (RDX, PETN, cocaine, heroin, etc.), clearly labeled.

**What must never happen:** claiming the physical demo detected something it didn't (e.g., "our sensor detected RDX on camera"). Claiming the *architecture* covers it, backed by real interface code + real reference data, is standard and defensible.

**Non-chemical PS requirements** (LiDAR mapping, autonomous nav, thermal imaging, rugged/all-weather, long-duration deployment, bomb-detection *assistance*, facial recognition, multilingual, offline sync, encryption, fail-safes) are almost all buildable for real at low cost — see component list below.

---

## 5. Complete Bill of Materials

### A. Handheld — sensing & alerts (~₹3,360–4,160)
| Component | Qty | Satisfies | ₹ |
|---|---|---|---|
| Arduino Nano | 1 | Controller | 300 |
| MQ-3 module | 1 | Narcotics VOC ch.1 | 150 |
| MQ-135 module | 1 | Narcotics VOC ch.2 | 150 |
| MQ-2 module | 1 | Narcotics VOC ch.3 | 120 |
| Bosch BME688 | 1 | Narcotics detection (strongest live-hardware claim) | 1,500 |
| DHT11 | 1 | Climatic compensation | 100 |
| 5V fan + nozzle | 1 | Non-intrusive active sampling | 150 |
| Push button | 1 | Field recalibration | 20 |
| 0.96" OLED | 1 | On-device UI | 220 |
| Active buzzer | 1 | Sound alert | 40 |
| Vibration motor | 1 | Vibration alert | 80 |
| Red/green LEDs + resistors | set | Visual alert | 30 |
| NEO-6M GPS module | 1 | GPS tagging | 350 |
| DFPlayer Mini + speaker | 1 | Multilingual voice alerts | 250 |
| Enclosure (tiffin/PVC box) | 1 | Ruggedised, lightweight | 200 |
| Power bank | 1 | Field power | 0–800 |
| Wiring/perfboard | set | — | 200 |

### B. Quadruped — mechanical (~₹4,400–8,300)
| Component | Qty | Satisfies | ₹ |
|---|---|---|---|
| MG996R/DS3218 servo | 12 | Legs | 2,200–4,800 |
| PCA9685 PWM driver | 1 | Servo control | 200 |
| 3D-printed/laser-cut frame (SpotMicroAI STLs) | 1 set | Chassis | 800–1,500 |
| 2S/3S Li-ion + BEC | 1 | Servo power rail | 900–1,500 |
| Screws/standoffs | set | Assembly | 300 |

### C. Quadruped — sensing & compute (~₹7,970–20,170)
| Component | Qty | Satisfies | ₹ |
|---|---|---|---|
| Raspberry Pi 4 | 1 | Compute (gait, vision, classifier) | 3,000–5,000 |
| MPU6050 IMU | 1 | Sensor fusion, balance | 120 |
| HC-SR04 ultrasonic | 2–3 | Obstacle detection | 200 |
| Pi Camera/USB webcam | 1 | Video surveillance, optical imaging | 500–1,200 |
| AMG8833 thermal array | 1 | Thermal imaging (real, affordable) | 1,800–2,500 |
| IR LED array | 1 | Night patrolling | 200 |
| 2nd sensing head (MQ+BME688+fan) | 1 set | Narcotics detection on robot | 1,850 |
| RPLIDAR A1 (stretch) | 1 | LiDAR mapping (real, if budget allows) | 8,000–9,000 |
| microSD card | 1 | Onboard logging | 300 |

### D. Shared software/comms (₹0)
- Web Serial / MQTT (handheld ↔ dashboard)
- Offline queue (IndexedDB/SQLite) + sync-on-reconnect
- AES-256 encryption on stored logs
- SHA-256 hash-chained event log (tamper evidence)
- English + Hindi + 1 regional language, TTS
- OpenCV/`face_recognition` watchlist demo
- `detection_module` adapter interface + stubbed IMS/Raman modules (real NIST/SWGDRUG reference data)
- Random forest/SVM classifier on sensor fingerprint
- PatchCore (anomalib) or OpenCV diff-based under-frame anomaly detection
- Gazebo + CHAMP (ROS2) gait/SLAM simulation (fallback if no real LiDAR)
- Auto-generated seizure memo template
- Fail-safes: battery-low auto-sit, Wi-Fi-loss auto-stop, watchdog timer

### E. Test kit (~₹380)
- Citrus peel/oil (cannabis-terpene proxy), vinegar (heroin-marker proxy)
- Perfume, sanitizer, coffee/chilli powder (false-alarm distractors)
- Cardboard/PVC mock under-coach rig, cotton pads, tiffin
- Box labeled "TEST OBJECT" (safe bomb-assistance prop)

**⛔ Never use real narcotics, explosives, or precursors — NDPS Act 1985 / Explosives Act 1884.**

### Total cost
| Tier | Total |
|---|---|
| Without real LiDAR (Gazebo sim instead) | ~₹16,100–33,000 |
| With real LiDAR | ~₹24,100–42,000 |

**Cut order if over budget:** LiDAR → thermal AMG8833 → servo grade → BME688 (revert to MQ-only). Keep all of section D (software) — it's free and carries the "satisfies all PS points" architecture claim.

---

## 6. Open Threads / Next Steps
- [ ] Write Arduino firmware (MQ + BME688 fusion, local alert logic)
- [ ] Write Python training script (random forest/SVM on sensor fingerprint)
- [ ] Write `detection_module` adapter interface + stubbed IMS/Raman modules
- [ ] Pull SpotMicroAI repo structure; write leg IK + gait script
- [ ] Build requirement-compliance PPT slide (color-coded Real/Simulated/Roadmap)
- [ ] Collect real sensor data (≥25 samples per class, incl. distractors) → confusion matrix, ROC, false-alarm rate
- [ ] Reuse `demo-production/` pipeline (record.js, generate_tts.ps1, finalize.js) for the new demo video

---

*Exported from Claude Code session, 2026-09-12.*
