"""Lightweight price extraction helpers for monitor price scanning."""

import logging

logger = logging.getLogger(__name__)


def extract_skyscanner_price(itinerary: dict) -> dict | None:
    """Extract price info from a Skyscanner itinerary.

    Skyscanner returns price.raw in actual currency units.
    """
    try:
        price_info = itinerary.get("price", {})
        raw_price = price_info.get("raw")
        if raw_price is None or raw_price <= 0:
            return None

        legs = itinerary.get("legs", [])
        first_leg = legs[0] if legs else {}
        carriers = first_leg.get("carriers", {}).get("marketing", [])
        airline = carriers[0].get("alternateId") if carriers else None
        stop_count = first_leg.get("stopCount", 0)
        departure = first_leg.get("departure", "")[:10]

        return {
            "price": float(raw_price),
            "currency": price_info.get("currency", "TWD"),
            "airline": airline,
            "stops": stop_count,
            "departure_date": departure,
        }
    except (IndexError, KeyError, TypeError, ValueError):
        logger.debug("Failed to extract Skyscanner price", exc_info=True)
        return None


def extract_kiwi_price(itinerary: dict) -> dict | None:
    """Extract price info from a Kiwi itinerary.

    Kiwi returns price.raw in actual currency units.
    """
    try:
        price_info = itinerary.get("price", {})
        raw_price = price_info.get("raw")
        if raw_price is None or raw_price <= 0:
            return None

        legs = itinerary.get("legs", [])
        first_leg = legs[0] if legs else {}
        carriers = first_leg.get("carriers", {}).get("marketing", [])
        airline = carriers[0].get("alternateId") if carriers else None
        stop_count = first_leg.get("stopCount", 0)
        departure = first_leg.get("departure", "")[:10]

        return {
            "price": float(raw_price),
            "currency": price_info.get("currency", "TWD"),
            "airline": airline,
            "stops": stop_count,
            "departure_date": departure,
        }
    except (IndexError, KeyError, TypeError, ValueError):
        logger.debug("Failed to extract Kiwi price", exc_info=True)
        return None
