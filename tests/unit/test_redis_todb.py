import pytest
from unittest.mock import AsyncMock

from src.utils.redis_to_db import save_stats_to_db


@pytest.mark.asyncio
async def test_save_stats_success():

    redis = AsyncMock()
    session = AsyncMock()

    redis.keys.return_value = ["clicks:test"]
    redis.get.side_effect = [
        "5",
        "1111111111",
    ]

    await save_stats_to_db(redis, session)

    assert session.execute.called
    assert session.commit.called
    redis.delete.assert_any_call("clicks:test")
    redis.delete.assert_any_call("last_use:test")