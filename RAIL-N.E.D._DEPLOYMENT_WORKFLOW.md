# RAIL-N.E.D. — Operational Workflow (How RPF uses it)

---

## SCENARIO 1: Entry Gate Screening (Handheld Constable)

**Time: 08:00 AM, Mumbai Central Station, Platform 1 Entry Gate**

### Step 1: Constable prepares the handheld
- Constable arrives at gate with handheld device (charged, online via 4G).
- Clicks "Start Duty" on OLED.
- Device auto-logs location (GPS), officer ID (biometric or PIN), and timestamp.
- Handheld is in Hindi mode (voice prompts in Hindi).
- State: **Ready to scan**.

### Step 2: Passenger arrives with luggage
- Passenger queues with a backpack.
- Constable holds out the handheld: "Kripya aapka bag swab karne deejiye" (Please let me swab your bag).
- **Non-intrusive:** bag stays closed; no search, no opening.

### Step 3: Constable swabs the bag handle
```
Action                 Time    Display & Audio
─────────────────────────────────────────────────
Swab pad touches       0 sec   "Scanning…" (OLED)
handheld surface        
(2–3 sec contact)            

Pad retracts into      1 sec   Servo whine sound (normal)
heater chamber               
(motorized)                  

Heater ramps           15 sec  OLED: "T = 50°C… 100°C… 150°C…"
50→200°C                     (temperature display)
                             
NO₂ sensor reads       5 sec   "Analyzing…" + soft beep every sec
during ramp                   
                             
ML classifier          2 sec   Algorithm compares NO₂ fingerprint
processes the signal         against trained profiles
```

**Total: 30 seconds**

### Step 4a: Result = NEGATIVE (green)
- **OLED display:** ✓ GREEN tick
- **Audio:** cheerful beep + Hindi: "Shuddh, aage badhiye" (Clear, move ahead)
- **Record created:** 
  ```
  Timestamp: 08:00:32
  Location: Mumbai Central, Gate 1 (GPS: 19.0176, 72.8194)
  Officer: Const. Rajesh [ID: RPF-001]
  Device: Handheld #H-042
  Bag description: Backpack, blue
  Result: Negative (Confidence 98%)
  Evidence: Sensor trace, video frame, signed hash
  ```
- **Passenger:** "Shukriya" (Thank you) and moves through.
- **Constable:** continues to next passenger.

