import pytest

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



@pytest.mark.asyncio
async def test_redirect(async_client):

    create = await async_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"}
    )

    short_code = create.json()["short_code"]

    response = await async_client.get(f"/links/{short_code}")

    assert response.status_code == 307


