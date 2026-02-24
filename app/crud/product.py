from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.product import Product
from app.models.batch import Batch


# CREATE (Manufacturer)
def create_product(db: Session, data, manufacturer_id: int):
    exists = db.query(Product.id).filter(Product.name == data.name).first()
    if exists:
        raise ValueError("Product with this name already exists")

    product = Product(**data.dict(), manufacturer_id=manufacturer_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# GET ONE (Admin use)
def get_product_by_id(db: Session, product_id: int):
    return (
        db.query(Product)
        .options(joinedload(Product.batches))
        .filter(Product.id == product_id)
        .first()
    )


# GET ALL (Admin)
def get_all_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()


# GET MANUFACTURER PRODUCTS
def get_manufacturer_products(db: Session, manufacturer_id: int):
    return db.query(Product)\
        .filter(Product.manufacturer_id == manufacturer_id)\
        .all()


# UPDATE (Admin only)
def update_product(db: Session, product: Product, data):
    update_data = data.dict(exclude_unset=True)

    if "name" in update_data:
        exists = db.query(Product.id).filter(
            Product.name == update_data["name"],
            Product.id != product.id
        ).first()
        if exists:
            raise ValueError("Product with this name already exists")

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# DELETE (Admin only)
def delete_product(db: Session, product: Product):
    db.delete(product)
    db.commit()


# MANUFACTURER DASHBOARD
def get_manufacturer_dashboard(db: Session, manufacturer_id: int):

    total_products = db.query(func.count(Product.id))\
        .filter(Product.manufacturer_id == manufacturer_id)\
        .scalar() or 0

    total_batches = (
        db.query(func.count(Batch.id))
        .join(Product)
        .filter(Product.manufacturer_id == manufacturer_id)
        .scalar()
    ) or 0

    # Batch count per product
    rows = (
        db.query(
            Product.id,
            Product.name,
            func.count(Batch.id).label("batch_count")
        )
        .outerjoin(Batch)
        .filter(Product.manufacturer_id == manufacturer_id)
        .group_by(Product.id)
        .all()
    )

    # Latest batch per product
    subq = (
        db.query(
            Batch.product_id,
            func.max(Batch.created_at).label("max_created")
        )
        .join(Product)
        .filter(Product.manufacturer_id == manufacturer_id)
        .group_by(Batch.product_id)
        .subquery()
    )

    latest = (
        db.query(Batch)
        .join(
            subq,
            (Batch.product_id == subq.c.product_id) &
            (Batch.created_at == subq.c.max_created)
        )
        .all()
    )

    latest_map = {
        b.product_id: {
            "last_batch_id": b.id,
            "last_batch_code": b.batch_code,
            "last_batch_created_at": b.created_at,
        }
        for b in latest
    }

    products = []
    for r in rows:
        prod = {
            "id": r.id,
            "name": r.name,
            "batch_count": int(r.batch_count),
            "last_batch_id": None,
            "last_batch_code": None,
            "last_batch_created_at": None,
        }

        if r.id in latest_map:
            prod.update(latest_map[r.id])

        products.append(prod)

    return {
        "total_products": int(total_products),
        "total_batches": int(total_batches),
        "products": products
    }