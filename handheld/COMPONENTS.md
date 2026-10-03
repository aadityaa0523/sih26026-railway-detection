# RAIL-N.E.D. handheld prototype: components list

Prices are indicative one-off Indian retail estimates (Rs). Verify every line before quoting
or ordering. Sources: `RAIL-N.E.D._FEASIBILITY_REPORT.md` section 4 and the corrections in
`SIH_PPT_SESSION_HANDOFF.md` (Pi Zero 2 W, MiCS-2714). Pins marked "code" are already in
`handheld/handheld/outputs.py` / `sensors.py`.

## 1. Compute and storage
| # | Part | Qty | Est. Rs | Note |
|---|---|---|---|---|
| 1 | Raspberry Pi Zero 2 W (get the **WH**, pre-soldered header) | 1 | 1,800 | Wi-Fi + BT; runs the existing Python code unchanged |
| 2 | microSD 32 GB, A1/A2 class | 1 | 400 | OS + SQLite event log |
| 3 | MCP3008 8-ch SPI ADC (DIP) | 1 | 300 | Pi has no analog input; code uses ch0 MQ-135, ch1 MQ-3, ch2 MQ-2. **ch3 = MiCS-2714 NO2 (new)** |

## 2. Sensors: SNIFF route
| # | Part | Qty | Est. Rs | Note |
|---|---|---|---|---|
| 4 | MQ-135, MQ-3, MQ-2 gas sensor modules | 3 | 450 | 5 V heaters, about 0.8 W each, so duty-cycle them |
| 5 | Bosch BME688 breakout (I2C 0x77) | 1 | 1,500 | gas + T/RH/P; code uses the adafruit_bme680 driver |
| 6 | 10k + 20k resistors for 3 dividers | 3 sets | 20 | **MQ analog outputs can reach 5 V; MCP3008 runs at 3.3 V.** Divide, and add a scale factor in `sensors.py` (it assumes a direct 3.3 V read today) |

## 3. HEAT chamber: the core innovation
| # | Part | Qty | Est. Rs | Note |
|---|---|---|---|---|
| 7 | SGX **MiCS-2714** NO2 sensor (breakout or SMD + carrier) | 1 | 1,000 | **Not MQ-131 (ozone).** Check datasheet for heater voltage and load resistor |
| 8 | Ceramic MCH heater, ~10 W, 5-12 V | 1 | 150 | Swab heated 50 -> 250 C |
| 9 | K-type thermocouple + MAX6675 module (SPI) | 1 | 300 | Closed-loop PID; use SPI CE1 |
| 10 | N-channel logic-level MOSFET (e.g. IRLZ44N) + flyback/gate resistors | 2 | 100 | One for heater PWM, one for pump |
| 11 | Small DC air micro-pump (3-5 V) | 1 | 400 | Draws air over the sensors |
| 12 | Machined / folded aluminium chamber, about 5 mL, with swab port | 1 | 300 | Small volume is what makes ppm-level NO2 readable |
| 13 | **Thermal fuse**, rated just above the 250 C operating point (confirm rating) | 1 | 100 | Hard safety cut-off in series with the heater; software cut-off at 260 C |
| 14 | PTFE or ceramic standoffs, PTFE-coated glass-fibre swab pads, aluminium tape | set | 200 | Thermal isolation from the printed shell; reusable swabs |

## 4. Alerts, display, location
| # | Part | Qty | Est. Rs | Note |
|---|---|---|---|---|
| 15 | Active buzzer 5 V | 1 | 40 | BCM 17 (code) |
| 16 | Vibration motor + driver transistor | 1 | 60 | BCM 27 (code) |
| 17 | LEDs red / amber / green + resistors | 3 | 50 | BCM 22 / 23 / 24 (code) |
| 18 | **1.3" ST7789 240x240 SPI colour display** (instead of 0.96" OLED) | 1 | 500 | Hindi / regional text is unreadable on a 128x64 OLED; testing plan HH-INT-004 needs it legible |
| 19 | MAX98357A I2S amp + 3 W 4 ohm speaker | 1 | 400 | Spoken alerts in Hindi / regional language |
| 20 | u-blox NEO-6M GPS module + antenna (UART) | 1 | 350 | Timestamp + location on every record |
| 21 | Momentary push buttons (scan, swab, mode) | 3 | 30 | Trigger a scan / swab cycle |

## 5. Security
| # | Part | Qty | Est. Rs | Note |
|---|---|---|---|---|
| 22 | Microchip ATECC608 breakout (I2C 0x60) | 1 | 150 | ECDSA P-256 signing, key never leaves the chip. Signed hash-linked log, **not blockchain** |

## 6. Power
| # | Part | Qty | Est. Rs | Note |
|---|---|---|---|---|
| 23 | 2S Li-ion pack, 2 x 18650 (2,000-2,500 mAh) + holder | 1 | 450 | About 15 Wh, 100+ swabs per charge |
| 24 | 2S BMS + USB-C charge module | 1 | 250 | Protection + charging |
| 25 | Buck converter, 7.4 V -> 5 V, 3 A | 1 | 200 | Heater peaks at about 2 A plus the Pi |
| 26 | Slide power switch, inline fuse, 1000 uF capacitor | set | 120 | Pump and heater switching noise |

## 7. Mechanical, wiring, consumables
| # | Part | Qty | Est. Rs | Note |
|---|---|---|---|---|
| 27 | 3D-printed enclosure (PETG), sniff nozzle, swab port cover | 1 | 500 | **PETG softens near 80 C**: keep the chamber thermally isolated (item 14), never touching the shell |
| 28 | Perfboard or custom PCB, JST connectors, wire, heat-shrink | set | 500 | |
| 29 | Dried nail polish (nitrocellulose) for the legal test stand-in | 1 | 100 | Never use real explosives or narcotics. Distractors: vinegar, coffee, chilli, diesel, attar, agarbatti ash, sanitiser |

**Total about Rs 10,700.** Your slide says about Rs 9,000 and the feasibility report says about
Rs 6,870. The report assumed an ESP32-S3, which was replaced by the Pi Zero 2 W. Single-unit
prototype prices run higher than volume pricing. Either update the slide figure or label it
"at scale".

## 8. Wiring summary
| Bus | Devices |
|---|---|
| SPI0 CE0 | MCP3008 (MQ-135, MQ-3, MQ-2, MiCS-2714) |
| SPI0 CE1 | MAX6675 thermocouple |
| SPI1 (aux) | ST7789 display |
| I2C (SDA/SCL) | BME688 (0x77), ATECC608 (0x60) |
| I2S | MAX98357A speaker amp |
| UART | NEO-6M GPS |
| GPIO | buzzer 17, vibration 27, LEDs 22/23/24, heater PWM + pump (MOSFETs, pins to be assigned), 3 buttons |

## 9. Still to write (software gaps vs the slide)
The code today covers SNIFF (MQ + BME688), classify, alert, hash-chained log and MQTT sync.
It has **no** HEAT driver (heater PID, MAX6675 read, MiCS-2714 channel, temperature-ramp
features), no two-route agreement rule, no ATECC608 signing, and no GPS / display / speaker
drivers.
