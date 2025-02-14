from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import List
import uuid

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String(255), nullable=False, unique=True)
    description = mapped_column(String(255), nullable=True)

class UserRole(Base):
    __tablename__ = "userroles"
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)

class User(Base):
    __tablename__ = 'users'
    
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = mapped_column(String(255), nullable=False)
    email = mapped_column(String(255), unique=True, nullable=False)
    role = mapped_column(String(50), default="user")
    phone = mapped_column(String(20))
    password_hash = mapped_column(String(255))
    address = mapped_column(String(255))
    city = mapped_column(String(100))
    state = mapped_column(String(100))
    postal_code = mapped_column(String(20))
    is_oauth = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles: Mapped[List["Role"]] = relationship("Role", lazy="selectin", secondary="userroles")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, phone={self.phone})>"
