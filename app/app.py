from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import os
from datetime import datetime
from uuid import UUID

from app.db import Product, User, Category, get_async_session, create_db_and_tables
from app.schemas import ProductCreate, ProductRead, ProductUpdate
from sqlalchemy import Column, DateTime, func, select

from app.schemas import (
    UserCreate, UserRead, UserUpdate,
    PasswordResetRequest, PasswordReset,
    ForgotPasswordResponse, ResetPasswordResponse,
    ErrorResponse,
    ProductCreate, ProductRead, ProductUpdate,
    CategoryCreate, CategoryRead, CategoryUpdate,
    AdminCreate, AdminRead
)

from app.users import (
    auth_backend,
    current_active_user,
    fastapi_users,
    get_user_manager,
    UserManager
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Add HTTPS redirection middleware for production
if os.getenv("ENV", "development") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Add CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Authorization"],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/auth/verify", responses={200: {"description": "Email verified successfully"}})
async def verify_email(token: str, user_manager=Depends(get_user_manager)):
    try:
        logger.debug(f"Verifying token: {token}")
        user = await user_manager.verify_user(token)
        logger.info(f"User {user.id} verified successfully")
        return JSONResponse(
            status_code=200,
            content={
                "message": "Email verified successfully",
                "user_id": str(user.id),
                "is_verified": user.is_verified
            }
        )
    except ValueError as e:
        logger.error(f"Verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during verification: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.post(
    "/auth/forgot-password",
    response_model=ForgotPasswordResponse,
    responses={
        200: {"description": "Password reset instructions sent to the email"},
        500: {"model": ErrorResponse}
    }
)
async def forgot_password(
    request: PasswordResetRequest,
    user_manager: UserManager = Depends(get_user_manager)
):
    try:
        user = await user_manager.get_by_email(request.email)
        if user:
            token = await user_manager.forgot_password(user, None)
            logger.info(f"Password reset email sent for user: {user.id}")
        else:
            logger.info(f"No user found with email: {request.email}")
    except Exception as e:
        logger.error(f"Password reset request failed: {str(e)}")
    
    # Always return the email in the response, even if the user does not exist
    return ForgotPasswordResponse(
        status="success",
        message="If the email exists, password reset instructions will be sent",
        email=request.email
    )

