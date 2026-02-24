from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.batch import Batch
from app.models.product import Product
from app.models.lab_report import LabReport
from app.models.transport import Transport
from app.models.ai_score import AIScore

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/batch/{batch_id}")
def view_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")

    product = db.query(Product).filter(Product.id == batch.product_id).first()
    lab = db.query(LabReport).filter(LabReport.batch_id == batch.id).all()
    transport = db.query(Transport).filter(Transport.batch_id == batch.id).all()
    score = db.query(AIScore).filter(AIScore.batch_id == batch.id).first()

    return {
        "product": {
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "description": product.description
        },
        "batch": {
            "code": batch.batch_code,
            "material_info": batch.material_info,
            "manufactured": batch.manufacture_date,
            "expiry": batch.expiry_date,
            "location": batch.manufacturing_location,
            "base_carbon": batch.base_carbon_footprint,
            "status": batch.status
        },
        "lab_reports": [
            {
                "summary": l.test_summary,
                "certifications": l.certifications,
                "eco_rating": l.eco_rating,
                "verified": l.verified,
                "date": l.created_at
            } for l in lab
        ],
        "transport": [
            {
                "origin": t.origin,
                "destination": t.destination,
                "distance_km": t.distance_km,
                "fuel": t.fuel_type,
                "emission": t.transport_emission
            } for t in transport
        ],
        "ai_score": score and {
            "environment": score.environment_score,
            "ethics": score.ethics_score,
            "safety": score.safety_score,
            "cost": score.cost_score,
            "final": score.final_score
        }
    }
