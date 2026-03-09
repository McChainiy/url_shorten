from src.database import get_async_session, async_session_maker
from src.utils.redis_to_db import save_stats_to_db
from src.redis import redis
import asyncio

async def stats_worker():
    while True:
        async with async_session_maker() as session:
            await save_stats_to_db(redis, session)

        await asyncio.sleep(30)