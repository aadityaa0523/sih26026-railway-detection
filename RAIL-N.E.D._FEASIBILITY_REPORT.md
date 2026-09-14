# RAIL-N.E.D. — Feasibility and Viability Report (v2)

**Team:** CONGNIVISTA · **PS:** SIH26026 (Ministry of Railways) · **Date:** 14 Sep 2026

> **v2 corrects errors in v1:**
> - The NO₂ sensor is the SGX **MiCS-2714**; MQ-131 is an ozone sensor.
> - The safe test sample is dried nail **polish**, which contains nitrocellulose; nail-polish *remover* doesn't.
> - FSL reports are confidential case records, not public ones.
> - DS3225 servos cost about ₹1,200–1,800 each, so the robot is about ₹50k, not ₹23k.
> - IMS trace detectors cost several lakh, not ₹50k.
> - The invented accuracy figures, sample counts and dates are removed.
>
> Prices are indicative; check them before quoting.

---

## 1. Verdict

- **Feasible for a prototype, on two conditions:**
  1. The HEAT bench test shows a clear NO₂ signal from a legal stand-in, above all common distractors.
  2. The seizure-learning loop is shown as a working pipeline on our own data plus a pilot request to RPF. It is not presented as already holding real seizure data.
- **Viable at scale:** handheld ≈ ₹7k, quadruped ≈ ₹50k, no chemical reagents, reusable swabs.
- **Fallback:** if the HEAT test fails, the residue route reverts to colour-test swabs (the previous design). Nothing else in the system changes, so the risk is contained.

---

## 2. What changed from the previous solution

| Element | Previous (route matrix) | New | Why it's better | Cost of the change |
|---|---|---|---|---|
| Residue explosives (RDX, PETN) | Colour-test swab card read by a camera; reagents, single-use | **HEAT**: swab heated in a 5 mL chamber; an NO₂ sensor plus release temperature give a fingerprint | Reaches non-volatile explosives with no chemicals; reusable swab; digital trace | +≈ ₹2.2k per unit |
| Robot | Sniffs and looks | Sniffs, looks **and swabs** (nose pad retracts into the heater) | Robot can test a suspect bag while the bomb squad stays back | +1 micro-servo, pad holder |
| Training data | Lab stand-ins only | Lab stand-ins now, plus FSL-labelled field data through an RPF pilot | Real-world accuracy without the team ever handling narcotics | Governance effort, MoU |
| Evidence | Hash-chained log | Device-signed record + phone video, aligned to BNSS §105 / BSA §63 | Legal grounding instead of a buzzword | ATECC608 chip ≈ ₹150 |
| Unchanged | SNIFF route, SEE (change vs last clean scan), two-route rule, dashboard, offline sync, multilingual alerts | — | — | — |

---

## 3. Feasibility, innovation by innovation

### 3.1 HEAT chamber: detect what doesn't evaporate

**Principle**
- RDX gives off about 5 parts per trillion of vapour at 25 °C (vapour pressure ≈ 4×10⁻⁹ Torr). No vapour sensor can reach that, PID included.
- When heated, RDX's weakest bond (N–NO₂) breaks. Near its melting point (≈ 205 °C), NO₂ is among the first products. PETN and nitroglycerin, both nitrate esters, behave the same way at lower temperatures.
- Airport trace detectors also start by heating the swab (thermal desorption), but then use an IMS costing several lakh. We replace the IMS with low-cost gas sensors plus the release temperature. That's less specific, so positives always go for confirmation.

**Signal estimate (theory; the bench test decides)**
- 1 µg of RDX is 4.5 nmol. Released into 5 mL of air (≈ 0.2 mmol) at about one NO₂ per molecule, that's up to ≈ 20 ppm NO₂.
- Allowing 10–100× losses (swab transfer, wall adsorption, partial decomposition) gives ≈ 0.2–2 ppm.
- The MiCS-2714 measures 0.05–10 ppm, so microgram-level residue is in range on paper.
- The key insight is to **shrink the air, not the sensor**: a small chamber turns a tiny mass into a readable concentration.

**Fingerprint = which sensor fires × at what temperature** during a 50 → 250 °C ramp. NO₂ is an oxidising gas; drug and terpene vapours are reducing gases, so they push the sensors in opposite directions.

