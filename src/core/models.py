from sqlalchemy import Column, String, DateTime, func

from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    phone_number = Column(String, primary_key=True, index=True)

    state = Column(String, default="START")

    name = Column(String, nullable=True)
    language = Column(String, default="ru")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
