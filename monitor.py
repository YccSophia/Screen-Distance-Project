"""Screen-distance monitoring logic; distances are in centimeters."""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Reading:
    distance_cm: float
    state: str


def classify(distance_cm: float) -> Reading:
    """Paper-derived demo thresholds, not clinical recommendations."""
    if not math.isfinite(distance_cm) or distance_cm <= 0:
        raise ValueError('Distance must be finite and greater than zero.')
    state = 'BLOCK' if distance_cm < 25 else 'WARN' if distance_cm <= 30 else 'NORMAL'
    return Reading(distance_cm, state)


def light_round_trip_seconds(distance_cm: float) -> float:
    """Ideal optical round-trip delay using the paper's c = 3e8 m/s."""
    classify(distance_cm)
    return 2 * (distance_cm / 100) / 300_000_000
