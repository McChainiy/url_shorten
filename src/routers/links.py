from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.schemas.links import LinkCreate, LinkRead
from src.models.links import Link
from src.auth.models import User
from src.utils.shortener import generate_short_code

from src.auth.dependencies import current_active_user

router = APIRouter(prefix="/links", tags=["links"])




@router.post("/shorten", response_model=LinkRead)
async def create_short_link(
    data: LinkCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    short_code = generate_short_code()

    link = Link(
        original_url=str(data.original_url),
        short_code=short_code,
        user_id=user.id
    )

    session.add(link)
    await session.commit()
    await session.refresh(link)

    return link