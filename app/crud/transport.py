from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.models.transport import Transport
from app.models.batch import Batch
from app.services.carbon_engine import calculate_transport_emission


# =====================================================
# INTERNAL HELPERS
# =====================================================

def _route_exists(
    db: Session,
    batch_id: int,
    origin: str,
    destination: str,
    exclude_id: int | None = None,
) -> bool:
    """
    Check whether a transport route already exists for a batch.
    Case-insensitive comparison.
    Optionally exclude a specific transport ID (for updates).
    """
    query = db.query(Transport).filter(
        Transport.batch_id == batch_id,
        func.lower(Transport.origin) == origin.lower(),
        func.lower(Transport.destination) == destination.lower(),
    )

    if exclude_id:
        query = query.filter(Transport.id != exclude_id)

    return db.query(query.exists()).scalar()


def _validate_origin(db: Session, batch_id: int, origin: str) -> None:
    """
    Ensure the given origin is valid according to the chain rules.
    """
    data = get_available_origins(db, batch_id)
    if not data:
        raise ValueError("Batch not found")

    if origin not in data["origins"]:
        raise ValueError("Invalid origin for this batch")


# =====================================================
# CREATE
# =====================================================

def create_transport(db: Session, data, transporter_id: int):
    """
    Create a new transport with:
    - Batch existence validation
    - Chain origin validation
    - Duplicate route prevention
    - Emission calculation
    """

    batch = db.query(Batch).filter(Batch.id == data.batch_id).first()
    if not batch:
        raise ValueError("Batch not found")

    # Validate chain integrity
    _validate_origin(db, data.batch_id, data.origin)

    # Prevent duplicate route
    if _route_exists(db, data.batch_id, data.origin, data.destination):
        raise ValueError(
            f"Transport already exists from '{data.origin}' to '{data.destination}' for this batch"
        )

    emission = calculate_transport_emission(data.distance_km, data.fuel_type)

    transport = Transport(
        **data.model_dump(),
        transporter_id=transporter_id,
        transport_emission=emission,
    )

    db.add(transport)
    db.commit()
    db.refresh(transport)
    return transport


# =====================================================
# SINGLE
# =====================================================

def get_transport(db: Session, transport_id: int):
    """
    Retrieve a single transport by ID.
    """
    return (
        db.query(Transport)
        .options(joinedload(Transport.batch))
        .filter(Transport.id == transport_id)
        .first()
    )


# =====================================================
# NEXT EXPECTED ORIGINS
# =====================================================

def get_available_origins(db: Session, batch_id: int):
    """
    Compute available origin locations for the next transport
    based on balance of incoming and outgoing transports.
    """

    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        return None

    source = batch.manufacturing_location

    incoming = dict(
        db.query(Transport.destination, func.count(Transport.id))
        .filter(Transport.batch_id == batch_id)
        .group_by(Transport.destination)
        .all()
    )

    outgoing = dict(
        db.query(Transport.origin, func.count(Transport.id))
        .filter(Transport.batch_id == batch_id)
        .group_by(Transport.origin)
        .all()
    )

    balances = {}

    for loc, count in incoming.items():
        balances[loc] = balances.get(loc, 0) + count

    for loc, count in outgoing.items():
        balances[loc] = balances.get(loc, 0) - count

    available = [source]

    for loc, bal in balances.items():
        if loc != source and bal > 0:
            available.append(loc)

    return {
        "manufactured_at": source,
        "origins": available,
    }


# =====================================================
# MY TRANSPORTS (PAGINATED)
# =====================================================

def get_my_transports(
    db: Session,
    transporter_id: int,
    skip: int,
    limit: int,
    search: str | None,
):
    """
    Return paginated transports for a transporter.
    Supports search across origin, destination,
    product name, and batch code.
    """

    query = (
        db.query(Transport)
        .join(Batch)
        .options(joinedload(Transport.batch))
        .filter(Transport.transporter_id == transporter_id)
    )

    if search:
        query = query.filter(
            or_(
                Transport.origin.ilike(f"%{search}%"),
                Transport.destination.ilike(f"%{search}%"),
                Batch.product_name.ilike(f"%{search}%"),
                Batch.batch_code.ilike(f"%{search}%"),
            )
        )

    total = query.count()

    items = (
        query.order_by(Transport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, items


# =====================================================
# BATCH TRANSPORTS
# =====================================================

def get_batch_transports(db: Session, batch_id: int, skip: int, limit: int):
    """
    Return paginated transports for a specific batch.
    """

    query = (
        db.query(Transport)
        .options(joinedload(Transport.batch))
        .filter(Transport.batch_id == batch_id)
    )

    total = query.count()

    items = (
        query.order_by(Transport.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, items


# =====================================================
# UPDATE
# =====================================================

def update_transport(db: Session, transport: Transport, data):
    """
    Update a transport:
    - Prevent duplicate routes
    - Recalculate emission if needed
    """

    update_data = data.model_dump(exclude_unset=True)

    new_origin = update_data.get("origin", transport.origin)
    new_destination = update_data.get("destination", transport.destination)

    # Prevent duplicate route
    if _route_exists(
        db,
        transport.batch_id,
        new_origin,
        new_destination,
        exclude_id=transport.id,
    ):
        raise ValueError(
            f"Transport already exists from '{new_origin}' to '{new_destination}' for this batch"
        )

    # Recalculate emission if necessary
    if "distance_km" in update_data or "fuel_type" in update_data:
        distance = update_data.get("distance_km", transport.distance_km)
        fuel = update_data.get("fuel_type", transport.fuel_type)
        update_data["transport_emission"] = calculate_transport_emission(
            distance, fuel
        )

    for key, value in update_data.items():
        setattr(transport, key, value)

    db.commit()
    db.refresh(transport)
    return transport


# =====================================================
# DELETE
# =====================================================

def delete_transport(db: Session, transport: Transport):
    """
    Delete a transport record.
    """

    db.delete(transport)
    db.commit()
    return True


# =====================================================
# STATS
# =====================================================

def get_transport_stats(db: Session, transporter_id: int):
    """
    Compute aggregated statistics for a transporter:
    - Total transports
    - Total distance
    - Total emissions
    - Average emission per km
    """

    result = db.query(
        func.count(Transport.id),
        func.coalesce(func.sum(Transport.distance_km), 0),
        func.coalesce(func.sum(Transport.transport_emission), 0),
    ).filter(Transport.transporter_id == transporter_id).one()

    total_transports, total_distance, total_emission = result

    return {
        "total_transports": total_transports,
        "total_distance": round(total_distance, 2),
        "total_emission": round(total_emission, 2),
        "avg_emission_per_km": round(
            (total_emission / total_distance), 4
        ) if total_distance else 0,
    }