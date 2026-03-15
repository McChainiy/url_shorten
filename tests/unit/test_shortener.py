import pytest
from unittest.mock import AsyncMock, MagicMock

from src.utils.shortener import generate_short_code


@pytest.mark.asyncio
async def test_generate_short_code_success():
    session = AsyncMock()
    result_mock = MagicMock()

    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    code = await generate_short_code(session)

    assert code == 6


@pytest.mark.asyncio
async def test_generate_short_code_success():
    session = AsyncMock()
    result_mock = MagicMock()

    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    code = await generate_short_code(session)
    code2 = await generate_short_code(session)

    assert len(code) == 6
    assert code2 != code

@pytest.mark.asyncio
async def test_generate_short_code_fail():
    session = AsyncMock()
    result_mock = MagicMock()

    result_mock.scalar_one_or_none.return_value = 'abcd23'
    session.execute.return_value = result_mock
    with pytest.raises(Exception):
        await generate_short_code(session)

@pytest.mark.asyncio
async def test_generate_short_code_invalid_length():

    session = AsyncMock()

    with pytest.raises(ValueError):
        await generate_short_code(session, length=3)