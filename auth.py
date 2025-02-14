from fastapi import FastAPI, HTTPException, Depends, APIRouter, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, UUID4
from database import SessionLocal, engine
import models
import logging
from passlib.context import CryptContext
import uuid
import jwt  # Ensure this is the correct import from pyjwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
import os
from models import User as UserModel

# Create all database tables (if they don't already exist)
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    role: str
    email: EmailStr
    phone: str
    password: str
    address: str
    city: str
    state: str
    postal_code: str
    is_oauth: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    id: UUID4

class LoginResponse(BaseModel):
    message: str
    user_id: UUID4

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class User(BaseModel):
    id: UUID4
    username: str
    role: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    postal_code: str
    is_oauth: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    new_password: str | None = None

# Set up password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password using bcrypt
def hash_password(password: str):
    return pwd_context.hash(password)

# Verify the password using bcrypt
def verify_password(plain_password: str, hashed_password: str):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logging.error(f"Error verifying password: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid password hash")

# Generate a unique UUID for users
def generate_unique_id():
    return str(uuid.uuid4())

# Add a logger for debugging
logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create an access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = db.query(UserModel).filter(UserModel.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# Get the current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

# Signup route
@router.post("/signup", response_model=UserCreateResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(
        role=user.role,
        username=user.username,
        email=user.email,
        phone=user.phone,
        password_hash=hash_password(user.password),
        address=user.address,
        city=user.city,
        state=user.state,
        postal_code=user.postal_code,
        is_oauth=user.is_oauth,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=400, detail="Error creating user")
    
    return {"id": db_user.id}

# Login route
@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Email not found")
    
    if db_user.is_oauth:
        raise HTTPException(status_code=400, detail="User registered with OAuth. Please use OAuth to log in.")
    
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return {"message": "Login successful", "user_id": db_user.id}

# Token route
@router.post("/token", response_model=Token)
async def login_for_access_token(
    email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user route
@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Delete user route
@router.delete("/delete", response_model=dict)
def delete_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if not db_user or not verify_password(password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

# Update user route
@router.patch("/update", response_model=User)
def update_user(user_update: UserUpdate = Depends(), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if not db_user or not verify_password(password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if user_update.new_password and verify_password(user_update.new_password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
    
    if user_update.username:
        db_user.username = user_update.username
    if user_update.phone:
        db_user.phone = user_update.phone
    if user_update.address:
        db_user.address = user_update.address
    if user_update.city:
        db_user.city = user_update.city
    if user_update.state:
        db_user.state = user_update.state
    if user_update.postal_code:
        db_user.postal_code = user_update.postal_code
    if user_update.new_password:
        db_user.password_hash = hash_password(user_update.new_password)
    
    db.commit()
    db.refresh(db_user)
    return db_user