from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)  # Use Integer for 4-digit ID
    username = Column(String(255), unique=True, nullable=False)  # Specify length
    email = Column(String(255), unique=True, nullable=False)  # Specify length
    phone = Column(String(20))  # Specify length
    password_hash = Column(String(255))  # Specify length
    address = Column(String(255))  # Specify length
    city = Column(String(100))  # Specify length
    state = Column(String(100))  # Specify length
    postal_code = Column(String(20))  # Specify length
    is_oauth = Column(Boolean, default=False)  # Changed to boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, phone={self.phone})>"
