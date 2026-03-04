from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, Boolean, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()



