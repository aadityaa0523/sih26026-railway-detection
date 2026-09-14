# RAIL-N.E.D. Testing Plan — All Layers

**Objective:** Validate the handheld and quadruped prototypes before shortlist submission (target: December 2026).

**Testing pyramid:**
```
                        ▲
                       / \
                      /   \  System Tests (1–2 weeks)
                     /     \
                    /_______\
                   /         \
                  /    Inte-  \  Integration Tests (2 weeks)
                 /    gration  \
                /_____________\
               /               \
              /  Unit / Bench   \  Unit Tests (4 weeks)
             /       Tests       \
            /___________________ \
```

---

## LAYER 1: UNIT & BENCH TESTS (4 weeks, Sep–Oct)

### 1.1 HEAT Chamber (the critical innovation)

**Test name:** HEAT-001 to HEAT-008

| # | Test | Pass criterion | Notes |
|---|---|---|---|
| HEAT-001 | Heater element temp ramp | Reaches 200 °C in <30 sec, stable ±5 °C | Use thermocouple; plot the curve |
| HEAT-002 | NO₂ sensor response (nail polish) | Triggers at 150–200 °C; peak >100 ppm | Repeat 10×; dried nail polish only |
| HEAT-003 | NO₂ sensor vs distractors | Coffee, vinegar, chilli, diesel, attar all read <20 ppm at same temp | 5 repeats each; plot overlap |
| HEAT-004 | Thermal fingerprint separation | Nail polish's temperature-response curve is >50% different from any distractor | ML classifier shows >90% accuracy on the 7 samples |
| HEAT-005 | Chamber seal integrity | Gas leakage <5% per hour when heater off | Use mass-flow meter or pressure decay |
| HEAT-006 | Pad cleanliness after bake-out | Residual NO₂ <5 ppm after heating to 220 °C for 30 sec | 10 consecutive heat cycles |
| HEAT-007 | Micro-pump flow rate | 50–200 mL/min at 5V | Measure with rotameter or soap-bubble method |
| HEAT-008 | Heater safety (thermal runaway) | Fuse blows or MOSFET cuts power if temp >250 °C | Hold heater at 260 °C for 10 sec; must stop immediately |

**Bench setup:** breadboard + Arduino Nano for control, thermocouple reader, flow meter, nail polish samples in marked vials.

**Deliverable:** plots for HEAT-002, HEAT-003, HEAT-004 on slide 4 (the "how we detect RDX" slide).

---

### 1.2 Swab Pad & Retraction Mechanism

**Test name:** SWAB-001 to SWAB-005

| # | Test | Pass criterion | Notes |
|---|---|---|---|
| SWAB-001 | Servo movement repeatability | 100 press-and-retract cycles; all complete without jamming | Time each cycle; max deviation <10% |
| SWAB-002 | Pad contact force | 0.5–2 N when nose pitches | FSR or load cell underneath the pad |
| SWAB-003 | Residue transfer (dead lift) | Swab a test surface with food colouring, heat the pad, colour transfers to chamber | Visual or spectrophotometer |
| SWAB-004 | Pad durability | After 100 heat cycles, pad shows no visible wear or fibre loss | SEM or macro photo comparison |
| SWAB-005 | Seal when retracted | No air leakage when pad is fully retracted and heater runs | Pressure decay or flow-sensor check |

**Bench setup:** 3D-printed nose mockup, servo tester, paint/food colouring test surface, thermal camera to watch the cycle.

**Deliverable:** video clip of 10 cycles for the finale demo; still photos for slide 3.

---

### 1.3 Gas Sensors (MQ array + BME688)

**Test name:** GAS-001 to GAS-003

| # | Test | Pass criterion | Notes |
|---|---|---|---|
| GAS-001 | MOS warm-up and baseline drift | Baseline stable within ±3% after 5 min warm-up; no drift over 30 min | Sample every 10 sec; plot over time |
| GAS-002 | BME688 temp/humidity compensation | After HEAT chamber runs, BME readings return to baseline within 2 min | Measure actual vs corrected readings |
| GAS-003 | Sensor cross-talk | When one sensor is heated, others don't trigger false positives | Heat MiCS-2714; check MQ-3/135/2 don't spike |

---

### 1.4 GPS & Connectivity

**Test name:** GPS-001 to GPS-002

| # | Test | Pass criterion | Notes |
|---|---|---|---|
| GPS-001 | Cold-start fix time | Acquires position within 60 sec indoors, 10 sec outdoors | Record TTFF (time-to-first-fix) |
| GPS-002 | MQTT over 3G/LTE | Signed record publishes and syncs when online; queues locally when offline | Test publish, kill network, restart, resync |

