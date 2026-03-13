import pytest
from sqlalchemy import select
from src.models.links import Link


# create
@pytest.mark.asyncio
async def test_create_short_link(async_client):

    response = await async_client.post(
        "/links/shorten",
        json={
            "original_url": "https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["original_url"] == "https://example.com/"
    assert "short_code" in data



# update
@pytest.mark.asyncio
async def test_update_link_success(auth_client, db):
    create = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    short_code = create.json()["short_code"]

    response = await auth_client.put(
        f"/links/{short_code}",
        json={
            "original_url": "https://google.com",
            "expires_at": None
        }
    )
    assert response.status_code == 200

    data = response.json()

    assert data["original_url"] == "https://google.com/"
    assert data["short_code"] == short_code

    result = await db.execute(
        select(Link).where(Link.short_code == short_code)
    )

    link = result.scalar_one()

    assert link.original_url == "https://google.com/"

@pytest.mark.asyncio
async def test_update_link_invalid_expiry(auth_client):

    create = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    short_code = create.json()["short_code"]

    response = await auth_client.put(
        f"/links/{short_code}",
        json={
            "original_url": "https://google.com",
            "expires_at": "2000-01-01T00:00:00"
        }
    )

    assert response.status_code == 422


# search
@pytest.mark.asyncio
async def test_search_links_unlogged(async_client, create_links):
    response = await async_client.get("/links/search", params={"original_url": "example"})
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 5

@pytest.mark.asyncio
async def test_search_links_logged(auth_client, create_links, test_user):
    response = await auth_client.get("/links/search", params={"original_url": "https://example.com",
                                                              "exact_match": True})
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1



@pytest.mark.asyncio
async def test_redirect(async_client):

    create = await async_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    short_code = create.json()["short_code"]

    response = await async_client.get(f"/links/{short_code}")

    assert response.status_code == 307


