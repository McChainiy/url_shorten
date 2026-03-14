import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from src.main import lifespan

@pytest.mark.asyncio
async def test_lifespan_creates_tasks():
    mock_app = MagicMock()
    
    with patch('asyncio.create_task') as mock_create_task, \
         patch('src.main.redis') as mock_redis, \
         patch('src.main.expire_service') as mock_expire_service:
        
        mock_create_task.return_value = AsyncMock()
        
        async with lifespan(mock_app):
            assert mock_create_task.call_count == 2
            
            mock_expire_service.run_periodic_cleanup.assert_called_once_with(interval=10)
        
        mock_expire_service.stop.assert_called_once()
        mock_redis.close.assert_called_once()

@pytest.mark.asyncio
async def test_lifespan_cancels_tasks_on_exit():
    mock_app = MagicMock()
    mock_task = AsyncMock()
    
    with patch('asyncio.create_task', return_value=mock_task), \
         patch('src.main.redis') as mock_redis, \
         patch('src.main.expire_service') as mock_expire_service:
        
        async with lifespan(mock_app):
            pass
        
        mock_task.cancel.call_count == 2