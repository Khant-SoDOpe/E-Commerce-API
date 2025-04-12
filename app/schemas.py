from uuid import UUID
import uuid
from datetime import datetime
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    postal_code: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    password: str

class UserRead(UserBase, schemas.BaseUser[UUID]):
    pass

class UserCreate(UserBase, schemas.BaseUserCreate):
    pass

class UserUpdate(UserBase, schemas.BaseUserUpdate):
    pass

class ResponseModel(BaseModel):
    status: str
    message: str

class ForgotPasswordResponse(ResponseModel):
    email: str

class ResetPasswordResponse(ResponseModel):
    user_id: str

class ErrorResponse(ResponseModel):
    error_type: str


class ProductBase(BaseModel):
    name: str
    category_id: int
    price: float
    stock: int = 0
    status: bool = True
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_start: Optional[datetime] = None
    discount_end: Optional[datetime] = None

class ProductCreate(BaseModel):
    name: str
    category_id: int
    price: float
    stock: int
    status: bool
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_start: Optional[str] = None
    discount_end: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[bool] = None
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_start: Optional[datetime] = None
    discount_end: Optional[datetime] = None

class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True