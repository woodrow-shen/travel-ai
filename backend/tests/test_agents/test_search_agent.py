from unittest.mock import AsyncMock, patch

import pytest

from app.agents.search_agent import SearchAgent
from app.config import settings

requires_amadeus = pytest.mark.skipif(
    not settings.AMADEUS_API_KEY, reason="AMADEUS_API_KEY not set"
)


async def test_search_agent_properties():
    agent = SearchAgent()
    assert agent.name == "search"
    assert "search" in agent.system_prompt.lower()
    assert len(agent.tools) > 0


async def test_resolve_gateway_hubs_japan():
    agent = SearchAgent()
    result = await agent.execute_tool("resolve_gateway_hubs", {"destination": "FKS"})
    assert result["needs_multi_segment"] is True
    assert result["country"] == "JP"
    assert "NRT" in result["gateway_hubs"]
    assert "HND" in result["gateway_hubs"]


async def test_resolve_gateway_hubs_no_hub():
    agent = SearchAgent()
    result = await agent.execute_tool("resolve_gateway_hubs", {"destination": "NRT"})
    assert result["needs_multi_segment"] is False


async def test_search_flights():
    agent = SearchAgent()
    mock_results = [
        {
            "type": "flight-offer",
            "source": "GDS",
            "price": {"grandTotal": "150.00", "currency": "EUR"},
            "itineraries": [
                {
                    "duration": "PT3H25M",
                    "segments": [
                        {
                            "departure": {"iataCode": "TPE", "at": "2026-04-01T08:00:00"},
                            "arrival": {"iataCode": "NRT", "at": "2026-04-01T12:25:00"},
                            "carrierCode": "BR",
                            "number": "198",
                            "duration": "PT3H25M",
                            "numberOfStops": 0,
                        }
                    ],
                }
            ],
        }
    ]
    with patch.object(
        agent.amadeus, "search_flights", new_callable=AsyncMock, return_value=mock_results
    ):
        result = await agent.execute_tool(
            "search_flights",
            {"origin": "TPE", "destination": "NRT", "date_from": "2026-04-01"},
        )
    assert "flights" in result
    assert "total" in result


async def test_unknown_tool():
    agent = SearchAgent()
    result = await agent.execute_tool("nonexistent", {})
    assert "error" in result


@requires_amadeus
async def test_search_flights_real_api():
    """Integration test: hits real Amadeus API. Skipped in CI."""
    agent = SearchAgent()
    result = await agent.execute_tool(
        "search_flights",
        {"origin": "TPE", "destination": "NRT", "date_from": "2026-04-01"},
    )
    assert "flights" in result
    assert "total" in result
