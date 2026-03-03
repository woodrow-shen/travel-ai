from unittest.mock import patch

import httpx
import pytest
import respx

from app.clients.rapidapi_base import RapidAPIBaseClient

BASE_URL = "https://test-api.p.rapidapi.com"
HOST = "test-api.p.rapidapi.com"


@pytest.fixture
def base_client():
    with patch("app.clients.rapidapi_base.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = "test-api-key"
        client = RapidAPIBaseClient(BASE_URL, HOST)
    yield client


@respx.mock
async def test_get_success(base_client):
    route = respx.get(f"{BASE_URL}/test/path").mock(
        return_value=httpx.Response(200, json={"status": True, "data": [1, 2, 3]})
    )

    result = await base_client._get("/test/path", {"q": "hello"})

    assert result == {"status": True, "data": [1, 2, 3]}
    assert route.called
    request = route.calls[0].request
    assert request.headers["x-rapidapi-key"] == "test-api-key"
    assert request.headers["x-rapidapi-host"] == HOST


@respx.mock
async def test_get_error_returns_empty_dict(base_client):
    respx.get(f"{BASE_URL}/test/fail").mock(
        return_value=httpx.Response(500, json={"error": "server error"})
    )

    result = await base_client._get("/test/fail")

    assert result == {}


@respx.mock
async def test_post_success(base_client):
    route = respx.post(f"{BASE_URL}/test/post").mock(
        return_value=httpx.Response(200, json={"status": True, "result": "ok"})
    )

    result = await base_client._post("/test/post", {"key": "value"})

    assert result == {"status": True, "result": "ok"}
    assert route.called


@respx.mock
async def test_post_error_returns_empty_dict(base_client):
    respx.post(f"{BASE_URL}/test/post-fail").mock(
        return_value=httpx.Response(422, json={"error": "bad request"})
    )

    result = await base_client._post("/test/post-fail", {"bad": "data"})

    assert result == {}


@respx.mock
async def test_get_network_error_returns_empty_dict(base_client):
    respx.get(f"{BASE_URL}/test/timeout").mock(side_effect=httpx.ConnectTimeout("timeout"))

    result = await base_client._get("/test/timeout")

    assert result == {}


async def test_close(base_client):
    await base_client.close()
    # After close, _get returns {} due to internal error handling (client is closed)
    result = await base_client._get("/anything")
    assert result == {}


def test_missing_api_key():
    """When RAPIDAPI_KEY is empty, client still initializes but requests will fail."""
    with patch("app.clients.rapidapi_base.settings") as mock_settings:
        mock_settings.RAPIDAPI_KEY = ""
        client = RapidAPIBaseClient(BASE_URL, HOST)
        assert client._headers["x-rapidapi-key"] == ""
