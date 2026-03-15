PRICE_TOOLS = [
    {
        "name": "compare_prices",
        "description": "Compare prices for the same flight/hotel across multiple data sources.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_type": {"type": "string", "enum": ["flight", "hotel"]},
                "search_params": {
                    "type": "object",
                    "description": "Search parameters specific to item type",
                },
            },
            "required": ["item_type", "search_params"],
        },
    },
    {
        "name": "get_price_history",
        "description": "Get historical price data for a route or hotel to identify trends.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "days_back": {"type": "integer", "default": 90},
            },
            "required": ["origin", "destination"],
        },
    },
    {
        "name": "get_price_graph",
        "description": (
            "Get daily lowest flight prices for a date range from Google Flights. "
            "Useful for finding the cheapest travel dates and analyzing price trends."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "IATA airport code (e.g. TPE)",
                },
                "destination": {
                    "type": "string",
                    "description": "IATA airport code (e.g. NRT)",
                },
                "departure_range": {
                    "type": "string",
                    "description": "Start,end dates comma-separated (e.g. 2026-04-01,2026-04-30)",
                },
                "return_date": {
                    "type": "string",
                    "description": "Optional return date for roundtrip (YYYY-MM-DD)",
                },
                "currency": {"type": "string", "default": "TWD"},
            },
            "required": ["origin", "destination", "departure_range"],
        },
    },
]
