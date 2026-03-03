
from app.clients.normalizer import (
    _parse_iso_duration,
    _skyscanner_datetime,
    deduplicate_flights,
    normalize_amadeus_flight,
    normalize_kiwi_flight,
    normalize_skyscanner_flight,
)
from app.schemas.search import normalized_dict_to_flight_result

# --- Skyscanner Normalization ---


SKYSCANNER_ITINERARY = {
    "id": "itin-001",
    "price": {"formatted": "NT$7,121", "raw": "7121000", "unit": "PRICE_UNIT_MILLI"},
    "legs": [
        {
            "originPlaceId": "128667054",
            "destinationPlaceId": "128668889",
            "departureDateTime": {
                "year": 2026, "month": 4, "day": 1,
                "hour": 2, "minute": 40, "second": 0,
            },
            "arrivalDateTime": {
                "year": 2026, "month": 4, "day": 1,
                "hour": 10, "minute": 5, "second": 0,
            },
            "durationInMinutes": 385,
            "stopCount": 1,
            "segments": [
                {
                    "marketingFlightNumber": "752",
                    "durationInMinutes": 155,
                    "originPlaceId": "128667054",
                    "destinationPlaceId": "128667080",
                    "departureDateTime": {
                        "year": 2026, "month": 4, "day": 1,
                        "hour": 2, "minute": 40, "second": 0,
                    },
                    "arrivalDateTime": {
                        "year": 2026, "month": 4, "day": 1,
                        "hour": 6, "minute": 15, "second": 0,
                    },
                    "carriers": {
                        "marketing": {"name": "Jin Air", "iata": "LJ"},
                        "operating": {"name": "Jin Air", "iata": "LJ"},
                    },
                },
                {
                    "marketingFlightNumber": "201",
                    "durationInMinutes": 120,
                    "originPlaceId": "128667080",
                    "destinationPlaceId": "128668889",
                    "departureDateTime": {
                        "year": 2026, "month": 4, "day": 1,
                        "hour": 7, "minute": 30, "second": 0,
                    },
                    "arrivalDateTime": {
                        "year": 2026, "month": 4, "day": 1,
                        "hour": 10, "minute": 5, "second": 0,
                    },
                    "carriers": {
                        "marketing": {"name": "Jin Air", "iata": "LJ"},
                        "operating": {"name": "Jin Air", "iata": "LJ"},
                    },
                },
            ],
        }
    ],
    "pricingOptions": [
        {
            "price": {"formatted": "NT$7,142"},
            "items": [{"deepLink": "https://booking.example.com/flight1"}],
        }
    ],
}


def test_normalize_skyscanner_flight():
    result = normalize_skyscanner_flight(
        SKYSCANNER_ITINERARY, origin="TPE", destination="NRT"
    )

    assert result["source"] == "skyscanner"
    assert result["price"] == 7121.0  # 7121000 / 1000
    assert result["currency"] == "TWD"
    assert result["airline"] == "LJ"
    assert result["airline_name"] == "Jin Air"
    assert result["flight_number"] == "LJ752"
    assert result["origin"] == "TPE"
    assert result["destination"] == "NRT"
    assert result["departure_time"] == "2026-04-01T02:40:00"
    assert result["arrival_time"] == "2026-04-01T10:05:00"
    assert result["duration_minutes"] == 385
    assert result["stops"] == 1
    assert result["booking_url"] == "https://booking.example.com/flight1"
    assert len(result["segments"]) == 2
    assert result["segments"][0]["flight_number"] == "LJ752"
    assert result["segments"][0]["origin"] == "TPE"
    assert result["segments"][0]["destination"] == ""
    assert result["segments"][1]["flight_number"] == "LJ201"
    assert result["segments"][1]["origin"] == ""
    assert result["segments"][1]["destination"] == "NRT"


def test_skyscanner_datetime():
    dt = {"year": 2026, "month": 1, "day": 5, "hour": 9, "minute": 3, "second": 7}
    assert _skyscanner_datetime(dt) == "2026-01-05T09:03:07"


def test_normalize_skyscanner_flight_no_origin_destination():
    """When origin/destination not passed, they default to empty string."""
    result = normalize_skyscanner_flight(SKYSCANNER_ITINERARY)
    assert result["origin"] == ""
    assert result["destination"] == ""


