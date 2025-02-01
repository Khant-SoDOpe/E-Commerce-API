from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Replace 'username', 'password', and 'dbname' with your actual local MySQL credentials and database name.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine that will communicate with the MySQL database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal will be used for creating database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models will inherit from.
Base = declarative_base()

# Ensure the tables are created in the database
def create_tables():
    Base.metadata.create_all(bind=engine)
