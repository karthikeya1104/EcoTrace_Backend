from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithBatches
)
from app.crud.product import (
    create_product,
    get_product_by_id,
    get_all_products,
    get_manufacturer_products,
    update_product,
    delete_product,
    get_manufacturer_dashboard
)
from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole

router = APIRouter()


# -------------------------
# Manufacturer Routes
# -------------------------

@router.post("/", response_model=ProductResponse)
def create_new_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer))
):
    try:
        return create_product(db, data, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-products/all", response_model=list[ProductResponse])
def get_my_products(
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer))
):
    return get_manufacturer_products(db, user.id)


@router.get("/my-products/stats")
def get_my_products_stats(
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer))
):
    return get_manufacturer_dashboard(db, user.id)


# -------------------------
# Admin Route 
# -------------------------

@router.get("/", response_model=list[ProductResponse])
def list_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.admin))
):
    return get_all_products(db, skip, limit)

@router.get("/{product_id}", response_model=ProductWithBatches)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.admin))
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_info(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.admin))
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        return update_product(db, product, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}")
def delete_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.admin))
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    delete_product(db, product)
    return {"message": "Product deleted successfully"}