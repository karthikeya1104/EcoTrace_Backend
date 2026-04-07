from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import SessionLocal
from app.models.batch import Batch
from app.models.product import Product
from app.models.lab_report import LabReport
from app.models.transport import Transport
from app.models.ai_score import AIScore
from app.models.material import Material, BatchMaterial

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/batch/{batch_id}")
def view_batch(batch_id: int, db: Session = Depends(get_db)):

    batch = (
        db.query(Batch)
        .options(
            selectinload(Batch.product),
            selectinload(Batch.materials).selectinload(BatchMaterial.material),
            selectinload(Batch.lab_reports).selectinload(LabReport.lab),
            selectinload(Batch.ai_scores),
            selectinload(Batch.transports).selectinload(Transport.transporter)
        )
        .filter(Batch.id == batch_id)
        .first()
    )

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    ai_score = batch.ai_scores[0] if batch.ai_scores else None

    return {
        "product": {
            "id": batch.product.id,
            "name": batch.product.name,
            "brand": batch.product.brand,
            "category": batch.product.category,
            "description": batch.product.description,
        },
        "batch": {
            "id": batch.id,
            "code": batch.batch_code,
            "manufacture_date": batch.manufacture_date,
            "expiry_date": batch.expiry_date,
            "manufacturing_location": batch.manufacturing_location,
            "base_carbon_footprint": batch.base_carbon_footprint,
            "status": batch.status.value if batch.status else None,
            "validation_status": batch.validation_status.value if batch.validation_status else None,
            "created_at": batch.created_at,
        },
        "materials": [
            {
                "material_id": bm.material.id,
                "name": bm.material.name,
                "common_name": bm.material.common_name,
                "risk_level": bm.material.risk_level,
                "description": bm.material.description,
                "percentage": bm.percentage,
                "source_info_provided": bm.source_info_provided,
                "source": bm.source,
            }
            for bm in batch.materials
        ],
        "transports": [
            {
                "id": t.id,
                "transporter_name": t.transporter.name if t.transporter else None,
                "origin": t.origin,
                "destination": t.destination,
                "distance_km": t.distance_km,
                "fuel_type": t.fuel_type,
                "vehicle_type": t.vehicle_type,
                "transport_emission": t.transport_emission,
                "notes": t.notes,
                "created_at": t.created_at,
            }
            for t in batch.transports
        ],
        "lab_reports": [
            {
                "id": l.id,
                "lab_name": l.lab.name if l.lab else None,
                "analysis": l.analysis_data,
                "certifications": l.certifications,
                "safety_status": (
                    l.safety_status.value
                    if hasattr(l.safety_status, "value")
                    else l.safety_status
                ),
                "notes": l.notes,
                "lab_score": l.lab_score,
                "verified": l.verified,
                "created_at": l.created_at,
            }
            for l in batch.lab_reports
        ],
        "ai_score": {
            "rating": ai_score.rating,
            "reasoning": ai_score.reasoning,
            "generated_at": ai_score.generated_at,
        }
        if ai_score
        else None,
    }