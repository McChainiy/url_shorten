# src/services/cleanup_service.py
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import delete, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker
from src.models.links import Link

DAYS_NOT_USED_BEFORE_DEACTIVATION = 30

class ExpireService:
    def __init__(self):
        self.running = False

    async def run_periodic_cleanup(self, interval=3600):
        self.running = True
        while self.running:
            await self.delete_expired_links()
            await asyncio.sleep(interval)
    
    async def delete_expired_links(self):
        async with async_session_maker() as session:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            month_ago = now - timedelta(days=DAYS_NOT_USED_BEFORE_DEACTIVATION)
            
            # вместо удаления помечаем ссылки как истекшие
            await session.execute(
                update(Link)
                .where(or_(Link.expires_at < now, Link.last_use < month_ago))
                .values(is_active=False)
            )
            await session.commit()
    
    def stop(self):
        self.running = False

expire_service = ExpireService()