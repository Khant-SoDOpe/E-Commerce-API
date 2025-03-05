from uuid import UUID
import uuid
from datetime import datetime
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr

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
