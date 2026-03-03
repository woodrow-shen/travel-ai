RECOMMENDATION_TOOLS = [
    {
        "name": "get_user_preferences",
        "description": (
            "Get the user's travel preferences "
            "(airlines, alliances, cabin class, stops)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User UUID"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "analyze_reviews",
        "description": (
            "Analyze reviews and ratings for airlines or hotels "
            "to generate a quality score."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "item_type": {"type": "string", "enum": ["airline", "hotel"]},
                "item_id": {"type": "string", "description": "Airline IATA code or hotel ID"},
            },
            "required": ["item_type", "item_id"],
        },
    },
]
