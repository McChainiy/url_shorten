import uuid
from sqlalchemy.orm import Mapped
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from src.models.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass