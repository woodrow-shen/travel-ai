import logging
from dataclasses import dataclass
from statistics import mean, stdev

logger = logging.getLogger(__name__)


@dataclass
class BugFareAlert:
    origin: str
    destination: str
    current_price: float
    average_price: float
    currency: str
    confidence: str  # "high" or "medium"
    source: str


def detect_anomaly(
    origin: str,
    destination: str,
    current_price: float,
    currency: str,
    history: list[float],
    source: str,
    other_source_price: float | None = None,
) -> BugFareAlert | None:
    if len(history) < 5:
        return None

    avg = mean(history)
    if avg == 0:
        return None

    confidence = None

    # Condition 1: Price below 50% of average
    if current_price < avg * 0.5:
        confidence = "high"
    # Condition 2: Price below 2 standard deviations
    elif len(history) >= 10:
        sd = stdev(history)
        if sd > 0 and current_price < avg - 2 * sd:
            confidence = "medium"

    if confidence is None:
        return None

    # Condition 3: Only one source shows low price -> more likely bug fare
    if other_source_price and other_source_price > avg * 0.7:
        confidence = "high"

    return BugFareAlert(
        origin=origin,
        destination=destination,
        current_price=current_price,
        average_price=avg,
        currency=currency,
        confidence=confidence,
        source=source,
    )
