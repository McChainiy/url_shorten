# src/auth/models.py
import uuid
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import relationship
from src.models.base import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    links = relationship(
        "Link",
        back_populates="user",
        cascade="all, delete-orphan",
    )