---

## LAYER 2: INTEGRATION TESTS (2 weeks, Oct–Nov)

### 2.1 Handheld Integration

**Test name:** HH-INT-001 to HH-INT-010

| # | Test | Pass criterion | Environment |
|---|---|---|---|
| HH-INT-001 | Power-up sequence | Heater, sensors, display, GPS all initialize in <10 sec | Lab bench |
| HH-INT-002 | HEAT + sensor pipeline | Trigger heat → read NO₂ → get ML classification within 30 sec total | Handheld in hand |
| HH-INT-003 | Alert generation (all channels) | On positive: buzzer + vibrator + LED + voice alert fire simultaneously | Lab with audio meter |
| HH-INT-004 | OLED display (multilingual) | Hindi, English, and one regional language render correctly; no character corruption | Test on live device |
| HH-INT-005 | Camera + phone link | Pi camera captures video; image transfers to phone via Bluetooth or USB | Record a 10-sec clip |
| HH-INT-006 | Signing + hashing (ATECC608) | Every alert record is signed and hashed; signature verifies on a second device | Export cert, run verify script |
| HH-INT-007 | Offline storage | Records queue in SQLite when offline; sync completes when network returns | Airplane mode test |
| HH-INT-008 | Battery life (nominal) | 8+ hours of intermittent use (1 swab per 2 min) | Run in controlled lab; plot drain curve |
| HH-INT-009 | Enclosure seal | No water ingress during misting (IP54 test, 2.5 L/min for 3 min from 12.5 cm) | IP rating chamber or faucet spray |
| HH-INT-010 | Drop test (1 m concrete) | Device survives 3 drops from 1 m; no cracks, all functions work | Padded enclosure absorbs impact |

**Setup:** Full handheld prototype, power supply, test stand, smartphone/laptop for verification.

**Pass/fail:** All 10 pass before moving to system test.

---

### 2.2 Quadruped Integration

**Test name:** QR-INT-001 to QR-INT-012

| # | Test | Pass criterion | Environment |
|---|---|---|---|
| QR-INT-001 | Servo initialization | All 12 servos respond to commands within 100 ms | Lab |
| QR-INT-002 | IMU calibration | MPU6050 reads stable pitch/roll; accelerometer offsets <±50 mg | Stationary device |
| QR-INT-003 | Gait execution (stand) | Robot stands upright, CG over support polygon, all joints locked | Record video |
| QR-INT-004 | Gait execution (walk) | Walk 2 m forward in a straight line; no falling, max drift <10 cm | Flat floor |
| QR-INT-005 | Nose fold (retract/deploy) | Servo folds nose 90°, swab pad seats in heater chamber, no binding | 20 cycles |
| QR-INT-006 | LiDAR scan (2D) | Acquires full 360° scan; no more than 5% dropouts | Stationary in a room |
| QR-INT-007 | Thermal imaging (MLX90640) | Records a thermal image every 2 sec; no corruption, temp range 0–50 °C | Handheld thermal reference to compare |
| QR-INT-008 | USB camera (under-frame view) | Records 1080p 30fps without drop frames; field of view ≥120° | Test video saved to disk |
| QR-INT-009 | MQTT on robot | Record publishes + syncs; same as HH-INT-002 but over onboard compute | Use Pi 4/5 connected to lab network |
| QR-INT-010 | Battery voltage monitor | BEC reports voltage; firmware cuts motors if V_batt <6V (failsafe) | Discharge battery to near-empty |
| QR-INT-011 | E-stop (link loss) | If MQTT/radio link drops, robot auto-sits within 2 sec | Kill network; watch robot |
| QR-INT-012 | Enclosure seal (robot) | Same as HH-INT-009; IP54 rating for the sensor chamber | Misting test |

**Pass/fail:** All 12 pass before system test.

---

## LAYER 3: SYSTEM TESTS (1–2 weeks, Nov–Dec)

### 3.1 End-to-End Handheld Flow

**Test name:** HH-SYS-001 to HH-SYS-005

| # | Test | Scenario | Pass criterion |
|---|---|---|---|
| HH-SYS-001 | Seizure workflow (positive) | Constable swabs a test bag (nail-polish residue), gets alert, records GPS + video + memo | Memo is auto-populated with all fields; GPS accuracy <10 m; video is legible |
| HH-SYS-002 | Seizure workflow (negative) | Swab a clean bag; no alert, record is still timestamped and synced | Clean record appears on dashboard |
| HH-SYS-003 | Two-route rule | Constable swabs twice (both positive) and submits one memo | Memo shows "2/2 routes agree"; confidence >90% |
| HH-SYS-004 | Network loss recovery | Officer swabs, loses network, walks to station, reconnects → records sync | All offline records reach the server |
| HH-SYS-005 | Live demonstration (gate scenario) | Handheld constable swabs a demo bag in front of judges; alert fires within 30 sec | Judges see green or red LED, hear alert, see memo |

