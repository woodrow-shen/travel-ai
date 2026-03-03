HOTEL_TOOLS = [
    {
        "name": "search_hotels",
        "description": "Search for hotels at a given location with check-in/check-out dates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City or area name"},
                "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                "check_out": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                "guests": {"type": "integer", "default": 1},
                "rooms": {"type": "integer", "default": 1},
                "stars_min": {"type": "integer", "description": "Minimum star rating"},
            },
            "required": ["location", "check_in", "check_out"],
        },
    },
]
