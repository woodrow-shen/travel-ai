from app.agents.search_agent import SearchAgent


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
    result = await agent.execute_tool(
        "search_flights", {"origin": "TPE", "destination": "NRT", "date_from": "2026-04-01"}
    )
    assert "flights" in result
    assert "total" in result


async def test_unknown_tool():
    agent = SearchAgent()
    result = await agent.execute_tool("nonexistent", {})
    assert "error" in result
