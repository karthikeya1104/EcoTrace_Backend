import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.logger import get_logger

logger = get_logger("database")

# Load .env only for local development
load_dotenv()
logger.info("Environment variables loaded")

# Proper boolean parsing
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
logger.info(f"DEBUG mode: {DEBUG}")

if DEBUG:
    logger.info("Using SQLite (Development)")
    DATABASE_URL = "sqlite:///./ecotrace.db"
else:
    logger.info("Using PostgreSQL (Production)")
    DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set")
    raise ValueError("DATABASE_URL environment variable is not set")

logger.info(f"Database connection initialized")

# Fix postgres:// issue (Railway/Render compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs special argument
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # prevents stale connection errors
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()