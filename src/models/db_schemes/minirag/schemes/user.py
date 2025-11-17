from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(SQLAlchemyBase):

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
