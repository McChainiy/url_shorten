import pytest
from unittest.mock import AsyncMock, patch

from src.utils.expire_links import ExpireService


@pytest.mark.asyncio
async def test_delete_expired_links():
    
    service = ExpireService()

    mock_session = AsyncMock()

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_session

    with patch("src.utils.expire_links.async_session_maker", return_value=mock_context):

        await service.delete_expired_links()

        assert mock_session.execute.called
        assert mock_session.commit.called


@pytest.mark.asyncio
async def test_run_periodic_cleanup():
    service = ExpireService()

    service.delete_expired_links = AsyncMock()
    async def fake_sleep(x):
        service.running = False

    with patch("asyncio.sleep", fake_sleep):

        await service.run_periodic_cleanup(interval=1)

    service.delete_expired_links.assert_called_once()