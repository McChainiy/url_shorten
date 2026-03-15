import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from src.utils.check_alias import check_alias, TAKEN_CODES

@pytest.mark.asyncio
async def test_check_alias_success():
    session = AsyncMock()
    
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    
    alias = "unique_alias"
    result = await check_alias(session, alias)
    
    assert result == alias
    session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_check_alias_fail():
    session = AsyncMock()
    
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = 'old_alias'
    session.execute.return_value = result_mock
    
    alias = "old_alias"
    with pytest.raises(HTTPException):
        await check_alias(session, alias)
