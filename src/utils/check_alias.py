from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.links import Link
from sqlalchemy import select


async def check_alias(
        session: AsyncSession,
        alias: str
):
    result = await session.execute(
        select(Link).where(Link.short_code == alias)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "This custom alias is already taken :(",
                "code": "ALIAS_TAKEN"
            }
        )

    return alias