from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.schemas.links import LinkCreate, LinkRead
from src.models.links import Link
from src.auth.models import User
from src.utils.shortener import generate_short_code
from src.utils.check_alias import check_alias
from typing import Optional
from sqlalchemy import select
import datetime

from src.auth.dependencies import current_optional_active_user


router = APIRouter(prefix="/links", tags=["links"])


@router.post("/shorten", response_model=LinkRead)
async def create_short_link(
    data: LinkCreate,
    session: AsyncSession = Depends(get_async_session),
    user: Optional[User] = Depends(current_optional_active_user)
):
    
    if data.custom_alias:
        short_code = await check_alias(session, data.custom_alias)
        
    else:
        short_code = await generate_short_code(session)

    if user:
        link = Link(
            original_url=str(data.original_url),
            short_code=short_code,
            user_id=user.id 
        )
    else:
        link = Link(
            original_url=str(data.original_url),
            short_code=short_code,
            user_id=None
        )

    session.add(link)
    await session.commit()
    await session.refresh(link)

    return link


@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )
    

    # TODO:
    # # Проверяем активна ли ссылка (если есть такое поле)
    # if hasattr(link, 'is_active') and not link.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_410_GONE,
    #         detail="This link has been deactivated"
    #     )
    
    # # Инкрементируем счетчик кликов (если есть)
    # if hasattr(link, 'clicks'):
    #     link.clicks += 1
    #     await session.commit()

    return RedirectResponse(url=link.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


async def check_permission(user, link):
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden for an unlogged user"
        )
    
    if link.user_id and link.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this link"
        )
    
    if not link.user_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update anonymous links"
        )

@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    short_code: str,
    session: AsyncSession = Depends(get_async_session),
    user: Optional[User] = Depends(current_optional_active_user)
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    
    await check_permission()

    await session.delete(link)
    await session.commit()
    
    return None


@router.put("/{short_code}", response_model=LinkRead)
async def update_link(
    short_code: str,
    data: LinkCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_optional_active_user),
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    
    await check_permission(user, link)
    
    link.original_url = str(data.original_url)
    
    # TODO: добавить поле updated_at
    # if hasattr(link, 'updated_at'):
    #     link.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(link)
    
    return link