@app.post(
    "/auth/reset-password",
    response_model=ResetPasswordResponse,
    responses={
        200: {"description": "Password reset successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def reset_password(
    reset_data: PasswordReset,
    request: Request,
    user_manager: UserManager = Depends(get_user_manager)
):
    try:
        user = await user_manager.reset_password(reset_data.token, reset_data.password, request)
        user.updated_at = datetime.now()
        return ResetPasswordResponse(
            status="success",
            message="Password has been reset successfully",
            user_id=str(user.id)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(e),
                "error_type": "validation_error"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An unexpected error occurred",
                "error_type": "server_error"
            }
        )

@app.get("/authenticated-route", responses={200: {"description": "Authenticated route accessed successfully"}})
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

@app.post(
    "/products/",
    response_model=ProductRead,
    tags=["products"],
    responses={200: {"description": "Product created successfully"}}
)
async def create_product(
    product: ProductCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can add products")
    
    category = await db.get(Category, product.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    product_data = product.model_dump()
    if "discount_start" in product_data and product_data["discount_start"]:
        product_data["discount_start"] = datetime.fromisoformat(product_data["discount_start"].replace("Z", "+00:00"))
    if "discount_end" in product_data and product_data["discount_end"]:
        product_data["discount_end"] = datetime.fromisoformat(product_data["discount_end"].replace("Z", "+00:00"))
    
    db_product = Product(**product_data)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@app.get(
    "/products/",
    response_model=List[ProductRead],
    tags=["products"],
    responses={200: {"description": "Products retrieved successfully"}}
)
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Product).offset(skip).limit(limit).order_by(Product.created_at.desc())
    )
    return result.scalars().all()

@app.get(
    "/products/{product_id}",
    response_model=ProductRead,
    tags=["products"],
    responses={200: {"description": "Product retrieved successfully"}}
)
async def read_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put(
    "/products/{product_id}",
    response_model=ProductRead,
    tags=["products"],
    responses={200: {"description": "Product updated successfully"}}
)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can update products")
    db_product = await db.get(Product, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = product_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    for key, value in update_data.items():
        setattr(db_product, key, value)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@app.delete(
    "/products/{product_id}",
    tags=["products"],
    responses={200: {"description": "Product deleted successfully"}}
)
async def delete_product(
    product_id: UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can delete products")
    db_product = await db.get(Product, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(db_product)
    await db.commit()
    return {"message": "Product deleted successfully"}

@app.post(
    "/categories/",
    response_model=CategoryRead,
    tags=["categories"],
    responses={200: {"description": "Category created successfully"}}
)
async def create_category(
    category: CategoryCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can add categories")
    
    db_category = Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@app.get(
    "/categories/",
    response_model=List[CategoryRead],
    tags=["categories"],
    responses={200: {"description": "Categories retrieved successfully"}}
)
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Category).offset(skip).limit(limit).order_by(Category.created_at.desc())
    )
    return result.scalars().all()

@app.get(
    "/categories/{category_id}",
    response_model=CategoryRead,
    tags=["categories"],
    responses={200: {"description": "Category retrieved successfully"}}
)
async def read_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put(
    "/categories/{category_id}",
    response_model=CategoryRead,
    tags=["categories"],
    responses={200: {"description": "Category updated successfully"}}
)
async def update_category(
    category_id: UUID,
    category_update: CategoryUpdate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can update categories")
    db_category = await db.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    update_data = category_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    for key, value in update_data.items():
        setattr(db_category, key, value)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@app.delete(
    "/categories/{category_id}",
    tags=["categories"],
    responses={200: {"description": "Category deleted successfully"}}
)
async def delete_category(
    category_id: UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can delete categories")
    db_category = await db.get(Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(db_category)
    await db.commit()
    return {"message": "Category deleted successfully"}

# Admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get(
    "/list",
    response_model=List[AdminRead],
    summary="List all admins",
    description="Retrieve a list of all admin users, including details about who granted them admin privileges and when.",
    responses={200: {"description": "Admins retrieved successfully"}}
)
async def list_admins(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can access this route")
    
    result = await db.execute(select(User).where(User.is_superuser == True))
    admins = result.scalars().all()
    return admins

@admin_router.post(
    "/add",
    response_model=AdminRead,
    summary="Add a new admin",
    description="Promote a user to admin by setting their `is_superuser` flag to `True`. Tracks who granted the admin privileges and when.",
    responses={200: {"description": "Admin added successfully"}}
)
async def add_admin(
    admin_data: AdminCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can add admins")
    
    new_admin = await db.get(User, admin_data.user_id)
    if not new_admin:
        raise HTTPException(status_code=404, detail="User not found")
    
    if new_admin.is_superuser:
        raise HTTPException(status_code=400, detail="User is already an admin")
    
    new_admin.is_superuser = True
    new_admin.admin_granted_by = user.id
    new_admin.admin_granted_at = datetime.now()
    await db.commit()
    await db.refresh(new_admin)
    return new_admin

@admin_router.delete(
    "/remove/{admin_id}",
    response_model=AdminRead,
    summary="Remove an admin",
    description="Revoke admin privileges from a user by setting their `is_superuser` flag to `False`. Clears the tracking fields for admin privileges.",
    responses={200: {"description": "Admin removed successfully"}}
)
async def remove_admin(
    admin_id: UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can remove admins")
    
    admin = await db.get(User, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    if not admin.is_superuser:
        raise HTTPException(status_code=400, detail="User is not an admin")
    
    admin.is_superuser = False
    admin.admin_granted_by = None
    admin.admin_granted_at = None
    await db.commit()
    await db.refresh(admin)
    return admin

@admin_router.get(
    "/users",
    response_model=List[UserRead],
    summary="List all users",
    description="Retrieve a list of all users. Only accessible by superusers.",
    responses={200: {"description": "Users retrieved successfully"}}
)
async def list_users(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can access this route")
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# Include the admin router
app.include_router(admin_router)