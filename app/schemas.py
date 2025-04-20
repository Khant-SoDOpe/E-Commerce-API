from uuid import UUID, uuid4  # Import uuid4 for generating default UUIDs
import uuid
from datetime import datetime, timezone, timedelta
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr
from typing import Optional

JST = timezone(timedelta(hours=9))  # Define Japan Standard Time (UTC+9)

class UserBase(BaseModel):
    """Use alias generators for consistent field naming."""
    username: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    postal_code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        alias_generator = lambda field: field.lower()
        allow_population_by_field_name = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    password: str

class UserRead(UserBase, schemas.BaseUser[UUID]):
    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(JST).strftime("%Y-%m-%d-%H-%M-%S")
        }

class UserCreate(UserBase, schemas.BaseUserCreate):
    is_active: Optional[bool] = True  # Default to True
    is_superuser: Optional[bool] = False  # Default to False
    is_verified: Optional[bool] = False  # Default to False
    created_at: Optional[datetime] = None  # Default to None, will be set by the database
    updated_at: Optional[datetime] = None  # Default to None, will be set by the database

    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(JST).strftime("%Y-%m-%d-%H-%M-%S")
        }

class UserUpdate(UserBase, schemas.BaseUserUpdate):
    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(JST).strftime("%Y-%m-%d-%H-%M-%S")
        }

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
    category_id: UUID
    price: float
    stock: int = 0
    status: bool = True
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_start: Optional[datetime] = None
    discount_end: Optional[datetime] = None

class ProductCreate(BaseModel):
    product_id: UUID = uuid4()  # Auto-generate product_id
    name: str
    category_id: UUID  # Ensure category_id is required
    price: float
    stock: int
    status: bool
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_start: Optional[str] = None
    discount_end: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[UUID] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[bool] = None
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_start: Optional[datetime] = None
    discount_end: Optional[datetime] = None

class ProductRead(ProductBase):
    product_id: UUID  # Renamed from id to product_id
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.astimezone(JST).strftime("%Y-%m-%d-%H-%M-%S")
        }

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryRead(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.astimezone(JST).strftime("%Y-%m-%d-%H-%M-%S")
        }

class AdminCreate(BaseModel):
    user_id: UUID

class AdminRead(UserRead):
    admin_granted_by: Optional[UUID] = None
    admin_granted_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(JST).strftime("%Y-%m-%d-%H-%M-%S")
        }