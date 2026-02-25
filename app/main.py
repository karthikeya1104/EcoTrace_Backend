from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import *
from app.routes import auth, admin, users, products, batches, public, transport, ai, lab_reports, lab
from app.utils.logger import get_logger
import dotenv
import os

logger = get_logger("main")

dotenv.load_dotenv()
logger.info("FastAPI application starting...")

app = FastAPI(title="EcoTrace")
logger.info("FastAPI app initialized")

# 🔓 CORS CONFIGURATION (ADD THIS)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
origins = [
    "http://localhost:5173",      # Vite
    "http://127.0.0.1:5173",
    "http://localhost:3000",      # CRA (if ever)
    "http://127.0.0.1:3000",
] if DEBUG else [
    os.getenv("FRONTEND_URL", "http://localhost:5173")
]

logger.info(f"CORS origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🔓 END CORS CONFIGURATION

logger.info("CORS middleware added")

# ROUTES
app.include_router(auth.router, prefix="/auth")
logger.info("Auth router loaded")
app.include_router(admin.router)
logger.info("Admin router loaded")
app.include_router(users.router, prefix="/api")
logger.info("Users router loaded")
app.include_router(products.router, prefix="/api/products", tags=["Products"])
logger.info("Products router loaded")
app.include_router(batches.router, prefix="/api/batches", tags=["Batches"])
logger.info("Batches router loaded")
app.include_router(transport.router, prefix="/api/transports", tags=["Transport"])
logger.info("Transport router loaded")
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
logger.info("AI router loaded")
app.include_router(lab.router, prefix="/api/labs", tags=["Labs"])
logger.info("Labs router loaded")
app.include_router(lab_reports.router, prefix="/api/lab-reports", tags=["LabReports"])
logger.info("Lab reports router loaded")
app.include_router(public.router, prefix="/api", tags=["public"])
logger.info("Public router loaded")

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    raise

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "EcoTrace backend running"}

