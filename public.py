from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from pydantic import BaseModel, EmailStr
import uuid
from pydantic import UUID4

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

# Pydantic model for incoming user creation data.
class UserCreate(BaseModel):
    username: str
    role: str = "user"  # Set default role to "user"
    email: EmailStr
    phone: str
    password: str
    address: str
    city: str
    state: str
    postal_code: str
    is_oauth: bool = False
    oauth_id: str = None

@router.get("/users/{user_id}", response_model=dict)
def read_user(user_id: UUID4, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    roles = db.query(models.Role).join(models.UserRole).filter(models.UserRole.user_id == user_id).all()
    role_names = [role.name for role in roles]
    
    return {
        "id": str(db_user.id),  # Ensure the id is returned as a string
        "username": db_user.username,
        "email": db_user.email,
        "phone": db_user.phone,
        "address": db_user.address,
        "city": db_user.city,
        "state": db_user.state,
        "postal_code": db_user.postal_code,
        "oauth_provider": db_user.oauth_provider,
        "oauth_id": db_user.oauth_id,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "roles": role_names
    }