def test_normalize_skyscanner_flight_no_pricing_options():
    itin = {**SKYSCANNER_ITINERARY, "pricingOptions": []}
    result = normalize_skyscanner_flight(itin, origin="TPE", destination="NRT")
    assert result["booking_url"] == ""


def test_normalize_skyscanner_flight_empty_legs():
    itin = {**SKYSCANNER_ITINERARY, "legs": []}
    result = normalize_skyscanner_flight(itin, origin="TPE", destination="NRT")
    assert result["airline"] == ""
    assert result["segments"] == []
    assert result["origin"] == "TPE"
    assert result["destination"] == "NRT"


# --- Kiwi Normalization ---


KIWI_ITINERARY = {
    "id": "kiwi-itin-001",
    "price": {"amount": "6790", "priceBeforeDiscount": "6790"},
    "duration": 21000,
    "sector": {
        "id": "sector-001",
        "duration": 21000,
        "sectorSegments": [
            {
                "segment": {
                    "source": {
                        "station": {
                            "code": "TPE", "name": "桃園機場",
                            "type": "AIRPORT",
                            "city": {"name": "台北"},
                            "country": {"code": "TW"},
                        },
                        "localTime": "2026-04-01T02:50:00",
                    },
                    "destination": {
                        "station": {
                            "code": "ICN", "name": "仁川機場",
                            "type": "AIRPORT",
                            "city": {"name": "首爾"},
                            "country": {"code": "KR"},
                        },
                        "localTime": "2026-04-01T06:15:00",
                    },
                    "duration": 8400,
                    "type": "FLIGHT",
                    "code": "6154",
                    "carrier": {"name": "Jeju Air", "code": "7C"},
                    "operatingCarrier": {"name": "Jeju Air", "code": "7C"},
                },
                "layover": {"duration": 4200},
            },
            {
                "segment": {
                    "source": {
                        "station": {"code": "ICN", "name": "仁川機場", "type": "AIRPORT"},
                        "localTime": "2026-04-01T07:25:00",
                    },
                    "destination": {
                        "station": {"code": "NRT", "name": "成田機場", "type": "AIRPORT"},
                        "localTime": "2026-04-01T10:15:00",
                    },
                    "duration": 6600,
                    "type": "FLIGHT",
                    "code": "901",
                    "carrier": {"name": "Korean Air", "code": "KE"},
                    "operatingCarrier": {"name": "Korean Air", "code": "KE"},
                },
                "layover": None,
            },
        ],
    },
    "pnrCount": 2,
    "bagsInfo": {"includedHandBag": True, "includedCheckedBag": False},
    "bookingOptions": [
        {
            "edges": [
                {
                    "node": {
                        "bookingUrl": "https://booking.kiwi.com/flight1",
                        "price": {"amount": "6790"},
                    }
                }
            ]
        }
    ],
}


def test_normalize_kiwi_flight():
    result = normalize_kiwi_flight(KIWI_ITINERARY)

    assert result["source"] == "kiwi"
    assert result["price"] == 6790
    assert result["currency"] == "TWD"
    assert result["airline"] == "7C"
    assert result["airline_name"] == "Jeju Air"
    assert result["flight_number"] == "7C6154"
    assert result["origin"] == "TPE"
    assert result["destination"] == "ICN"  # First segment destination
    assert result["departure_time"] == "2026-04-01T02:50:00"
    assert result["arrival_time"] == "2026-04-01T06:15:00"
    assert result["duration_minutes"] == 350  # 21000 / 60
    assert result["stops"] == 1  # 2 segments - 1
    assert result["booking_url"] == "https://booking.kiwi.com/flight1"
    assert result["bags_info"] == {"includedHandBag": True, "includedCheckedBag": False}
    assert result["is_virtual_interlining"] is True  # pnrCount=2
    assert len(result["segments"]) == 2
    assert result["segments"][0]["flight_number"] == "7C6154"
    assert result["segments"][0]["duration_minutes"] == 140  # 8400 / 60
    assert result["segments"][1]["flight_number"] == "KE901"
    assert result["segments"][1]["duration_minutes"] == 110  # 6600 / 60


def test_normalize_kiwi_flight_single_segment():
    """Single-segment flight should have 0 stops."""
    itin = {
        **KIWI_ITINERARY,
        "sector": {
            "duration": 8400,
            "sectorSegments": [KIWI_ITINERARY["sector"]["sectorSegments"][0]],
        },
        "pnrCount": 1,
    }
    result = normalize_kiwi_flight(itin)
    assert result["stops"] == 0
    assert result["is_virtual_interlining"] is False