---

### 3.2 End-to-End Quadruped Flow

**Test name:** QR-SYS-001 to QR-SYS-004

| # | Test | Scenario | Pass criterion |
|---|---|---|---|
| QR-SYS-001 | Pit-line patrol (20 m) | Robot walks a marked pit line, stops at 3 marked "coaches", swabs each, records position and thermal | All 3 positions logged within ±0.5 m; thermal shows hotspot (heat pad placed under mock coach) |
| QR-SYS-002 | Obstacle avoidance | Place a chair in the robot's path; it detects and stops or reroutes | LiDAR shows the obstacle; robot doesn't crash |
| QR-SYS-003 | Recovery from link loss | Radio link fails mid-patrol; robot auto-sits; link restored → resumes from last waypoint | Logs show "link loss at (x,y); resumed at (x,y)" |
| QR-SYS-004 | Live demonstration (yard scenario) | Robot walks a pit line, swabs a mock bag, records alert, sends to control-room dashboard | Dashboard shows alert with GPS, thermal, and video thumbnail |

---

### 3.3 Dashboard Verification

**Test name:** DASH-001 to DASH-003

| # | Test | Scenario | Pass criterion |
|---|---|---|---|
| DASH-001 | Real-time feed | Trigger 5 alerts from handheld/robot; all appear on dashboard within 5 sec | Timestamp, GPS, confidence, video thumbnail all present |
| DASH-001b | Offline alert queue | Trigger alerts while Wi-Fi is off; reconnect; queue drains and appears in order | Events are ordered by original timestamp, not arrival |
| DASH-002 | Seizure memo generation | Click an alert; auto-populated memo includes all NDPS-required fields | Officer ID, bag description, witness, evidence handling all present |
| DASH-003 | Evidence verification | Export a record; run the verification script; signature check passes | Script output: "✓ Valid signature, unmodified record, timestamp [time]" |

---

## LAYER 4: FIELD & ENVIRONMENTAL TESTS (1 week, Nov)

### 4.1 Handheld Field Tests

**Test name:** HH-FIELD-001 to HH-FIELD-004

| # | Test | Environment | Pass criterion |
|---|---|---|---|
| HH-FIELD-001 | Heat + humidity | Operate in 35 °C, 80% RH (Indian summer); run 20 swabs | No sensor drift >±5%; no false positives |
| HH-FIELD-002 | Dust & salt spray | IP54 misting + dust chamber; run 10 swabs | Enclosure shows no water inside; all sensors respond |
| HH-FIELD-003 | GPS denial (tunnel/building) | Operate indoors with no GPS; LiDAR not available; fallback to manual entry | Record is timestamped; GPS field is marked "denied" |
| HH-FIELD-004 | Low battery | Run device until voltage drops below 5V; auto-cutoff activates | Device powers down cleanly; no data loss |

---

### 4.2 Quadruped Field Tests

**Test name:** QR-FIELD-001 to QR-FIELD-003

| # | Test | Environment | Pass criterion |
|---|---|---|---|
| QR-FIELD-001 | Uneven terrain (ballast simulation) | Pit of pea gravel and small stones, 30 m path | Robot walks without tipping; max speed 0.2 m/s; recovers from small stumbles |
| QR-FIELD-002 | Electromagnetic interference (25 kV lines) | Operate within 10 m of a high-voltage wire (lab simulation: high-frequency noise) | No sensor glitches; servo commands still execute |
| QR-FIELD-003 | Thermal drift | Heat the robot to 40 °C (direct sun); run HEAT chamber | Temperature compensation keeps baseline stable; no false NO₂ spike |

---

## LAYER 5: STRESS & ENDURANCE TESTS (1 week, Nov)

### 5.1 Handheld Endurance

**Test name:** HH-STRESS-001 to HH-STRESS-002

| # | Test | Scenario | Pass criterion |
|---|---|---|---|
| HH-STRESS-001 | 100-swab marathon | Continuous operation: swab, heat, read, record, repeat, no breaks | All 100 records are valid; no memory leaks; battery depletes linearly; no sensor saturation |
| HH-STRESS-002 | Servo life (swab pad retraction) | 500 press-and-retract cycles on the swab servo | Max 1 failure in 500; replace pad every ~100 cycles |

---

### 5.2 Quadruped Endurance

