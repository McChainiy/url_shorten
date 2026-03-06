from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from src.auth.models import User

class LinkService:
    MAX_EXPIRY_DAYS = {
        'anonymous': 7,
        'authenticated': 100,
        'premium': 365
    }
    
    DEFAULT_EXPIRY_DAYS = {
        'anonymous': 7,
        'authenticated': 30,
        'premium': 90
    }
    
    @classmethod
    def get_user_type(cls, user: Optional[User]) -> str:
        if not user:
            return 'anonymous'
        return 'authenticated'
    
    @classmethod
    def validate_expiry_date(
        cls, 
        expires_at: Optional[datetime], 
        user: Optional[User]
    ) -> datetime:
        user_type = cls.get_user_type(user)
        now = datetime.now()
        
        if expires_at is None:
            expires_at = now + timedelta(days=cls.DEFAULT_EXPIRY_DAYS[user_type])
            return expires_at.replace(second=0, microsecond=0)
        
        max_days = cls.MAX_EXPIRY_DAYS[user_type]
        max_date = now + timedelta(days=max_days)
        
        if expires_at > max_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": f"expires_at too far in the future",
                    "max_allowed": max_date.isoformat(),
                    "max_days": max_days,
                    "user_type": user_type
                }
            )
        
        return expires_at.replace(second=0, microsecond=0)