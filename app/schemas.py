import uuid
from datetime import datetime
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str
    phone: str
    address: str
    city: str
    state: str
    postal_code: str
    oauth_provider: str | None = None
    oauth_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class UserRead(schemas.BaseUser[uuid.UUID], UserBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

class UserCreate(schemas.BaseUserCreate, UserBase):
    pass

class UserUpdate(schemas.BaseUserUpdate, UserBase):
    pass
