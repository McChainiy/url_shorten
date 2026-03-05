from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    original_url: HttpUrl

class LinkRead(BaseModel):
    short_code: str
    original_url: HttpUrl