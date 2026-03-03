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
]
