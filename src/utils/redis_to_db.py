from sqlalchemy import select, or_, update
import datetime
from src.models.links import Link


async def save_stats_to_db(redis, session):

    keys = await redis.keys("clicks:*")

    for key in keys:
        short_code = key.split(":")[1]

        clicks = int(await redis.get(key) or 0)
        last_use = await redis.get(f"last_use:{short_code}")
        # print(last_use, clicks)
    
        if last_use is None or clicks == 0:
            continue
        last_use = datetime.datetime.fromtimestamp(int(last_use))

        await session.execute(
            update(Link)
            .where(Link.short_code == short_code)
            .values(
                clicks=Link.clicks + clicks,
                last_use=last_use)
            )

        await redis.delete(key)
        await redis.delete(f"last_use:{short_code}")

    await session.commit()