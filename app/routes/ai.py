from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole
from app.models.ai_score import AIScore
from app.models.batch import Batch
from app.services.ai_engine import generate_ai_score, analyze_batch_materials

router = APIRouter()

# Get AI score for a batch (Public)
@router.get("/batch/{batch_id}/score")
def get_batch_ai_score(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """Get the AI sustainability score for a batch."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    ai_score = db.query(AIScore).filter(AIScore.batch_id == batch_id).first()
    if not ai_score:
        raise HTTPException(status_code=404, detail="No AI score found for this batch")
    
    return {
        "id": ai_score.id,
        "batch_id": ai_score.batch_id,
        "environment_score": ai_score.environment_score,
        "ethics_score": ai_score.ethics_score,
        "safety_score": ai_score.safety_score,
        "cost_score": ai_score.cost_score,
        "final_score": ai_score.final_score,
        "reasoning": ai_score.reasoning,
        "generated_at": ai_score.generated_at
    }

# Analyze batch materials (manufacturer only)
@router.post("/batch/{batch_id}/analyze-materials")
def analyze_batch_material_info(
    batch_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.manufacturer))
):
    """
    Analyze materials in a batch.
    Returns AI-generated insights (placeholder data, will be replaced with actual AI).
    Manufacturers can only analyze their own batches.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if batch.product.manufacturer_id != user.id:
        raise HTTPException(status_code=403, detail="You can only analyze your own batches")
    
    analysis = analyze_batch_materials(batch.material_info or "")
    return {
        "batch_id": batch_id,
        "analysis": analysis,
        "note": "This is placeholder data. Actual AI analysis will be implemented later."
    }

# Generate new AI score
@router.post("/batch/{batch_id}/generate-score")
def regenerate_ai_score(
    batch_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_role(UserRole.admin))
):
    """
    Regenerate AI score for a batch.
    Admin only. Returns random placeholder data until AI engine is implemented.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    score_data = generate_ai_score()
    
    # Update or create AI score
    ai_score = db.query(AIScore).filter(AIScore.batch_id == batch_id).first()
    if not ai_score:
        ai_score = AIScore(batch_id=batch_id)
        db.add(ai_score)
    
    ai_score.environment_score = score_data.get("environment_score")
    ai_score.ethics_score = score_data.get("ethics_score")
    ai_score.safety_score = score_data.get("safety_score")
    ai_score.cost_score = score_data.get("cost_score")
    ai_score.final_score = score_data.get("final_score")
    ai_score.reasoning = score_data.get("reasoning")
    
    db.commit()
    db.refresh(ai_score)
    
    return {
        "id": ai_score.id,
        "batch_id": ai_score.batch_id,
        "environment_score": ai_score.environment_score,
        "ethics_score": ai_score.ethics_score,
        "safety_score": ai_score.safety_score,
        "cost_score": ai_score.cost_score,
        "final_score": ai_score.final_score,
        "reasoning": ai_score.reasoning,
        "note": "This is placeholder data. Actual AI analysis will be implemented later."
    }

# Get batch sustainability insights (Public)
@router.get("/batch/{batch_id}/insights")
def get_batch_sustainability_insights(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Get sustainability insights for a batch from AI analysis.
    Returns placeholder data until AI engine is fully implemented.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    ai_score = db.query(AIScore).filter(AIScore.batch_id == batch_id).first()
    
    return {
        "batch_id": batch_id,
        "overall_score": ai_score.final_score if ai_score else None,
        "sustainability_rating": "Excellent" if ai_score and ai_score.final_score >= 80 else "Good" if ai_score and ai_score.final_score >= 70 else "Fair" if ai_score else "Not Rated",
        "key_insights": [
            "Material sourcing should be optimized",
            "Carbon footprint is within acceptable range",
            "Consider implementing circular economy principles"
        ],
        "improvement_areas": [
            "Reduce packaging waste",
            "Source from certified sustainable suppliers",
            "Implement recycling programs"
        ],
        "note": "These are placeholder insights. Actual AI-powered analysis will be implemented later."
    }
