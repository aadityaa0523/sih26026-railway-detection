"""
AlertEngine: turns a classification into a physical alert decision.

zone_config carries the only knob that should ever change alert sensitivity -- a judge
asking "make the parcel office more sensitive than the platform" should be answerable by
handing this engine a different ZoneConfig, never by editing this file.
"""
from dataclasses import dataclass

from handheld.classifier import ClassificationResult


@dataclass(frozen=True)
class ZoneConfig:
    alert_threshold: float


@dataclass(frozen=True)
class AlertDecision:
    tier: str  # "clean" | "review" | "alert"
    outputs: tuple[str, ...]
    escalate: bool


class AlertEngine:
    def evaluate(self, classification: ClassificationResult, zone: ZoneConfig) -> AlertDecision:
        if classification.label == "clean":
            return AlertDecision(tier="clean", outputs=("led_green",), escalate=False)
        if not classification.is_unknown and classification.confidence >= zone.alert_threshold:
            return AlertDecision(tier="alert", outputs=("buzzer", "led_red", "vibration"), escalate=True)
        return AlertDecision(tier="review", outputs=("led_amber",), escalate=False)
