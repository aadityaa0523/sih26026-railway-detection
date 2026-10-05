"""
K-type thermocouple via a MAX6675 module on SPI.

Wiring (Raspberry Pi Zero 2 W, SPI0, shares the bus with the MCP3008 which uses CE0):
    MAX6675 VCC -> 3V3 (pin 1)        MAX6675 SO  -> GPIO9  / MISO (pin 21)
    MAX6675 GND -> GND (pin 6)        MAX6675 SCK -> GPIO11 / SCLK (pin 23)
                                      MAX6675 CS  -> GPIO7  / CE1  (pin 26)
Thermocouple into the module's screw terminal: yellow lead to "+", red lead to "-" (ANSI colours;
if the reading falls when warmed, swap them). Enable SPI first: `sudo raspi-config` -> Interfaces -> SPI.

Test it:   python -m handheld.thermocouple            (prints a reading each second; Ctrl+C to stop)
Off the Pi: python -m handheld.thermocouple --simulate
"""
import argparse
import math
import time


def max6675_decode(hi: int, lo: int) -> float:
    """Two bytes from the MAX6675 -> degrees C. Raises RuntimeError if the thermocouple is not connected."""
    raw = (hi << 8) | lo
    if raw & 0x4:
        raise RuntimeError("thermocouple open circuit (not connected, or a loose terminal)")
    return (raw >> 3) * 0.25


class Max6675:
    def __init__(self, bus: int = 0, device: int = 1):
        try:
            import spidev
        except ImportError as e:
            raise ImportError("spidev is required (Pi only): pip install spidev") from e
        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._spi.max_speed_hz = 4_000_000

    def read_c(self) -> float:
        hi, lo = self._spi.readbytes(2)
        return max6675_decode(hi, lo)

    def close(self):
        self._spi.close()


def main():
    ap = argparse.ArgumentParser(description="Print K-type thermocouple readings (MAX6675)")
    ap.add_argument("--simulate", action="store_true", help="fake readings, no hardware")
    ap.add_argument("--bus", type=int, default=0)
    ap.add_argument("--device", type=int, default=1, help="SPI chip-select: 1 = CE1 (GPIO7)")
    a = ap.parse_args()
    sensor = None if a.simulate else Max6675(a.bus, a.device)
    print("Reading every 1 s. Pinch the tip, or dip it in warm water, and watch the value rise. Ctrl+C to stop.")
    t0 = time.time()
    try:
        while True:
            try:
                t = 26 + 6 * math.sin((time.time() - t0) / 4) if sensor is None else sensor.read_c()
                print(f"{t:6.2f} C" + ("   (SIMULATED)" if sensor is None else ""))
            except RuntimeError as e:
                print("ERROR:", e)
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
