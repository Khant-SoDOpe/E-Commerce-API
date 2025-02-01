from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import SessionLocal, engine
import models
import random

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
    oauth_id: str = None

@router.get("/users/{user_id}", response_model=dict)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the user's information.
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "phone": db_user.phone,
        "address": db_user.address,
        "city": db_user.city,
        "state": db_user.state,
        "postal_code": db_user.postal_code,
        "is_oauth": db_user.is_oauth,  # Use boolean field
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at
    }

app.include_router(router)