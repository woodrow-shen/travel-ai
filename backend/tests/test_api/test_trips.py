import uuid

from httpx import AsyncClient


async def test_create_trip(client: AsyncClient, auth_headers):
    resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "Tokyo Trip",
            "destination": "Tokyo",
            "start_date": "2026-04-01",
            "end_date": "2026-04-10",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Tokyo Trip"
    assert data["destination"] == "Tokyo"


async def test_list_trips(client: AsyncClient, auth_headers):
    # Create two trips
    await client.post(
        "/api/v1/trips", json={"title": "Trip 1"}, headers=auth_headers
    )
    await client.post(
        "/api/v1/trips", json={"title": "Trip 2"}, headers=auth_headers
    )

    resp = await client.get("/api/v1/trips", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


async def test_get_trip(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/v1/trips", json={"title": "My Trip"}, headers=auth_headers
    )
    trip_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "My Trip"


async def test_update_trip(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/v1/trips", json={"title": "Old Title"}, headers=auth_headers
    )
    trip_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"title": "New Title"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


async def test_delete_trip(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/api/v1/trips", json={"title": "To Delete"}, headers=auth_headers
    )
    trip_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert resp.status_code == 404


async def test_get_nonexistent_trip(client: AsyncClient, auth_headers):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/trips/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404
