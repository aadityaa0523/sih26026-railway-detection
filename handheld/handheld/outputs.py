"""
AlertOutputs: drives the buzzer, vibration motor, and red/amber/green LEDs via gpiozero.

gpiozero abstracts the GPIO backend (RPi.GPIO on Pi 3B/4, lgpio on Pi 5) so this code doesn't
need to care which board it's on.

CRITICAL: this module must `import` cleanly on a non-Pi dev machine. gpiozero itself imports
fine without hardware, but constructing a Buzzer/LED/Motor without a real backend raises --
so the actual pin objects are created lazily in __init__, wrapped in try/except ImportError,
matching sensors.py's pattern.
"""

# BCM pin numbers -- change here if the wiring changes, never scattered through call sites.
PIN_BUZZER = 17
PIN_VIBRATION = 27
PIN_LED_RED = 22
PIN_LED_AMBER = 23
PIN_LED_GREEN = 24


class AlertOutputs:
    """`.fire(tier)` maps an AlertDecision tier straight to the physical outputs.

    Tier -> outputs, mirroring alerts.py's AlertDecision.outputs tuples:
      "clean"  -> ("led_green",)
      "review" -> ("led_amber",)
      "alert"  -> ("buzzer", "led_red", "vibration")
    """

    TIER_OUTPUTS = {
        "clean": ("led_green",),
        "review": ("led_amber",),
        "alert": ("buzzer", "led_red", "vibration"),
    }

    def __init__(self):
        try:
            from gpiozero import Buzzer, LED, Motor
        except ImportError as e:
            raise ImportError(
                "gpiozero is required for AlertOutputs (Pi only). Install with: "
                "pip install gpiozero rpi-lgpio. On a dev machine, main.py --simulate prints "
                "what would have fired instead of constructing this class."
            ) from e
        self._buzzer = Buzzer(PIN_BUZZER)
        self._vibration = Motor(PIN_VIBRATION)
        self._led_red = LED(PIN_LED_RED)
        self._led_amber = LED(PIN_LED_AMBER)
        self._led_green = LED(PIN_LED_GREEN)
        self._all_off()

    def _all_off(self):
        self._buzzer.off()
        self._vibration.stop()
        self._led_red.off()
        self._led_amber.off()
        self._led_green.off()

    def fire(self, tier: str) -> tuple[str, ...]:
        """Switches on the outputs for `tier` (all others off). Caller decides when to reset()
        -- e.g. after the next scan cycle -- so this method never blocks on a sleep.

        Returns the tuple of output names actually fired, so callers (main.py) can log it
        without recomputing the tier mapping.
        """
        outputs = self.TIER_OUTPUTS.get(tier, ())
        self._all_off()
        if "buzzer" in outputs:
            self._buzzer.on()
        if "vibration" in outputs:
            self._vibration.forward()
        if "led_red" in outputs:
            self._led_red.on()
        if "led_amber" in outputs:
            self._led_amber.on()
        if "led_green" in outputs:
            self._led_green.on()
        return outputs

    def reset(self):
        self._all_off()