**Build (handheld, ≈ ₹2.2k)**

| Part | Approx. cost |
|---|---|
| Ceramic (MCH) heater, MOSFET, PID temperature control | ₹150 |
| K-type thermocouple + MAX6675 | ₹300 |
| SGX MiCS-2714 NO₂ sensor | ₹1,000 |
| Micro-pump at low flow | ₹400 |
| Small aluminium or steel chamber | ₹300 |

The existing MOS array and BME688 sit downstream and share the same air path.

**Power:** 10 W × 30 s ≈ 0.08 Wh per swab. A 2S 2,000 mAh pack (≈ 15 Wh) gives 100+ swabs per charge. The three MQ heaters draw about 0.8 W each, so duty-cycle them.

**Legal stand-ins for testing**
- **Target:** a trace dab of dried nail polish. It contains nitrocellulose, a nitrate ester in the same class as PETN and nitroglycerin. Use a trace only; nitrocellulose ignites near 170 °C, and a dab is harmless in a metal chamber.
- **Distractors:** vinegar, coffee, chilli, attar, agarbatti ash, diesel, sanitiser, sweat.
- **Never** use ammonium nitrate (regulated under the Ammonium Nitrate Rules, 2012) or any explosive or narcotic. Testing real RDX needs an authorised lab (DRDO TBRL/HEMRL or CFSL); that's on the roadmap.

**Honest limits:** HEAT identifies a class (nitro/nitrate), not a specific molecule. Every positive needs FSL or IMS confirmation.

| Risk | Mitigation |
|---|---|
| Any heated organic gives off gases (false positives) | Dedicated NO₂ channel + release temperature + a "reject if unsure" class |
| Heater safety | Thermal fuse, 260 °C hard cut-off, metal chamber, trace samples only |
| Carry-over between swabs | Bake-out cycle after each test; reading is invalid until the baseline returns |
| Humidity and heat drift | BME688 compensation; clean-air baseline button |

**Bench test (gate G1)**
1. Test on a blank swab, then 8 distractors, then the nail-polish dab.
2. Run 10 repeats each on a 50 → 250 °C ramp.
3. Plot NO₂ response against temperature for each sample.
4. **Pass:** the stand-in's NO₂ peak separates clearly from every distractor in all repeats.

### 3.2 A robot that swabs

- **Mechanism:** a felt or PTFE-fibreglass pad sits on the nose tip. The robot pitches its body to press the pad on a bag or handle, then a micro-servo pulls the pad into the heater port. The pad is baked clean after each use.
- **Status:** the nose boom exists in the v3 chassis CAD. The swab port goes into the pending sensor-chamber task.
- **Parts:** micro-servo ≈ ₹150, pad holder and guide ≈ ₹300, spare pads.

| Risk | Mitigation |
|---|---|
| Uneven contact force | Force sensor (FSR, ≈ ₹100) or servo-current check; retry if contact fails |
| Dust in the port | Mesh screen + purge cycle |
| Pad wear | Pads are cheap and replaceable in the field |

**Bench test:**
- 100 press-and-retract cycles
- a seal leak check
- transfer test: dab nail polish on a bag handle, swab it with the robot, and compare the signal against a hand-swab

**Demo:** do it live with the stand-in.

### 3.3 Every seizure trains the fleet

**Flow**
1. At a seizure, the officer swabs the package exterior before it is sealed, creating a signed record.
2. The FSL analyses the sample, which is already mandatory.
3. RPF enters only the result class (for example "cannabis").
4. The label joins the record.
5. The model retrains periodically.
6. A signed model update goes out, and each device verifies the signature before installing.

**Why it's legal:** no one outside RPF and the FSL ever handles the drugs. The team never touches them.

**Governance:** FSL reports are confidential case records. Only the substance class is shared, through RPF, under an MoU. No personal data enters the training set.

**Prototype scope:** show the loop end-to-end on our own stand-in data with a simulated delayed label, and ask RPF for a pilot letter. Don't claim sample counts we don't have. The ceiling is one labelled field sample per swabbed seizure (RPF: 2,100+ seizures in 2025).

