import string
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.links import Link

MINIMUM = 6
MAX_ATTEMPTS = 10

async def generate_short_code(session: AsyncSession, length=MINIMUM):
    if length < MINIMUM: 
        raise ValueError(f"Length must be greater than {MINIMUM}")
    c = list(string.ascii_letters + string.digits)
    for i in range(MAX_ATTEMPTS):
        code = ''.join(random.choices(c, k=length))

        result = await session.execute(
            select(Link).where(Link.short_code == code)
        )
        existing_link = result.scalar_one_or_none()
        if not existing_link:
            return code
    raise Exception(f"Could not generate a short code of length {length} after {MAX_ATTEMPTS} attempts. Sorry.")