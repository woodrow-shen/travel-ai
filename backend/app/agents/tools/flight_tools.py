FLIGHT_TOOLS = [
    {
        "name": "search_flights",
        "description": (
            "Search for flights between two airports on given dates. "
            "Returns a list of available flights with prices."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "IATA airport code for departure (e.g., TPE)",
                },
                "destination": {
                    "type": "string",
                    "description": "IATA airport code for arrival (e.g., NRT)",
                },
                "date_from": {"type": "string", "description": "Departure date (YYYY-MM-DD)"},
                "date_to": {
                    "type": "string",
                    "description": "Return date (YYYY-MM-DD), optional",
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers",
                    "default": 1,
                },
                "cabin_class": {
                    "type": "string",
                    "description": "Cabin class: economy, business, first",
                },
                "max_stops": {"type": "integer", "description": "Maximum number of stops"},
            },
            "required": ["origin", "destination", "date_from"],
        },
    },
    {
        "name": "search_domestic_flights",
        "description": (
            "Search for domestic flights within a country, including "
            "foreigner discount fares (e.g., ANA Experience JAPAN Fare)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Domestic origin airport code"},
                "destination": {
                    "type": "string",
                    "description": "Domestic destination airport code",
                },
                "date": {"type": "string", "description": "Flight date (YYYY-MM-DD)"},
                "country": {"type": "string", "description": "Country code (e.g., JP, KR, TH)"},
            },
            "required": ["origin", "destination", "date", "country"],
        },
    },
    {
        "name": "resolve_gateway_hubs",
        "description": (
            "Given a destination airport, resolve the gateway hub airports "
            "for the country (e.g., NRT/HND for Japan)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string", "description": "Target destination airport code"},
            },
            "required": ["destination"],
        },
    },
    {
        "name": "combine_segments",
        "description": (
            "Combine international + domestic flight segments, "
            "calculating layover time and total price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "international_flights": {
                    "type": "array",
                    "description": "List of international flight results",
                },
                "domestic_flights": {
                    "type": "array",
                    "description": "List of domestic flight results",
                },
                "min_layover_minutes": {"type": "integer", "default": 120},
                "max_layover_minutes": {"type": "integer", "default": 360},
            },
            "required": ["international_flights", "domestic_flights"],
        },
    },
]