def test_normalize_kiwi_flight_no_booking_options():
    itin = {**KIWI_ITINERARY, "bookingOptions": []}
    result = normalize_kiwi_flight(itin)
    assert result["booking_url"] == ""


# --- Amadeus Normalization ---


AMADEUS_OFFER = {
    "type": "flight-offer",
    "id": "1",
    "price": {"currency": "TWD", "total": "7500.00", "base": "7000.00"},
    "itineraries": [
        {
            "duration": "PT3H30M",
            "segments": [
                {
                    "departure": {"iataCode": "TPE", "at": "2026-04-01T08:00:00"},
                    "arrival": {"iataCode": "NRT", "at": "2026-04-01T12:30:00"},
                    "carrierCode": "CI",
                    "number": "100",
                    "duration": "PT3H30M",
                },
            ],
        }
    ],
}


def test_normalize_amadeus_flight():
    result = normalize_amadeus_flight(AMADEUS_OFFER)

    assert result["source"] == "amadeus"
    assert result["price"] == 7500.0
    assert result["currency"] == "TWD"
    assert result["airline"] == "CI"
    assert result["flight_number"] == "CI100"
    assert result["origin"] == "TPE"
    assert result["destination"] == "NRT"
    assert result["departure_time"] == "2026-04-01T08:00:00"
    assert result["arrival_time"] == "2026-04-01T12:30:00"
    assert result["duration_minutes"] == 210  # 3h30m
    assert result["stops"] == 0  # 1 segment - 1
    assert len(result["segments"]) == 1


AMADEUS_MULTISEG_OFFER = {
    "price": {"total": "8500.00"},
    "itineraries": [
        {
            "duration": "PT7H15M",
            "segments": [
                {
                    "departure": {"iataCode": "TPE", "at": "2026-04-01T06:00:00"},
                    "arrival": {"iataCode": "ICN", "at": "2026-04-01T09:30:00"},
                    "carrierCode": "CI",
                    "number": "160",
                    "duration": "PT2H30M",
                },
                {
                    "departure": {"iataCode": "ICN", "at": "2026-04-01T11:00:00"},
                    "arrival": {"iataCode": "NRT", "at": "2026-04-01T13:15:00"},
                    "carrierCode": "KE",
                    "number": "705",
                    "duration": "PT2H15M",
                },
            ],
        }
    ],
}


AMADEUS_EUR_OFFER = {
    "price": {"currency": "EUR", "total": "307.00", "base": "280.00"},
    "itineraries": [
        {
            "duration": "PT3H30M",
            "segments": [
                {
                    "departure": {"iataCode": "TPE", "at": "2026-04-01T08:00:00"},
                    "arrival": {"iataCode": "NRT", "at": "2026-04-01T12:30:00"},
                    "carrierCode": "CI",
                    "number": "100",
                    "duration": "PT3H30M",
                },
            ],
        }
    ],
}


def test_normalize_amadeus_flight_currency_from_api():
    """When exchange_rates provided, EUR price is converted to TWD."""
    rates = {"EUR": 1.0, "TWD": 35.2, "USD": 1.08}
    result = normalize_amadeus_flight(AMADEUS_EUR_OFFER, currency="TWD", exchange_rates=rates)
    assert result["currency"] == "TWD"
    assert result["price"] == round(307.0 * 35.2, 2)


def test_normalize_amadeus_flight_no_exchange_rates():
    """Without exchange_rates param, EUR is preserved (backward compat)."""
    result = normalize_amadeus_flight(AMADEUS_EUR_OFFER)
    assert result["currency"] == "EUR"
    assert result["price"] == 307.0


def test_normalize_amadeus_flight_same_currency_no_conversion():
    """No conversion when API currency already matches requested currency."""
    rates = {"EUR": 1.0, "TWD": 35.2}
    result = normalize_amadeus_flight(AMADEUS_OFFER, currency="TWD", exchange_rates=rates)
    # AMADEUS_OFFER has currency=TWD, so no conversion should happen
    assert result["currency"] == "TWD"
    assert result["price"] == 7500.0


def test_normalize_amadeus_flight_currency_fallback():
    """When Amadeus response has no currency field, fall back to the default."""
    result = normalize_amadeus_flight(AMADEUS_MULTISEG_OFFER)
    assert result["currency"] == "TWD"  # default


