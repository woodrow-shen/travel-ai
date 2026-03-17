"""Normalize flight and hotel data from multiple sources into a common format."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _skyscanner_datetime(dt: dict) -> str:
    """Convert Skyscanner datetime object {year, month, day, hour, minute, second} to ISO 8601."""
    return (
        f"{dt['year']:04d}-{dt['month']:02d}-{dt['day']:02d}"
        f"T{dt['hour']:02d}:{dt['minute']:02d}:{dt['second']:02d}"
    )


def normalize_skyscanner_flight(
    itinerary: dict,
    currency: str = "TWD",
    origin: str = "",
    destination: str = "",
) -> dict:
    """Normalize a Skyscanner itinerary into the common flight format.

    Args:
        origin: IATA code of the origin airport (e.g. "TPE"). Passed by caller
            because Skyscanner response only contains numeric placeIds.
        destination: IATA code of the destination airport (e.g. "NRT").
    """
    price_raw = itinerary.get("price", {}).get("raw", 0)
    price = int(price_raw) / 1000  # milli-units to actual value

    legs = itinerary.get("legs", [])
    first_leg = legs[0] if legs else {}
    segments = first_leg.get("segments", [])
    first_segment = segments[0] if segments else {}

    carrier_marketing = first_segment.get("carriers", {}).get("marketing", {})
    airline_iata = carrier_marketing.get("iata", "")
    flight_number = f"{airline_iata}{first_segment.get('marketingFlightNumber', '')}"

    departure_dt = first_leg.get("departureDateTime", {})
    arrival_dt = first_leg.get("arrivalDateTime", {})

    pricing_options = itinerary.get("pricingOptions", [])
    booking_url = ""
    if pricing_options:
        items = pricing_options[0].get("items", [])
        if items:
            booking_url = items[0].get("deepLink", "")

    normalized_segments = []
    for idx, seg in enumerate(segments):
        seg_carrier = seg.get("carriers", {}).get("marketing", {})
        seg_origin = origin if idx == 0 else ""
        seg_dest = destination if idx == len(segments) - 1 else ""
        normalized_segments.append({
            "airline": seg_carrier.get("iata", ""),
            "airline_name": seg_carrier.get("name", ""),
            "flight_number": f"{seg_carrier.get('iata', '')}{seg.get('marketingFlightNumber', '')}",
            "origin": seg_origin,
            "destination": seg_dest,
            "departure_time": _skyscanner_datetime(seg["departureDateTime"])
            if "departureDateTime" in seg
            else "",
            "arrival_time": _skyscanner_datetime(seg["arrivalDateTime"])
            if "arrivalDateTime" in seg
            else "",
            "duration_minutes": seg.get("durationInMinutes", 0),
        })

    # Return leg (roundtrip): legs[1] if present
    return_segments = []
    if len(legs) > 1:
        return_leg = legs[1]
        return_segs = return_leg.get("segments", [])
        for idx, seg in enumerate(return_segs):
            seg_carrier = seg.get("carriers", {}).get("marketing", {})
            seg_origin = destination if idx == 0 else ""
            seg_dest = origin if idx == len(return_segs) - 1 else ""
            return_segments.append({
                "airline": seg_carrier.get("iata", ""),
                "airline_name": seg_carrier.get("name", ""),
                "flight_number": (
                    f"{seg_carrier.get('iata', '')}"
                    f"{seg.get('marketingFlightNumber', '')}"
                ),
                "origin": seg_origin,
                "destination": seg_dest,
                "departure_time": _skyscanner_datetime(seg["departureDateTime"])
                if "departureDateTime" in seg
                else "",
                "arrival_time": _skyscanner_datetime(seg["arrivalDateTime"])
                if "arrivalDateTime" in seg
                else "",
                "duration_minutes": seg.get("durationInMinutes", 0),
            })

    return {
        "source": "skyscanner",
        "price": price,
        "currency": currency,
        "airline": airline_iata,
        "airline_name": carrier_marketing.get("name", ""),
        "flight_number": flight_number,
        "origin": origin,
        "destination": destination,
        "departure_time": _skyscanner_datetime(departure_dt) if departure_dt else "",
        "arrival_time": _skyscanner_datetime(arrival_dt) if arrival_dt else "",
        "duration_minutes": first_leg.get("durationInMinutes", 0),
        "stops": first_leg.get("stopCount", 0),
        "segments": normalized_segments,
        "return_segments": return_segments,
        "booking_url": booking_url,
    }


def normalize_kiwi_flight(itinerary: dict, currency: str = "TWD") -> dict:
    """Normalize a Kiwi itinerary into the common flight format."""
    price = int(itinerary.get("price", {}).get("amount", "0"))

    sector = itinerary.get("sector", {})
    duration_seconds = sector.get("duration", 0)
    duration_minutes = duration_seconds // 60

    sector_segments = sector.get("sectorSegments", [])
    first_seg_wrapper = sector_segments[0] if sector_segments else {}
    first_segment = first_seg_wrapper.get("segment", {})

    carrier = first_segment.get("carrier", {})
    airline_code = carrier.get("code", "")
    flight_number = f"{airline_code}{first_segment.get('code', '')}"

    source_info = first_segment.get("source", {})
    dest_info = first_segment.get("destination", {})
    origin_code = source_info.get("station", {}).get("code", "")
    dest_code = dest_info.get("station", {}).get("code", "")

    booking_options = itinerary.get("bookingOptions", [])
    booking_url = ""
    if booking_options:
        edges = booking_options[0].get("edges", [])
        if edges:
            booking_url = edges[0].get("node", {}).get("bookingUrl", "")

    normalized_segments = []
    for seg_wrapper in sector_segments:
        seg = seg_wrapper.get("segment", {})
        seg_carrier = seg.get("carrier", {})
        seg_source = seg.get("source", {})
        seg_dest = seg.get("destination", {})
        normalized_segments.append({
            "airline": seg_carrier.get("code", ""),
            "airline_name": seg_carrier.get("name", ""),
            "flight_number": f"{seg_carrier.get('code', '')}{seg.get('code', '')}",
            "origin": seg_source.get("station", {}).get("code", ""),
            "destination": seg_dest.get("station", {}).get("code", ""),
            "departure_time": seg_source.get("localTime", ""),
            "arrival_time": seg_dest.get("localTime", ""),
            "duration_minutes": seg.get("duration", 0) // 60,
        })

    return {
        "source": "kiwi",
        "price": price,
        "currency": currency,
        "airline": airline_code,
        "airline_name": carrier.get("name", ""),
        "flight_number": flight_number,
        "origin": origin_code,
        "destination": dest_code,
        "departure_time": source_info.get("localTime", ""),
        "arrival_time": dest_info.get("localTime", ""),
        "duration_minutes": duration_minutes,
        "stops": len(sector_segments) - 1,
        "segments": normalized_segments,
        "return_segments": [],  # TODO: parse return leg once Kiwi response structure is verified
        "booking_url": booking_url,
        "bags_info": itinerary.get("bagsInfo"),
        "is_virtual_interlining": itinerary.get("pnrCount", 1) > 1,
    }


def normalize_amadeus_flight(
    offer: dict,
    currency: str = "TWD",
    exchange_rates: dict[str, float] | None = None,
) -> dict:
    """Normalize an Amadeus flight offer into the common flight format.

    If *exchange_rates* is provided and the Amadeus price currency differs from
    *currency*, the price is converted using the given rates.
    """
    from app.lib.currency import convert_price

    price_data = offer.get("price", {})
    price = float(price_data.get("total", "0"))
    actual_currency = price_data.get("currency", currency)

    # Convert currency if rates available and currencies differ
    if exchange_rates and actual_currency != currency:
        price, actual_currency = convert_price(price, actual_currency, currency, exchange_rates)

    itineraries = offer.get("itineraries", [])
    first_itin = itineraries[0] if itineraries else {}
    segments = first_itin.get("segments", [])
    first_segment = segments[0] if segments else {}

    airline = first_segment.get("carrierCode", "")
    flight_number = f"{airline}{first_segment.get('number', '')}"

    # Parse duration like "PT5H30M" into minutes
    duration_str = first_itin.get("duration", "")
    duration_minutes = _parse_iso_duration(duration_str)

    normalized_segments = []
    for seg in segments:
        seg_duration = _parse_iso_duration(seg.get("duration", ""))
        normalized_segments.append({
            "airline": seg.get("carrierCode", ""),
            "airline_name": "",
            "flight_number": f"{seg.get('carrierCode', '')}{seg.get('number', '')}",
            "origin": seg.get("departure", {}).get("iataCode", ""),
            "destination": seg.get("arrival", {}).get("iataCode", ""),
            "departure_time": seg.get("departure", {}).get("at", ""),
            "arrival_time": seg.get("arrival", {}).get("at", ""),
            "duration_minutes": seg_duration,
        })

    # Return leg (roundtrip): itineraries[1] if present
    return_segments = []
    if len(itineraries) > 1:
        return_itin = itineraries[1]
        for seg in return_itin.get("segments", []):
            seg_duration = _parse_iso_duration(seg.get("duration", ""))
            return_segments.append({
                "airline": seg.get("carrierCode", ""),
                "airline_name": "",
                "flight_number": f"{seg.get('carrierCode', '')}{seg.get('number', '')}",
                "origin": seg.get("departure", {}).get("iataCode", ""),
                "destination": seg.get("arrival", {}).get("iataCode", ""),
                "departure_time": seg.get("departure", {}).get("at", ""),
                "arrival_time": seg.get("arrival", {}).get("at", ""),
                "duration_minutes": seg_duration,
            })

    return {
        "source": "amadeus",
        "price": price,
        "currency": actual_currency,
        "airline": airline,
        "airline_name": "",
        "flight_number": flight_number,
        "origin": first_segment.get("departure", {}).get("iataCode", ""),
        "destination": first_segment.get("arrival", {}).get("iataCode", ""),
        "departure_time": first_segment.get("departure", {}).get("at", ""),
        "arrival_time": first_segment.get("arrival", {}).get("at", ""),
        "duration_minutes": duration_minutes,
        "stops": len(segments) - 1,
        "segments": normalized_segments,
        "return_segments": return_segments,
        "booking_url": "",
    }


def normalize_google_flights_flight(
    itinerary: dict,
    currency: str = "TWD",
) -> dict:
    """Normalize a Google Flights Data itinerary into the common flight format.

    Google Flights Data API (``google-flights-data.p.rapidapi.com``) returns
    flat flight objects with ``airlineCode``, ``departureAirport`` (IATA code),
    ``segments[]`` with ``departureAirportCode``, ``flightNumber``, etc.
    """
    price = itinerary.get("price", 0) or 0

    airline_code = itinerary.get("airlineCode", "")
    airline_name = itinerary.get("airlineName", "")
    origin = itinerary.get("departureAirport", "")
    destination = itinerary.get("arrivalAirport", "")
    total_duration = itinerary.get("durationMinutes", 0)
    stops = itinerary.get("stops", 0)

    segments_raw = itinerary.get("segments", [])
    first_seg = segments_raw[0] if segments_raw else {}

    # Build flight_number: airlineCode + first segment flightNumber
    first_flight_num = first_seg.get("flightNumber", "")
    flight_number = f"{airline_code}{first_flight_num}" if first_flight_num else ""

    # Build departure/arrival datetime from date + time
    dep_date = itinerary.get("departureDate", "")
    dep_time = itinerary.get("departureTime", "")
    arr_date = itinerary.get("arrivalDate", "")
    arr_time = itinerary.get("arrivalTime", "")
    departure_dt = f"{dep_date}T{dep_time}" if dep_date and dep_time else ""
    arrival_dt = f"{arr_date}T{arr_time}" if arr_date and arr_time else ""

    normalized_segments = []
    for seg in segments_raw:
        seg_dep_date = seg.get("departureDate", "")
        seg_dep_time = seg.get("departureTime", "")
        seg_arr_date = seg.get("arrivalDate", "")
        seg_arr_time = seg.get("arrivalTime", "")
        seg_code = seg.get("airlineCode", "")
        seg_num = seg.get("flightNumber", "")
        normalized_segments.append({
            "airline": seg_code,
            "airline_name": seg.get("airlineName", ""),
            "flight_number": f"{seg_code}{seg_num}" if seg_num else "",
            "origin": seg.get("departureAirportCode", ""),
            "destination": seg.get("arrivalAirportCode", ""),
            "departure_time": f"{seg_dep_date}T{seg_dep_time}"
            if seg_dep_date and seg_dep_time
            else "",
            "arrival_time": f"{seg_arr_date}T{seg_arr_time}"
            if seg_arr_date and seg_arr_time
            else "",
            "duration_minutes": seg.get("duration", 0),
        })

    return {
        "source": "google_flights",
        "price": price,
        "currency": currency,
        "airline": airline_code,
        "airline_name": airline_name,
        "flight_number": flight_number,
        "origin": origin,
        "destination": destination,
        "departure_time": departure_dt,
        "arrival_time": arrival_dt,
        "duration_minutes": total_duration,
        "stops": stops,
        "segments": normalized_segments,
        "return_segments": [],
        "booking_url": "",
        "booking_token": itinerary.get("bookingToken", ""),
    }


def _parse_iso_duration(duration: str) -> int:
    """Parse ISO 8601 duration (e.g. 'PT5H30M') into minutes."""
    if not duration or not duration.startswith("PT"):
        return 0
    rest = duration[2:]
    hours = 0
    minutes = 0
    if "H" in rest:
        h_part, rest = rest.split("H", 1)
        hours = int(h_part)
    if "M" in rest:
        m_part, _ = rest.split("M", 1)
        minutes = int(m_part)
    return hours * 60 + minutes


def deduplicate_flights(flights: list[dict]) -> list[dict]:
    """Remove duplicate flights keeping the lowest price per flight_number+departure_time."""
    seen: dict[str, dict] = {}
    for flight in flights:
        key = f"{flight['flight_number']}_{flight['departure_time']}"
        if key not in seen or flight["price"] < seen[key]["price"]:
            seen[key] = flight
    return list(seen.values())


# ---------------------------------------------------------------------------
# Hotel normalizers
# ---------------------------------------------------------------------------


def normalize_skyscanner_hotel(
    hotel: dict,
    currency: str = "TWD",
    checkin: str = "",
    checkout: str = "",
) -> dict:
    """Normalize a Skyscanner hotel card into the common hotel format.

    Skyscanner hotel search returns ``data.hotels`` where each hotel has
    fields like ``name``, ``stars``, ``reviewsSummary``, ``lowestPrice``,
    ``coordinates``, ``images`` etc.  The exact shape depends on the
    ``hotelCards`` variant the API returns.
    """
    name = hotel.get("name", "")
    stars = hotel.get("stars", 0) or 0

    reviews = hotel.get("reviewsSummary", {})
    user_rating = reviews.get("score")
    if user_rating is not None:
        user_rating = float(user_rating)
    review_count = reviews.get("total")
    if review_count is not None:
        review_count = int(review_count)

    price_raw = hotel.get("lowestPrice", hotel.get("price", ""))
    price_per_night = _parse_price_string(price_raw)

    # Calculate total from nights
    nights = _count_nights(checkin, checkout)
    total_price = price_per_night * nights if nights else price_per_night

    coords = hotel.get("coordinates", {})
    lat = coords.get("lat") or coords.get("latitude")
    lng = coords.get("lng") or coords.get("longitude")

    images_raw = hotel.get("images", [])
    images = []
    for img in images_raw[:5]:
        if isinstance(img, str):
            images.append(img)
        elif isinstance(img, dict):
            images.append(img.get("url") or img.get("thumbnail") or "")

    return {
        "source": "skyscanner",
        "name": name,
        "address": hotel.get("location", hotel.get("address", "")),
        "latitude": float(lat) if lat else None,
        "longitude": float(lng) if lng else None,
        "star_rating": int(stars),
        "user_rating": user_rating,
        "review_count": review_count,
        "price_per_night": price_per_night,
        "total_price": total_price,
        "currency": currency,
        "amenities": [],
        "images": images,
        "booking_url": hotel.get("deepLink", hotel.get("url", "")),
        "cancellation_policy": hotel.get("cancellation"),
    }


def normalize_kiwi_hotel(
    hotel: dict,
    currency: str = "TWD",
    checkin: str = "",
    checkout: str = "",
) -> dict:
    """Normalize a Kiwi stays result into the common hotel format.

    Kiwi ``stays/search/by-dest`` returns ``data.hotels`` where each hotel
    has ``hotel_name``, ``address``, ``review_score``, ``review_nr``,
    ``price_breakdown``, ``main_photo_url``, ``class`` (star rating),
    ``hotel_facilities`` etc.
    """
    name = hotel.get("hotel_name", hotel.get("name", ""))
    stars = hotel.get("class", 0) or 0

    review_score = hotel.get("review_score")
    if review_score is not None:
        review_score = float(review_score)
    review_count = hotel.get("review_nr")
    if review_count is not None:
        review_count = int(review_count)

    price_breakdown = hotel.get("price_breakdown", {})
    gross_price = price_breakdown.get("gross_price", 0) or 0
    total_price = float(gross_price)

    nights = _count_nights(checkin, checkout)
    price_per_night = total_price / nights if nights else total_price

    lat = hotel.get("latitude")
    lng = hotel.get("longitude")

    photo = hotel.get("main_photo_url", "")
    images = [photo] if photo else []

    facilities = hotel.get("hotel_facilities", "")
    amenities = []
    if isinstance(facilities, str) and facilities:
        amenities = [f.strip() for f in facilities.split(",") if f.strip()]
    elif isinstance(facilities, list):
        amenities = facilities

    return {
        "source": "kiwi",
        "name": name,
        "address": hotel.get("address", ""),
        "latitude": float(lat) if lat else None,
        "longitude": float(lng) if lng else None,
        "star_rating": int(stars),
        "user_rating": review_score,
        "review_count": review_count,
        "price_per_night": round(price_per_night, 2),
        "total_price": total_price,
        "currency": currency,
        "amenities": amenities[:10],
        "images": images,
        "booking_url": hotel.get("url", ""),
        "cancellation_policy": hotel.get("is_free_cancellable")
        and "Free cancellation"
        or None,
    }


def deduplicate_hotels(hotels: list[dict]) -> list[dict]:
    """Remove duplicate hotels keeping the lowest price per name+city."""
    seen: dict[str, dict] = {}
    for hotel in hotels:
        key = hotel.get("name", "").lower().strip()
        if not key:
            continue
        if key not in seen or hotel.get("price_per_night", 0) < seen[key].get(
            "price_per_night", 0
        ):
            seen[key] = hotel
    return list(seen.values())


def _parse_price_string(raw: object) -> float:
    """Extract numeric price from string like '$120' or '120.50' or int."""
    if isinstance(raw, (int, float)):
        return float(raw)
    if not isinstance(raw, str) or not raw:
        return 0.0
    cleaned = "".join(c for c in raw if c.isdigit() or c == ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _count_nights(checkin: str, checkout: str) -> int:
    """Count nights between checkin/checkout date strings (YYYY-MM-DD)."""
    if not checkin or not checkout:
        return 1
    try:
        from datetime import date as date_type

        ci = date_type.fromisoformat(checkin)
        co = date_type.fromisoformat(checkout)
        delta = (co - ci).days
        return max(delta, 1)
    except ValueError:
        return 1