### Step 4b: Result = POSITIVE (red)
- **OLED display:** ✗ RED X
- **Audio:** loud buzzer + vibration + Hindi: "Samaan ko rukiye, yah pos-i-tiv hai" (Hold your bag, this is positive)
- **Device action:**
  - Auto-records 15-second video (constable's phone camera, already rolling since swab started)
  - GPS position locked
  - Record status: **Pending Confirmation**
  ```
  Alert Level: ⚠️ TIER 1 (first pass only)
  Confidence: 72%
  Suspected class: Heroin marker (acetic acid) or Unknown VOC
  Next step: Two-route check required
  ```

### Step 5: Two-route confirmation (if positive)
**Constable must swab a SECOND part of the bag (two-route rule — no single sensor decides).**

- Constable: "Aapke bag ka aur ek samaan nahi check kar du?" (Let me check another part?)
- Swabs the **zipper** or **shoulder strap** (different surface).
- Repeats steps 3–4.

**Outcome:**
- **Both swabs negative:** ✓ False alarm. Passenger goes through. Record: "Inconclusive."
- **Both swabs positive:** 🚨 Escalate to officer with NNBS/IMS.
- **One + one –:** Record marked "Reject — conflicting results." Passenger may proceed (no evidence).

### Step 6: If escalated (2 routes agree)
- **Officer approach:** A senior constable or inspector with portable **IMS** (or field reagent test) comes to reswab.
- **Passenger:** held for 10–15 min.
- **IMS result** (lab-grade): ✓ Confirmed or ✗ False alarm.
- **If confirmed:** NDPS seizure procedure starts (Sec 50, officer present, video rolling, memo filled).
- **All record:** GPS, time, evidence chain, officer photo, witness signatures (via phone app) → **admissible in court**.

### Step 7: Shift sync
- Constable ends shift at 16:00.
- Clicks "End Duty."
- Handheld uploads all 120 records of the day (100 negative, 15 inconclusive, 5 positive escalations) to the **RPF control room server**.
- Each record carries its signed hash; control room auto-verifies.
- **State:** Ready for next day.

---

## SCENARIO 2: Parcel Office Screening (Handheld Constable)

**Time: 10:00 AM, Mumbai Central Parcel Office**

### Step 1: Parcel arrives from sender
- Unclaimed parcel, origin unknown, flagged by manual screening.
- Parcel office in-charge hands it to the constable with handheld.

### Step 2: Swab the parcel exterior
- Constable swabs the **parcel tape and corners** (high-residue zones).
- Same 30-second cycle as gate screening.

### Step 3: Result = Positive
- Alert fires immediately.
- **Recording:** Parcel is photographed (phone camera), barcode scanned, weight noted.
- **Record:**
  ```
  Location: Parcel Office, Mumbai Central
  Parcel ID: PO-20260914-0847
  Origin: Unknown/Anonymous tip
  Weight: 2.3 kg
  Swab result: Positive, Heroin marker, 85% confidence
  Device: Handheld #H-042
  Officer: Const. Rajesh
  Hash: 3x4f9c1f86b5cb1...  [signed by device key]
  Status: Pending IMS confirmation
  ```

### Step 4: Escalation
- Parcel is **sealed in an evidence bag** (new bag, untouched).
- Handheld record + photo + hash are printed as an **evidence certificate**.
- Parcel is held for IMS test.
- **Control room dashboard** shows: "PO-20260914-0847 Positive · Heroin class · Rajesh · GPS: 19.0176, 72.8194 · Time: 10:07 · Confidence: 85%"
- Duty officer reviews on the dashboard and authorizes next step.

### Step 5: IMS confirmation (lab, next day)
- FSL tests the parcel, confirms heroin.
- FSL report is entered into RPF's case management system.
- **The same report becomes a training label** for the ML model (via RPF's data-sharing MoU):
  ```
  Event ID: PO-20260914-0847
  Sensor fingerprint: [NO₂ 85 ppm @ 165°C, MQ-3 120 pV, MQ-135 45 pV]
  FSL result: ✓ Heroin confirmed
  [Label saved; model retrains on Friday]
  ```

### Step 6: Seizure memo (auto-generated)
```
═════════════════════════════════════════════
        SEIZURE MEMO
        Ministry of Railways, RPF
═════════════════════════════════════════════
Date & Time:    14 Sep 2026, 10:07 AM
Location:       Parcel Office, Mumbai Central
Officer:        Const. Rajesh Kumar [ID: RPF-001]
Device:         SenseGuard Handheld #H-042
Suspect Item:   Parcel, 2.3 kg
Description:    Brown kraft box, taped
Witnesses:      Parcel clerk [Name], Station master [Name]
Scan Result:    Heroin marker detected (confidence 85%)
                IMS confirmed: Heroin

Remarks:        Item swabbed at exterior per NDPS 
                procedure, photo attached, sealed in 
                evidence bag, referred to FSL.

Procedure:      BNSS §105 - video recorded ✓
                Evidence signed & hashed ✓
                Officer ID biometric ✓

Seized by:      [Signature + phone OTP]
Date signed:    14 Sep 2026, 10:15 AM
═════════════════════════════════════════════
[QR code for hash verification]
```

**Printed on thermal printer at parcel office in <2 minutes.**

---

## SCENARIO 3: Yard & Under-Frame Patrol (Quadruped Robot)

**Time: 22:00 PM (10 PM), Mumbai Central Pit Line (under coaches)**

### Step 1: Operator preps the robot
- Maintenance shift, robot is docked and charged.
- Operator (seated in the control cabin) connects to the robot via MQTT.
- **Mobile dashboard** shows:
  ```
  Robot #QR-01 Status
  ─────────────────
  Battery: 100%
  GPS: On (has outdoor LTE)
  LiDAR: Ready
  Thermal: Ready
  Swab nose: Ready
  Last position: Dock A
  Geofence: Pit line zone (active, 25 kV overhead lines marked as no-go)
  ```

### Step 2: Operator sends patrol waypoint
- Operator taps on the **pit-line map** on the dashboard.
- Marks 5 coaches (A1–A5) to be scanned.
- Clicks "Start patrol."

### Step 3: Robot walks to Coach A1
```
Action                        Display on Operator Dashboard
──────────────────────────────────────────────────────────
Robot exits dock              ✓ Dock exit logged
                             Position: A1_START (GPS)

LiDAR scan (360°)            Map view shows pit line, walls
                             Obstacle: None

Walk 20 m to A1              Position updates every 2 sec
                             Speed: 0.18 m/s

Arrive at A1                 ✓ Waypoint reached
                             Time: 22:08
```

### Step 4: Robot swabs under Coach A1
```
Action                        Time    Sensor Data
─────────────────────────────────────────────────────────
Nose deploys (lowers)        0 sec   Servo angle: -45°
                             
Swab pad touches the         2 sec   Force sensor: 1.2 N
under-frame (spot chosen     
by LiDAR height)             

Pad retracts into chamber    1 sec   Seal check: OK
                             
Heater ramps                15 sec   NO₂: 5 ppm (baseline)
                                    MQ-3: 10 pV (clean)
                                    Temp: 50→200°C
                             
ML classifies                2 sec   Result: NEGATIVE (99% confidence)
```

**Total: 22 seconds**

### Step 5: Result = Negative
- **Record:**
  ```
  Coach: A1
  Timestamp: 22:09:15
  GPS: 19.0178, 72.8195
  LiDAR z-height: 0.15 m (under frame confirmed)
  Thermal scan: No hotspots detected
  Swab result: Negative
  Confidence: 99%
  Signed by: QR-01 (Jetson key: 4a9c2f...)
  Device status: Scan complete
  ```
- **Dashboard:** Green tick for Coach A1.
- **Video:** thermal image + LiDAR scan automatically saved.

### Step 6: Continue to Coach A2–A5
- Robot walks autonomously to A2, swabs, moves to A3, etc.
- All 5 coaches scanned in ~15 minutes.
- **No human touches the under-frames; no risk of electrocution from overhead lines.**

### Step 7: Result = Positive at Coach A3
```
Coach A3, Timestamp 22:24:47
Swab result: POSITIVE
NO₂ signal: 145 ppm @ 172°C
MQ-3 response: Strong (150 pV)
ML confidence: 81% (Unknown explosive class, possible RDX marker)
Status: ALERT — Bomb squad required
```

- **Robot action:**
  - Auto-records video (chest camera, wide angle).
  - Stays at the spot; does NOT re-swab (waits for human).
  - Sends alert to operator: 🚨 "ALERT at Coach A3 under-frame."
  
- **Operator action:**
  - Calls bomb squad: "Quadruped has flagged Coach A3 under-frame."
  - Bomb squad arrives (5–10 min) with protective gear and IMS.
  - Robot stays put, replays the thermal image + LiDAR for the squad.
  - Squad swabs the spot with IMS (two-route rule).
  
- **If IMS confirms explosives:**
  - Track is evacuated.
  - Police and Army EOD called.
  - Record includes robot's video + signed hash + IMS result.
  
- **If IMS is negative:**
  - False alarm logged.
  - Model learns: "This thermal/residue signature = false positive."
  - Record: "Coach A3 under-frame, false alarm, robot over-sensitive, adjust threshold."

### Step 8: Patrol complete
- Robot returns to dock.
- **Control room dashboard shows:**
  ```
  Pit Line Patrol #QR-01 Complete
  ─────────────────────────────────
  Duration: 22 min
  Distance: 120 m
  Coaches scanned: 5
  Results: A1 ✓ A2 ✓ A3 🚨 A4 ✓ A5 ✓
  Alerts: 1 (pending IMS)
  All records signed ✓
  Video: Coach A3 saved
  ```
- Operator downloads all records for the shift.
- Robot is charged, ready for next night.

---

## SCENARIO 4: Control Room Dashboard (Supervisor)

**Time: 09:00 AM, Mumbai Central RPF Control Room**

### The supervisor's view
- **Live alert feed** (last 24 hours):
  ```
  Time         Device       Location            Result  Confidence  Officer
  ─────────────────────────────────────────────────────────────────────────
  08:15:22     HH-042       Platform 1 Gate     NEG     99%        Rajesh
  08:22:47     HH-042       Platform 1 Gate     POS     75%        Rajesh
  08:23:15     HH-042       Platform 1 Gate     POS     88%        Rajesh
  09:47:10     HH-039       Parcel office       NEG     97%        Prabhat
  10:07:33     HH-039       Parcel office       POS     85%        Prabhat ← 2 routes agree
  22:09:15     QR-01        Coach A1, pit       NEG     99%        [Auto]
  22:15:42     QR-01        Coach A2, pit       NEG     98%        [Auto]
  22:24:47     QR-01        Coach A3, pit       POS     81%        [Auto] ← Escalated
  22:31:15     QR-01        Coach A4, pit       NEG     97%        [Auto]
  22:39:22     QR-01        Coach A5, pit       NEG     96%        [Auto]
  ```

### Click on an alert: "10:07:33 Parcel office POS"
- **Detail panel opens:**
  ```
  ═══ ALERT DETAILS ═════════════════════
  ID: PO-20260914-0847
  Device: Handheld #H-039 (Prabhat)
  Time: 14 Sep 2026, 10:07:33 AM
  Location: Mumbai Central, Parcel Office
  GPS: 19.0176, 72.8194 ± 5 m
  
  ITEM
  ───
  Description: Parcel, brown kraft box, 2.3 kg
  Scan 1: 08:15:22 - POS (85% heroin marker)
  Scan 2: 08:15:48 - POS (88% heroin marker)
  Two-route rule: ✓ PASS (both agree)
  Status: Escalated to IMS
  
  EVIDENCE CHAIN
  ──────────────
  Video: [Play] (15 sec, officer at parcel office)
  Sensor trace: [Graph] (NO₂ rise, MQ responses)
  Hash: 3x4f9c1f86b5...
  Signed by: Device HH-039 (ATECC608 key)
  Verification: ✓ Unmodified
  
  NEXT STEPS
  ──────────
  [ ] IMS pending (scheduled for 11:00)
  [ ] Parcel sealed in evidence bag
  [ ] Awaiting FSL report
  
  PRINT MEMO
  ```

### Click "Print memo"
- **Browser generates** the seizure memo (see Scenario 2, Step 6).
- Memo is printed at the parcel office or control room.
- **Memo has:**
  - QR code linking to the hash verification (court can scan and verify).
  - Officer signature (biometric OTP).
  - All evidence attached (photos, video timestamp, sensor trace).

### Dashboard also shows **risk heatmap**
```
SEIZURES LAST 30 DAYS (by location)
──────────────────────────────────
Platform 1 entry gate:    ████████ 12 seizures (high)
Coach bay A1–A5 pit:      ███ 5 seizures (medium)
Parcel office:            ██ 3 seizures (medium)
Platform 2 entry gate:    █ 1 seizure (low)
Locomotive yard:          ██ 2 seizures (low)

RECOMMENDATION: Deploy QR-02 to Coach bay tomorrow night.
```

- Supervisor can **send the quadruped robot to high-risk zones** based on data.
- No guessing; evidence-driven patrols.

---

## SCENARIO 5: Weekly Model Update (Fleet Learning)

**Time: Friday 02:00 AM, RPF Data Center**

### Automated pipeline
1. **Collect field data (Mon–Thu):**
   - 1,200 handheld swabs + 150 robot swabs = 1,350 records.
   - Each record has: sensor trace, GPS, time, video thumbnail, signed hash.
   - Status: 1,300 negative, 50 positive (flagged).

2. **FSL reports arrive (by Friday 00:00):**
   - Last week's 50 positive alerts were tested by FSL.
   - 45 confirmed (cannabis 20, heroin 15, other drugs 10).
   - 5 false alarms (coffee, perfume, spice).

3. **Pair sensor traces with FSL results:**
   ```
   Sensor fingerprint              FSL result      Label
   ─────────────────────────────────────────────────────
   NO₂ 120 ppm @ 160°C, MQ-3 110   Cannabis        Positive
   NO₂ 95 ppm @ 155°C, MQ-3 88     Heroin          Positive
   NO₂ 10 ppm @ 180°C, MQ-3 8      False alarm     Negative
   ...
   [Total: 1,350 training examples]
   ```

4. **Retrain ML model:**
   ```bash
   python train.py \
     --data /home/rpf/training_data.csv \
     --model random_forest \
     --test_split 0.2 \
     --output model_2026_09_15.pkl
   ```
   - Result: accuracy 92% (up from 88% last week).
   - Confusion matrix: 5 false positives, 2 false negatives out of 45 tests.

5. **Sign and push update:**
   - New model is digitally signed (RPF private key).
   - Pushed to all 500 handheld + 50 robot devices via MQTT.
   - Devices verify the signature before installing (security).
   - **Old model stays active until new one verifies; rollback available.**

6. **Log the update:**
   ```
   Model v9 deployed, 14 Sep 2026, 02:30 AM
   Samples: 1,350 (45 positive, 1,305 negative)
   Accuracy: 92% (up from 88%)
   False positives: 5 (0.37%)
   False negatives: 2 (4.4%)
   Deployment status: 450/500 devices updated ✓
   ```

---

## SUMMARY: A Day in RPF Operations

| Time | Activity | Device | Result | Evidence |
|---|---|---|---|---|
| 08:00 | Gate patrol starts | Handheld #H-042 | 50 negative scans | 50 records, all signed |
| 08:23 | Heroin alert (2-route confirm) | Handheld #H-042 | Positive | Video, hash, memo |
| 10:07 | Parcel office positive | Handheld #H-039 | Escalated to IMS | Video, parcel photo, hash |
| 11:00 | IMS confirms heroin | FSL lab | Seizure logged | Memo filed with court evidence |
| 22:00 | Pit-line robot patrol | Quadruped #QR-01 | 4 negative, 1 alert | 5 records, thermal scans |
| 22:25 | Under-frame alert (A3) | Quadruped #QR-01 | Bomb squad called | Video, signed record, position |
| 02:00 (Friday) | Weekly model retraining | Server | 1,350 samples → 92% accuracy | New model deployed to fleet |

---

## What makes this different from manual operations

| Manual RPF method | RAIL-N.E.D. |
|---|---|
| Officer swabs, reads colour change by eye | Device reads electronically; officer taps a photo |
| Memo written by hand, no timestamps | Auto-filled memo with GPS, time, video, hash |
| Evidence scattered (photo on phone, swab in a bag, memo in a file) | Everything linked: one signed hash covers all |
| FSL report filed separately; no loop back to improve screening | FSL report becomes training label; model improves every week |
| No data on which zones have seizures | Dashboard heatmap shows high-risk areas; patrols deployed by data |
| Dogs fatigue; GPS-denied yards can't be patrolled at night | Robot works 24/7, needs no breaks, can go under power lines |

---

**This is how the system works in government hands.**

Every step is traceable, logged, and verifiable. A constable can catch a threat in 30 seconds. A judge can verify the evidence from a QR code.
