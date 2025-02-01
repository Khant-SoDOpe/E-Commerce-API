from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import SessionLocal, engine
import models
import random
import logging
from passlib.context import CryptContext
import uuid

# Create all database tables (if they don't already exist)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for incoming user creation data.
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone: str
    password: str  # This will be hashed before storage.
    address: str
    city: str
    state: str
    postal_code: str
    is_oauth: bool = False  # Changed to boolean

# Pydantic model for login data
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Pydantic model for user creation response
class UserCreateResponse(BaseModel):
    id: int

# Pydantic model for login response
class LoginResponse(BaseModel):
    message: str
    user_id: int

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

# Generate a unique 4-digit ID or UUID for users
def generate_unique_id(db: Session):
    new_id = str(uuid.uuid4().int)[:8]  # Generate a short UUID-based ID
    return new_id

# Add a logger for debugging
logging.basicConfig(level=logging.INFO)

@router.post("/signup", response_model=UserCreateResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the username or email already exists
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Generate a unique 4-digit ID
    user_id = generate_unique_id(db)

    # Create a new User instance.
    db_user = models.User(
        id=user_id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        password_hash=hash_password(user.password),  # Use hashed password
        address=user.address,
        city=user.city,
        state=user.state,
        postal_code=user.postal_code,
        is_oauth=user.is_oauth,  # Use boolean field
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=400, detail="Error creating user")
    
    # Return the newly created user's ID.
    return {"id": db_user.id}

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Email not found")
    
    if db_user.is_oauth:
        raise HTTPException(status_code=400, detail="User registered with OAuth. Please use OAuth to log in.")
    
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Return a success message and user ID
    return {"message": "Login successful", "user_id": db_user.id}

app.include_router(router)
