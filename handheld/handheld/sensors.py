"""
Hardware readers: 3x MQ gas sensors via an MCP3008 SPI ADC, plus a Bosch BME688 over I2C.

Pi GPIO has no analog input, so the MQ sensors (analog output) go through an MCP3008.
The BME688 is digital (I2C) and needs no ADC channel.

CRITICAL: this module must `import` cleanly on a non-Pi dev machine (Windows/Mac/CI) even
when spidev/smbus2 are not installed. All hardware-library imports happen lazily, inside
__init__, wrapped in try/except ImportError -- so `import handheld.sensors` never fails,
only *using* a reader off-Pi does.
"""


class AdcReader:
    """Reads the 3 MQ sensor channels (MQ-135, MQ-3, MQ-2) via an MCP3008 over SPI.

    MCP3008 is a 10-bit ADC (0-1023) read over spidev's raw xfer protocol -- there's no
    higher-level library needed for 3 single-ended channels, spidev is the standard choice
    on Pi 3B/4.
    """

    MQ135_CHANNEL = 0
    MQ3_CHANNEL = 1
    MQ2_CHANNEL = 2
    VREF = 3.3

    def __init__(self, bus: int = 0, device: int = 0, max_speed_hz: int = 1_350_000):
        try:
            import spidev
        except ImportError as e:
            raise ImportError(
                "spidev is required for AdcReader (Pi only). Install with: pip install spidev. "
                "On a dev machine, use `main.py --simulate` instead of a real AdcReader."
            ) from e
        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._spi.max_speed_hz = max_speed_hz

    def _read_channel(self, channel: int) -> int:
        # MCP3008 single-ended read protocol: start bit, single/diff bit, channel select.
        cmd = [1, (8 + channel) << 4, 0]
        _, high, low = self._spi.xfer2(cmd)
        return ((high & 3) << 8) | low

    def _to_voltage(self, raw: int) -> float:
        return raw / 1023 * self.VREF

    def read(self) -> dict[str, float]:
        """Returns the three MQ channel voltages, keyed to match Calibrator's reading dict."""
        return {
            "mq135": self._to_voltage(self._read_channel(self.MQ135_CHANNEL)),
            "mq3": self._to_voltage(self._read_channel(self.MQ3_CHANNEL)),
            "mq2": self._to_voltage(self._read_channel(self.MQ2_CHANNEL)),
        }

    def close(self):
        self._spi.close()


class Bme688Reader:
    """Reads the Bosch BME688 (temp/humidity/pressure/gas-resistance) over I2C.

    Chose `adafruit-circuitpython-bme680` over raw smbus2: the BME688 needs Bosch's
    temp/pressure/humidity compensation formulas (calibration coefficients baked into each
    chip) to turn raw registers into real units -- reimplementing that over smbus2 is exactly
    the kind of wheel a hackathon shouldn't reinvent. The adafruit driver is BME680-native
    and register-compatible with the BME688 for these fields, and it's the best-supported
    Pi library for this sensor.
    """

    def __init__(self, i2c_address: int = 0x77):
        try:
            import board
            import busio
            import adafruit_bme680
        except ImportError as e:
            raise ImportError(
                "adafruit-circuitpython-bme680 (+ board/busio) is required for Bme688Reader "
                "(Pi only). Install with: pip install adafruit-circuitpython-bme680. "
                "On a dev machine, use `main.py --simulate` instead of a real Bme688Reader."
            ) from e
        i2c = busio.I2C(board.SCL, board.SDA)
        self._sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=i2c_address)

    def read(self) -> dict[str, float]:
        """Returns gas resistance (ohms) plus the environmental fields used to compensate it."""
        return {
            "gas_resistance": self._sensor.gas,
            "temperature": self._sensor.temperature,
            "humidity": self._sensor.humidity,
            "pressure": self._sensor.pressure,
        }
