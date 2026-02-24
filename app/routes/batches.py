from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from math import ceil
from app.schemas.batch import (
    BatchCreate,
    BatchUpdate,
    BatchResponse,
    BatchListResponse,
)
from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole
from app.crud.batch import (
    list_batches,
    get_batch, 
    create_batch,
    update_batch,
    delete_batch,
)

router = APIRouter()


# ============================================================
# LIST (Paginated)
# ============================================================
@router.get("/my", response_model=BatchListResponse)
def list_my_batches(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer)),
):
    
    total, items = list_batches(
        db=db,
        manufacturer_id=user.id,
        page=page,
        limit=limit,
        search=search,
    )

    return BatchListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=ceil(total / limit) if total else 1,
        items=items,
    )


# ============================================================
# GET SINGLE
# ============================================================
@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer)),
):
    batch = get_batch(db, batch_id, user.id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return batch


# ============================================================
# CREATE
# ============================================================
@router.post("/{product_id}", response_model=BatchResponse)
def create_batch(
    product_id: int,
    data: BatchCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer)),
):
    try:
        batch, _ = create_batch(
            db=db,
            product_id=product_id,
            manufacturer_id=user.id,
            data=data,
        )
        return batch
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# UPDATE
# ============================================================
@router.put("/{batch_id}", response_model=BatchResponse)
def update_batch(
    batch_id: int,
    data: BatchUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer)),
):
    try:
        return update_batch(
            db=db,
            batch_id=batch_id,
            manufacturer_id=user.id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================
# DELETE
# ============================================================
@router.delete("/{batch_id}")
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer)),
):
    try:
        delete_batch(
            db=db,
            batch_id=batch_id,
            manufacturer_id=user.id,
        )
        return {"message": "Batch deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))