def test_normalize_amadeus_flight_multi_segment():
    result = normalize_amadeus_flight(AMADEUS_MULTISEG_OFFER)

    assert result["stops"] == 1
    assert result["duration_minutes"] == 435  # 7h15m
    assert len(result["segments"]) == 2
    assert result["segments"][0]["flight_number"] == "CI160"
    assert result["segments"][1]["flight_number"] == "KE705"


# --- ISO Duration Parser ---


def test_parse_iso_duration_hours_and_minutes():
    assert _parse_iso_duration("PT5H30M") == 330


def test_parse_iso_duration_hours_only():
    assert _parse_iso_duration("PT2H") == 120


def test_parse_iso_duration_minutes_only():
    assert _parse_iso_duration("PT45M") == 45


def test_parse_iso_duration_empty():
    assert _parse_iso_duration("") == 0


def test_parse_iso_duration_invalid():
    assert _parse_iso_duration("invalid") == 0


# --- Deduplication ---


def test_deduplication():
    flights = [
        {
            "source": "skyscanner",
            "flight_number": "CI100",
            "departure_time": "2026-04-01T08:00:00",
            "price": 7500,
        },
        {
            "source": "kiwi",
            "flight_number": "CI100",
            "departure_time": "2026-04-01T08:00:00",
            "price": 7200,
        },
        {
            "source": "amadeus",
            "flight_number": "CI100",
            "departure_time": "2026-04-01T08:00:00",
            "price": 7800,
        },
        {
            "source": "skyscanner",
            "flight_number": "LJ752",
            "departure_time": "2026-04-01T02:40:00",
            "price": 7121,
        },
    ]

    result = deduplicate_flights(flights)

    assert len(result) == 2
    # CI100: lowest price should be from kiwi (7200)
    ci100 = [f for f in result if f["flight_number"] == "CI100"][0]
    assert ci100["price"] == 7200
    assert ci100["source"] == "kiwi"
    # LJ752: only one entry
    lj752 = [f for f in result if f["flight_number"] == "LJ752"][0]
    assert lj752["price"] == 7121


def test_deduplication_empty():
    assert deduplicate_flights([]) == []


def test_deduplication_no_duplicates():
    flights = [
        {"flight_number": "CI100", "departure_time": "2026-04-01T08:00:00", "price": 7500},
        {"flight_number": "CI101", "departure_time": "2026-04-01T10:00:00", "price": 8000},
    ]
    result = deduplicate_flights(flights)
    assert len(result) == 2


# --- Roundtrip Return Segments ---


AMADEUS_ROUNDTRIP_OFFER = {
    "type": "flight-offer",
    "id": "2",
    "price": {"currency": "TWD", "total": "14500.00", "base": "13000.00"},
    "itineraries": [
        {
            "duration": "PT3H30M",
            "segments": [
                {
                    "departure": {"iataCode": "TPE", "at": "2026-04-01T08:00:00"},
                    "arrival": {"iataCode": "NRT", "at": "2026-04-01T12:30:00"},
                    "carrierCode": "CI",
                    "number": "100",
                    "duration": "PT3H30M",
                },
            ],
        },
        {
            "duration": "PT4H00M",
            "segments": [
                {
                    "departure": {"iataCode": "NRT", "at": "2026-04-08T14:00:00"},
                    "arrival": {"iataCode": "TPE", "at": "2026-04-08T17:00:00"},
                    "carrierCode": "CI",
                    "number": "101",
                    "duration": "PT4H00M",
                },
            ],
        },
    ],
}


def test_normalize_amadeus_roundtrip_return_segments():
    result = normalize_amadeus_flight(AMADEUS_ROUNDTRIP_OFFER)

    assert result["source"] == "amadeus"
    assert result["price"] == 14500.0
    # Outbound segments
    assert len(result["segments"]) == 1
    assert result["segments"][0]["origin"] == "TPE"
    assert result["segments"][0]["destination"] == "NRT"
    # Return segments
    assert len(result["return_segments"]) == 1
    ret = result["return_segments"][0]
    assert ret["origin"] == "NRT"
    assert ret["destination"] == "TPE"
    assert ret["flight_number"] == "CI101"
    assert ret["departure_time"] == "2026-04-08T14:00:00"
    assert ret["arrival_time"] == "2026-04-08T17:00:00"
    assert ret["duration_minutes"] == 240


