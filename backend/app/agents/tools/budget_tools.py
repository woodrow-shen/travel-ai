BUDGET_TOOLS = [
    {
        "name": "estimate_costs",
        "description": (
            "Estimate total trip costs including flights, "
            "hotels, activities, and daily expenses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "days": {"type": "integer"},
                "travelers": {"type": "integer", "default": 1},
                "budget_level": {"type": "string", "enum": ["budget", "mid", "luxury"]},
            },
            "required": ["destination", "days"],
        },
    },
    {
        "name": "find_alternatives",
        "description": "Find cheaper alternatives for flights, hotels, or activities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_type": {"type": "string", "enum": ["flight", "hotel", "activity"]},
                "current_option": {"type": "object", "description": "Current option details"},
                "max_price": {"type": "number"},
            },
            "required": ["item_type", "current_option"],
        },
    },
]
