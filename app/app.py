from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request, responses
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.db import User, create_db_and_tables
from app.schemas import (
    UserCreate, UserRead, UserUpdate,
    PasswordResetRequest, PasswordReset,
    ForgotPasswordResponse, ResetPasswordResponse,
    ErrorResponse
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

# Add CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/auth/verify")
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
        200: {"model": ForgotPasswordResponse},
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
            return ForgotPasswordResponse(
                status="success",
                message="Password reset instructions sent to your email",
                email=request.email
            )
    except Exception as e:
        logger.error(f"Password reset request failed: {str(e)}")
    
    return ForgotPasswordResponse(
        status="success",
        message="If the email exists, password reset instructions will be sent",
        email=request.email
    )

@app.post(
    "/auth/reset-password",
    response_model=ResetPasswordResponse,
    responses={
        200: {"model": ResetPasswordResponse},
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

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}