| Risk | Mitigation |
|---|---|
| MoU delayed or refused | The prototype doesn't depend on it; the loop is shown on our own data |
| FSL backlog delays labels | Fine for batch retraining |
| Class imbalance (ganja dominates seizures) | Per-class thresholds; "unknown" class |
| Model poisoning | Signed updates, staged rollout, rollback |

### 3.4 Born-legal evidence

**Legal hooks (verify exact wording before submission)**
- **BNSS 2023 §105:** search and seizure must be recorded by audio-video means, preferably a mobile phone. Check how this applies alongside NDPS search procedure.
- **BSA 2023 §63:** electronic records need a certificate. The format in the Schedule includes the record's hash value.
- **e-Sakshya:** the MHA app for recording search and seizure. Check export or integration options.

**Implementation**
- The constable's phone records the video.
- The handheld signs the sensor record with an ATECC608 chip (ECDSA P-256; the key never leaves the chip).
- The app hashes the video and record together (SHA-256), encrypts them (AES-256) and syncs when online.
- A verification script lets the court or FSL check integrity.
- This is not blockchain. It is a signed, hash-linked log.

| Risk | Mitigation |
|---|---|
| Legal interpretation differs | Get written guidance from a public prosecutor or FSL; reword the slide to match |
| Device key compromised | One key per device, revocation list, tamper-evident chip |

---

## 4. Viability

**Handheld (≈ ₹7k)**

| Part | ₹ |
|---|---|
| ESP32-S3 | 700 |
| MQ-3, MQ-135, MQ-2 | 450 |
| BME688 | 1,500 |
| HEAT chamber (heater, thermocouple + MAX6675, MiCS-2714, pump, chamber) | 2,150 |
| NEO-6M GPS | 350 |
| OLED | 220 |
| Buzzer, vibration motor, LEDs | 150 |
| ATECC608 | 150 |
| 2S Li-ion + charger | 700 |
| Enclosure, wiring | 500 |
| **Total** | **≈ 6,870** |

**Quadruped (≈ ₹50k)**

| Part | ₹ |
|---|---|
| DS3225 × 12 | ≈ 18,000 |
| Raspberry Pi 5 (8 GB) | ≈ 8,000 |
| RPLIDAR C1 | ≈ 7,500 |
| MLX90640 thermal | ≈ 5,000 |
| USB camera | 800 |
| PCA9685 | 250 |
| IMU | 150 |
| Battery + BEC | 2,500 |
| Frame, printing, fasteners | 2,000 |
| Sensor + HEAT chamber | 4,100 |
| Swab nose | 600 |
| ATECC608 + microSD | 550 |
| **Total** | **≈ 49,450** |

**Reference points:** Boston Dynamics Spot ≈ US$75k (₹60 L+); imported IMS trace detectors cost several lakh each.

- **Consumables:** no chemicals; swab pads are reused after bake-out and replaced occasionally.
- **Maintenance:** clean-air recalibration of the MOS sensors; replaceable heater; check the NO₂ sensor's rated life in its datasheet.
- **Operations:** about 30 s per swab. The constable swabs, inserts and reads the light, with Hindi or regional-language voice alerts.
- **Scale:** the handheld price allows one per RPF post; robots go to high-risk yards and stations.

---

## 5. Plan with decision gates

Fill in dates against the actual SIH calendar.

| Phase | Work | Gate |
|---|---|---|
| 0 | Verify BNSS §105, BSA §63 and e-Sakshya; order parts | Legal refs confirmed, or slide wording softened |
| 1 | HEAT bench test (3.1) | **G1:** stand-in clearly separates from distractors → keep HEAT; otherwise fall back to colour swabs |
| 2 | Handheld v1; robot swab nose | 100-cycle swab test passes |
| 3 | Learning-loop pipeline demo; RPF pilot-letter request | Loop runs end-to-end on our data |
| 4 | Integration; heat, drop and battery tests | Live demo script runs 5 times without a failure |

---

## 6. Verify before the PPT goes in

1. **BNSS §105:** exact wording and how it applies to NDPS searches.
2. **BSA §63:** the Schedule certificate includes a hash-value field.
3. **e-Sakshya:** scope, and whether RPF uses it.
4. **MiCS-2714:** range and response time, and current Indian prices for every BOM line.
5. **RDX residue:** a published source for typical microgram-level residue after handling explosives (cite it on slide 4).