**Test name:** QR-STRESS-001 to QR-STRESS-002

| # | Test | Scenario | Pass criterion |
|---|---|---|---|
| QR-STRESS-001 | 4-hour patrol | Robot walks a 500 m loop continuously; pauses every 50 m to swab a test point; relogs route | Battery depletes to 30%; no servo overheating (temp <60 °C); all 10 swab records are valid |
| QR-STRESS-002 | Servo wear (all 12 legs) | 2-hour continuous walk with max torque (climb 10° slope, hold) | No servo releases smoke; check for gear play after test |

---

## LAYER 6: SAFETY & COMPLIANCE TESTS (2 weeks, Oct–Nov)

### 6.1 Electrical Safety

**Test name:** SAFE-001 to SAFE-003

| # | Test | Scenario | Pass criterion |
|---|---|---|---|
| SAFE-001 | Heater overheat protection | Force heater to 280 °C; fuse or cutoff must stop it by 290 °C | Record temp curve with overshoot <10 °C past 260 °C limit |
| SAFE-002 | Battery charge safety | Charge Li-ion pack to 4.25V per cell (overcharge); BMS must cut charge at 4.20V | Test with bench power supply |
| SAFE-003 | Robot motor stall detection | Run motor into a wall (locked rotor); current limit must trigger within 500 ms | Measure current and response time |

---

### 6.2 Legal & Regulatory

**Test name:** LEGAL-001 to LEGAL-002

| # | Test | Scenario | Pass criterion |
|---|---|---|---|
| LEGAL-001 | Evidence chain (BNSS §105 + BSA §63) | Generate a signed record; export it and verify with a third-party script | Judge / FSL confirms format matches regulations |
| LEGAL-002 | No narcotics in testing | Audit all test samples used; confirm none are NDPS-listed | Nail polish, vinegar, coffee, chilli, attar, diesel only |

---

## Deliverables by submission milestone

### **Week of 20 Sep (end of unit tests)**
- ✅ HEAT chamber bench plots (HEAT-002, 003, 004)
- ✅ Swab pad durability photos (SWAB-004)
- ✅ Test summary: 8/8 HEAT tests pass; 5/5 SWAB tests pass

### **Week of 30 Oct (end of integration tests)**
- ✅ Handheld video: full workflow (swab → alert → memo → sync)
- ✅ Robot video: pit-line walk + swab + alert
- ✅ Test summary: 10/10 HH-INT, 12/12 QR-INT pass

### **Week of 15 Nov (end of system & field tests)**
- ✅ Dashboard screenshot: live alert feed with 5 demo events
- ✅ Memo example: auto-populated seizure memo
- ✅ Heat+humidity test result: no sensor drift
- ✅ Test summary: 23/23 system tests + 7/7 field tests pass

### **Week of 1 Dec (end of stress tests & shortlist submission)**
- ✅ Endurance test logs: 100-swab handheld, 4-hour robot patrol
- ✅ Legal compliance: evidence-chain verification script + sample output
- ✅ **Gate 1 decision: ready for shortlist → proceed to finals**

---

## Go / No-Go gates

| Gate | Trigger | Decision |
|---|---|---|
| **G1 (HEAT bench)** | HEAT-002, 003, 004 all pass by Sep 20 | Go: proceed with handheld build. No-go: fall back to colour-swab design |
| **G2 (Integration)** | HH-INT 10/10, QR-INT 12/12 by Oct 30 | Go: proceed to system tests. No-go: debug and re-test |
| **G3 (System)** | HH-SYS 5/5, QR-SYS 4/4, DASH 3/3 by Nov 15 | Go: ready for shortlist. No-go: bug fix + one more week of testing |
| **G4 (Stress)** | HH-STRESS 2/2, QR-STRESS 2/2, LEGAL 2/2 by Dec 1 | Go: **submit shortlist**. No-go: extend to Dec 10 or withdraw |

---

## Test data archive

Save every test result to a `tests/` folder in the repo:
```
tests/
├── HEAT-001_ramp.csv           (temp vs time)
├── HEAT-002_response.csv       (NO₂ ppm vs temp, all repeats)
├── HEAT-003_distractors.csv    (7 samples, 5 repeats each)
├── SWAB-001_cycles.csv         (servo cycle time, 100 cycles)
├── HH-INT-001_log.txt          (power-up sequence, timestamps)
├── HH-SYS-001_video.mp4        (seizure workflow)
├── QR-SYS-001_log.csv          (robot positions, timestamps)
├── DASH-001_screenshot.png     (alert feed)
└── LEGAL-001_verification.txt  (signature check output)
```

Every test has a pass/fail line that can be grepped.
