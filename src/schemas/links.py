from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional
import re
from datetime import datetime, timezone

class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(
        None, 
        min_length=4, 
        max_length=20,
        description="Custom alias for short link (4-20 characters, alphanumeric + _ -)"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="When the link expires (strictly with timezone)! e.g. 2026-04-06T14:00:00+03:00",
    )

    @field_validator('custom_alias')
    def validate_alias(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Alias must contain only letters, numbers, underscore and hyphen')
        return v


    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, v):
        if v is None:
            return None
            
        if v.tzinfo is None:
            raise ValueError(
                "expires_at must include timezone! e.g. 2026-04-06T14:00:00+03:00"
            )
        
        v_utc = v.astimezone(timezone.utc)
        
        if v is not None and v < datetime.now(timezone.utc):
            raise ValueError('expires_at must be in the future')
        if v.second != 0 or v.microsecond != 0:
            raise ValueError('expires_at must be precise to the minute (no seconds)')
        

        return v_utc.replace(tzinfo=None)

    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, v):
        if v is None:
            return None
            
        if v.tzinfo is None:
            raise ValueError(
                "expires_at must include timezone! e.g. 1999-12-31T10:10:00+03:00"
            )
        v_utc = v.astimezone(timezone.utc)
        
        if v_utc < datetime.now(timezone.utc):
            raise ValueError(f'expires_at must be in the future\n{v_utc}\n{datetime.now(timezone.utc)}')
        
        # if v_utc.second != 0 or v_utc.microsecond != 0:
        #     raise ValueError('expires_at must be precise to the minute (no seconds)')
    

        return v_utc.replace(tzinfo=None)
    
        

class LinkRead(BaseModel):
    short_code: str
    original_url: HttpUrl


class LinkUpdate(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = Field(
        None,
        description="Когда ссылка истекает (ISO format). Пример: 1999-12-31T23:59:59",
    )

    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, v):
        if v is None:
            return None
            
        if v.tzinfo is None:
            raise ValueError(
                "expires_at must include timezone! e.g. 1999-12-31T10:10:00+03:00"
            )
        v_utc = v.astimezone(timezone.utc)
        
        if v_utc < datetime.now(timezone.utc):
            raise ValueError(f'expires_at must be in the future\n{v_utc}\n{datetime.now(timezone.utc)}')
        
        # if v_utc.second != 0 or v_utc.microsecond != 0:
        #     raise ValueError('expires_at must be precise to the minute (no seconds)')
    

        return v_utc.replace(tzinfo=None)
    

class LinkStats(BaseModel):
    short_code: str
    original_url: str
    clicks: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_use: Optional[datetime] = None
    # days_since_creation: int
    
    