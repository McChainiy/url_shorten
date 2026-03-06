from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional
import re
from datetime import datetime

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
        description="Когда ссылка истекает (ISO format). Пример: 1999-12-31T23:59:59",
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
        if v is not None and v < datetime.now():
            raise ValueError('expires_at must be in the future')
        if v.second != 0 or v.microsecond != 0:
            raise ValueError('expires_at must be precise to the minute (no seconds)')
        return v
    

class LinkRead(BaseModel):
    short_code: str
    original_url: HttpUrl