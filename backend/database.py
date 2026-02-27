# Used to access environment variables (like DB username, password, etc.)
import os

# SQLAlchemy function to create database engine (connection manager)
from sqlalchemy import create_engine

# sessionmaker -> creates DB session objects
# declarative_base -> base class for ORM models (tables)
from sqlalchemy.orm import sessionmaker, declarative_base

# Used to load variables from .env file
from dotenv import load_dotenv


# Load environment variables from .env file into system environment
# This allows us to store sensitive data outside the code
load_dotenv()


# -------------------------------
# DATABASE CONFIGURATION
# -------------------------------
# Read database credentials from environment variables
# If not found, use default values provided as second argument

DB_USER = os.getenv("DB_USER", "postgres")         # Database username
DB_PASSWORD = os.getenv("DB_PASSWORD", "password") # Database password
DB_HOST = os.getenv("DB_HOST", "localhost")        # Database host (usually localhost)
DB_PORT = os.getenv("DB_PORT", "5432")             # PostgreSQL default port
DB_NAME = os.getenv("DB_NAME", "attendance_db")    # Database name


# Create full PostgreSQL connection URL
# Format: postgresql://username:password@host:port/database
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# -------------------------------
# ENGINE CREATION
# -------------------------------
# Engine is the core interface to the database
# It manages the connection pool and talks to PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# -------------------------------
# SESSION CONFIGURATION
# -------------------------------
# SessionLocal will be used to create database sessions
# autocommit=False -> You must manually commit changes
# autoflush=False -> Changes won’t auto-sync until committed
# bind=engine -> Attach session to our database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -------------------------------
# BASE CLASS FOR MODELS
# -------------------------------
# All ORM models (tables) will inherit from this Base class
# Example:
# class Employee(Base):
#     __tablename__ = "employees"
Base = declarative_base()


# -------------------------------
# DATABASE DEPENDENCY FUNCTION
# -------------------------------
# This function provides a database session to FastAPI endpoints
# It is used with: Depends(get_db)
# It automatically:
#   1. Creates DB session
#   2. Yields it to the route
#   3. Closes it after request finishes
def get_db():
    db = SessionLocal()  # Create new database session
    try:
        yield db         # Provide session to API route
    finally:
        db.close()       # Always close session after request (prevents memory leaks)
