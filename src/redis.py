import redis.asyncio as aioredis

redis = aioredis.from_url("redis://localhost", decode_responses=True)