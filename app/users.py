import uuid
from typing import Optional
import logging
from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
import jwt
from datetime import datetime, timedelta
from app.db import User, get_user_db
from app.email import send_verification_email, send_password_reset_email
from fastapi_users.schemas import BaseUserUpdate, BaseUserCreate  # Correct import for BaseUserCreate
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError  # Import IntegrityError

logger = logging.getLogger(__name__)

SECRET = "SECRET"

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def generate_verification_token(self, user: User) -> str:
        data = {
            "user_id": str(user.id),  # Convert UUID to string
            "exp": datetime.now() + timedelta(hours=24),
            "aud": "fastapi-users:verify"  # Add audience claim
        }
        return jwt.encode(data, self.verification_token_secret, algorithm="HS256")

    def verify_token(self, token: str, secret: str, audience: str = None) -> uuid.UUID:
        try:
            options = {"verify_aud": bool(audience)}
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                audience=audience,
                options=options
            )
            # For password reset tokens, use 'sub' field
            if audience == "fastapi-users:reset":
                user_id = payload.get("sub")
            else:
                user_id = payload.get("user_id")

            if not user_id:
                raise HTTPException(status_code=400, detail="Invalid token: no user identifier found")
                
            return uuid.UUID(user_id)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except (jwt.InvalidTokenError, ValueError) as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        token = self.generate_verification_token(user)
        await send_verification_email(user.email, token)
        print(f"User {user.id} has registered. Verification email sent.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        try:
            await send_password_reset_email(user.email, token)
            logger.info(f"Password reset email sent to user {user.id}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to send password reset email")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def verify_user(self, token: str):
        try:
            user_id = self.verify_token(token, self.verification_token_secret, "fastapi-users:verify")
            user = await self.get(user_id)
            
            if not user:
                raise HTTPException(status_code=403, detail="User not found")
            
            if not user.is_verified:
                # Update the user with verified status and updated_at timestamp
                update_dict = {
                    "is_verified": True,
                    "updated_at": datetime.now()  # Update the updated_at field
                }
                await self.user_db.update(user, update_dict)
                user = await self.get(user_id)  # Refresh user data
            
            return user
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")

    async def reset_password(self, token: str, password: str, request: Optional[Request] = None):
        try:
            user_id = self.verify_token(token, self.reset_password_token_secret, "fastapi-users:reset")
            user = await self.get(user_id)
            
            if not user:
                raise HTTPException(status_code=403, detail="User not found")
            
            # Update the user with the new password and updated_at timestamp
            user_update = BaseUserUpdate(password=password)
            await super().update(
                user_update=user_update,
                user=user,
                safe=True,
                request=request
            )
            await self.user_db.update(user, {"updated_at": datetime.now()})  # Update the updated_at field
            
            logger.info(f"Password successfully reset for user {user.id}")
            return user
            
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Password reset failed: {str(e)}")

    async def on_exception(self, exception: Exception, request: Optional[Request] = None):
        if isinstance(exception, HTTPException):
            if exception.status_code == 401:
                # Custom error response for invalid login credentials
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": "error",
                        "message": "Invalid login credentials. Please check your email and password.",
                        "error_type": "authentication_error"
                    }
                )
            elif exception.status_code == 404:
                # Custom error response for account not found
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "error",
                        "message": "Account not found. Please check your email or register for a new account.",
                        "error_type": "account_not_found"
                    }
                )
        # For other exceptions, use the default behavior
        return await super().on_exception(exception, request)

    async def create(self, user_create: BaseUserCreate, safe: bool = False, request: Optional[Request] = None) -> User:
        try:
            return await super().create(user_create, safe=safe, request=request)
        except IntegrityError as e:
            if "user_phone_key" in str(e.orig):
                raise HTTPException(
                    status_code=400,
                    detail="A user with this phone number already exists."
                )
            elif "user_username_key" in str(e.orig):
                raise HTTPException(
                    status_code=400,
                    detail="A user with this username already exists."
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="A database integrity error occurred."
                )


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)