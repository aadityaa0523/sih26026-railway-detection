# Handheld demo: dummy heat swab (simulated)

The demo shows the whole flow **sniff -> heat swab -> two-route decision -> alert -> log**.
The sensor side is **simulated**: no gas sensor, heater or chemistry is involved. The "swab" is a
**prop**. The device replays a scripted heat curve for whichever pad you pick. Say this out loud;
the banner and result lines also say SIMULATED.

## Run it
```
cd handheld
pip install -r requirements.txt
python -m handheld.demo_flow            # asks which pad (1-4)
python -m handheld.demo_flow --pad 3    # skip the question
python -m handheld.demo_flow --pad 3 --fast   # no animation delay
python -m handheld.demo_flow --hardware # also drives the real LEDs + buzzer on a Pi (sensors stay simulated)
```
Also available: `python -m handheld.swab_demo --all --sniff alert` (table of all samples) and
`python -m handheld.swab_demo --sample nitro_standin --plot heat.png` (curve stamped SIMULATED).

## The four pads
| Pad | Say it is | What the screen shows |
|---|---|---|
| 1 | Clean swab of an empty bag | Both routes clear -> **CLEAN** (green LED) |
| 2 | A bag with sanitiser / perfume on it | Vapour screen flags, heat curve shows no nitro signature -> **REVIEW**, one route only (amber) |
| 3 | The legal stand-in: a dried nail-polish dab | Vapour flags **and** a heat peak near 185 C -> **ALERT**, two routes agree (red LED, buzzer, vibration) |
| 4 | Something unfamiliar | Heat responds but not the nitro signature -> **REVIEW**, goes to a human, no false alarm |

## Make the dummy swab prop (cheap, 10 minutes)
- 4 swabs: a small pad of **glass-fibre filter paper or felt** clipped on a short stick (a pen cap or
  skewer), each with a **number tag** 1-4 (coloured heat-shrink or tape).
- Optional theatre: a trace of **dried** nail polish on pad 3 and a drop of sanitiser on pad 2.
  It has no effect on the readings (they are scripted); it only makes the demo feel real.
  Keep wet polish and any heating away from the props; nothing is heated in this demo.
- A small closed bag or pouch to "wipe" in front of the judges.
- Never use real explosives or narcotics, ever.

## What to do on stage (about 2 minutes)
1. "This is a simulated demo of our flow; the heat sensor is the part we are still building."
2. Wipe the bag with **pad 1**, insert it, run `--pad 1` -> green, "no alert".
3. **Pad 2** -> amber. "One route alone never raises an alert. It goes to review."
4. **Pad 3** -> watch the temperature climb, the peak near 185 C, then red + buzzer.
   "Alert only fires because two independent routes agree."
5. Show the record line: "Every alert is logged, signed (simulated here) and synced to the control room."
6. Open `dashboard/index.html` -> Alert Register for the same story at station level.
7. Close with: "Every positive still goes to FSL / IMS for confirmation."

## If a judge asks
- *Is the sensor real?* "No. The curve is scripted; the bench test on the real chamber is our next step."
- *Does it detect RDX?* "Not claimed. We detect a nitro/nitrate **class** signature from a legal stand-in."
- *Accuracy?* "None claimed. The vapour model was trained on synthetic data."

## Swapping in the real sensor later
`handheld/heat.py` has `SimulatedHeatBackend` and `HardwareHeatBackend(read_no2=...)`. Pass your NO2
(or stand-in) sensor reading function and the same flow runs on real data. The hardware backend is untested.
