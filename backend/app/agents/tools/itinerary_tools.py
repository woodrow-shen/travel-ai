ITINERARY_TOOLS = [
    {
        "name": "create_itinerary",
        "description": (
            "Generate a day-by-day travel itinerary for a trip, "
            "including activities and transportation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "interests": {"type": "array", "items": {"type": "string"}},
                "budget_level": {"type": "string", "enum": ["budget", "mid", "luxury"]},
            },
            "required": ["destination", "start_date", "end_date"],
        },
    },
    {
        "name": "optimize_route",
        "description": "Optimize the order of activities/locations to minimize travel time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "locations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "lat": {"type": "number"},
                            "lng": {"type": "number"},
                        },
                    },
                },
            },
            "required": ["locations"],
        },
    },
]