def test_normalize_amadeus_oneway_no_return_segments():
    result = normalize_amadeus_flight(AMADEUS_OFFER)
    assert result["return_segments"] == []


SKYSCANNER_ROUNDTRIP_ITINERARY = {
    "id": "itin-rt-001",
    "price": {"formatted": "NT$14,000", "raw": "14000000", "unit": "PRICE_UNIT_MILLI"},
    "legs": [
        {
            "originPlaceId": "128667054",
            "destinationPlaceId": "128668889",
            "departureDateTime": {
                "year": 2026, "month": 4, "day": 1,
                "hour": 8, "minute": 0, "second": 0,
            },
            "arrivalDateTime": {
                "year": 2026, "month": 4, "day": 1,
                "hour": 12, "minute": 30, "second": 0,
            },
            "durationInMinutes": 210,
            "stopCount": 0,
            "segments": [
                {
                    "marketingFlightNumber": "100",
                    "durationInMinutes": 210,
                    "departureDateTime": {
                        "year": 2026, "month": 4, "day": 1,
                        "hour": 8, "minute": 0, "second": 0,
                    },
                    "arrivalDateTime": {
                        "year": 2026, "month": 4, "day": 1,
                        "hour": 12, "minute": 30, "second": 0,
                    },
                    "carriers": {
                        "marketing": {"name": "China Airlines", "iata": "CI"},
                    },
                },
            ],
        },
        {
            "originPlaceId": "128668889",
            "destinationPlaceId": "128667054",
            "departureDateTime": {
                "year": 2026, "month": 4, "day": 8,
                "hour": 14, "minute": 0, "second": 0,
            },
            "arrivalDateTime": {
                "year": 2026, "month": 4, "day": 8,
                "hour": 17, "minute": 0, "second": 0,
            },
            "durationInMinutes": 240,
            "stopCount": 0,
            "segments": [
                {
                    "marketingFlightNumber": "101",
                    "durationInMinutes": 240,
                    "departureDateTime": {
                        "year": 2026, "month": 4, "day": 8,
                        "hour": 14, "minute": 0, "second": 0,
                    },
                    "arrivalDateTime": {
                        "year": 2026, "month": 4, "day": 8,
                        "hour": 17, "minute": 0, "second": 0,
                    },
                    "carriers": {
                        "marketing": {"name": "China Airlines", "iata": "CI"},
                    },
                },
            ],
        },
    ],
    "pricingOptions": [],
}


def test_normalize_skyscanner_roundtrip_return_segments():
    result = normalize_skyscanner_flight(
        SKYSCANNER_ROUNDTRIP_ITINERARY, origin="TPE", destination="NRT"
    )

    assert result["price"] == 14000.0
    # Outbound
    assert len(result["segments"]) == 1
    assert result["segments"][0]["origin"] == "TPE"
    # Return segments
    assert len(result["return_segments"]) == 1
    ret = result["return_segments"][0]
    assert ret["origin"] == "NRT"  # destination becomes return origin
    assert ret["destination"] == "TPE"  # origin becomes return destination
    assert ret["flight_number"] == "CI101"
    assert ret["departure_time"] == "2026-04-08T14:00:00"
    assert ret["arrival_time"] == "2026-04-08T17:00:00"
    assert ret["duration_minutes"] == 240


def test_normalize_skyscanner_oneway_no_return_segments():
    result = normalize_skyscanner_flight(SKYSCANNER_ITINERARY, origin="TPE", destination="NRT")
    assert result["return_segments"] == []


def test_normalize_kiwi_flight_return_segments_empty():
    """Kiwi normalizer always returns empty return_segments (TODO)."""
    result = normalize_kiwi_flight(KIWI_ITINERARY)
    assert result["return_segments"] == []


# --- Schema converter: return segments ---


def test_normalized_dict_to_flight_result_with_return_segments():
    d = normalize_amadeus_flight(AMADEUS_ROUNDTRIP_OFFER)
    flight = normalized_dict_to_flight_result(d)

    assert flight.return_segments is not None
    assert len(flight.return_segments) == 1
    assert flight.return_segments[0].departure_airport == "NRT"
    assert flight.return_segments[0].arrival_airport == "TPE"
    assert flight.return_segments[0].flight_number == "CI101"


def test_normalized_dict_to_flight_result_oneway_no_return():
    d = normalize_amadeus_flight(AMADEUS_OFFER)
    flight = normalized_dict_to_flight_result(d)

    assert flight.return_segments is None
