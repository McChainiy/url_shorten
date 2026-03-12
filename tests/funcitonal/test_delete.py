import pytest
from sqlalchemy import select
from src.models.links import Link

@pytest.mark.asyncio
async def test_delete_link_unlogged(async_client):

    create = await async_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    short_code = create.json()["short_code"]

    response = await async_client.delete(f"/links/{short_code}")

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_link_logged(auth_client, db):

    short_code = 'wtf12345'
    create = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com",
              "custom_alias": f"{short_code}"}
    )

    # short_code = create.json()["short_code"]
    

    response = await auth_client.delete(f"/links/{short_code}")

    assert response.status_code == 204

    result = await db.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    assert link is None

@pytest.mark.asyncio
async def test_delete_link_404(auth_client, db):

    create = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    short_code = create.json()["short_code"]

    response = await auth_client.delete(f"/links/hahahah")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_link_403(auth_client, db):

    create = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    # short_code = create.json()["short_code"]
    short_code = 'wtf12345'

    response = await auth_client.delete(f"/links/{short_code}")

    assert response.status_code == 404