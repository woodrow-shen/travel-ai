from unittest.mock import AsyncMock, patch

from app.schemas.search import FlightSearchRequest, HotelSearchRequest
from app.services.search_service import SearchService


async def test_search_flights_returns_response(test_user):
    service = SearchService()
    with (
        patch.object(service.amadeus, "search_flights", new_callable=AsyncMock, return_value=[]),
        patch.object(
            service.skyscanner, "search_flights", new_callable=AsyncMock, return_value=[]
        ),
        patch.object(service.kiwi, "search_flights", new_callable=AsyncMock, return_value=[]),
    ):
        request = FlightSearchRequest(
            origin="TPE",
            destination="NRT",
            date_from="2026-04-01",
        )
        result = await service.search_flights(request, test_user)
        assert result.flights == []
        assert result.total_results == 0
        assert result.type == "flight"
        assert result.search_id


async def test_search_hotels_returns_response(test_user):
    service = SearchService()
    request = HotelSearchRequest(
        location="Tokyo",
        check_in="2026-04-01",
        check_out="2026-04-05",
    )
    result = await service.search_hotels(request, test_user)
    assert result.results == []
    assert result.total == 0
