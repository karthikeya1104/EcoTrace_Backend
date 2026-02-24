from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import *
from app.routes import auth, admin, users, products, batches, public, transport, ai, lab_reports, lab
import dotenv
import os

dotenv.load_dotenv()

app = FastAPI(title="EcoTrace")

# 🔓 CORS CONFIGURATION (ADD THIS)
origins = [
    "http://localhost:5173",      # Vite
    "http://127.0.0.1:5173",
    "http://localhost:3000",      # CRA (if ever)
    "http://127.0.0.1:3000",
] if not os.getenv("DEBUG") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🔓 END CORS CONFIGURATION


# ROUTES
app.include_router(auth.router, prefix="/auth")
app.include_router(admin.router)
app.include_router(users.router, prefix="/api")
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(batches.router, prefix="/api/batches", tags=["Batches"])
app.include_router(transport.router, prefix="/api/transports", tags=["Transport"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(lab.router, prefix="/api/labs", tags=["Labs"])
app.include_router(lab_reports.router, prefix="/api/lab-reports", tags=["LabReports"])
app.include_router(public.router, prefix="/api", tags=["public"])

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "EcoTrace backend running"}
