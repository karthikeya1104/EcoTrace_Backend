from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.routes.auth import get_db
from app.core.roles import require_role
from app.models.user import UserRole

from app.schemas.transport import (
    TransportCreate,
    TransportUpdate,
    TransportResponse,
    TransportListResponse
)

from app.crud.transport import (
    get_transport_stats,
    get_my_transports,
    get_available_origins,
    get_batch_transports,
    create_transport,
    get_transport,
    update_transport,
    delete_transport,
)

router = APIRouter()

@router.get("/my/stats")
def transport_stats(
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.transporter))
):
    """
    Return aggregated transport statistics for the logged-in transporter.
    """
    return get_transport_stats(db, user.id)


@router.get("/my", response_model=TransportListResponse)
def list_my_transports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.transporter))
):
    """
    Return paginated transports belonging to the logged-in transporter.
    Optional search across origin, destination, product name, and batch code.
    """
    total, items = get_my_transports(db, user.id, skip, limit, search)
    return {"total": total, "items": items}


@router.get("/batch/{batch_id}/available-origins")
def available_origins(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Return valid origin locations for the next transport of a batch.
    """
    data = get_available_origins(db, batch_id)

    if not data:
        raise HTTPException(status_code=404, detail="Batch not found")

    return data


@router.get("/batch/{batch_id}", response_model=TransportListResponse)
def list_batch_transports(
    batch_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.manufacturer))
):
    """
    Return paginated transports for a specific batch.
    """
    total, items = get_batch_transports(db, batch_id, skip, limit)
    return {"total": total, "items": items}


@router.post("/", response_model=TransportResponse)
def create_new_transport(
    data: TransportCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.transporter))
):
    """
    Create a new transport for a batch.
    Performs duplicate and chain validation.
    """
    try:
        return create_transport(db, data, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transport_id}", response_model=TransportResponse)
def get_transport_by_id(
    transport_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.transporter))
):
    """
    Return a single transport belonging to the logged-in transporter.
    """
    transport = get_transport(db, transport_id)

    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")

    if transport.transporter_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return transport


@router.put("/{transport_id}", response_model=TransportResponse)
def update_transport_info(
    transport_id: int,
    data: TransportUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.admin))
):
    """
    Update transport information:
    - Only admin can update 
    """
    transport = get_transport(db, transport_id)

    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")

    if transport.transporter_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return update_transport(db, transport_id, data)


@router.delete("/{transport_id}")
def delete_transport_by_id(
    transport_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.admin))
):
    """
    Delete transport information:
    - Only admin can delete
    """
    transport = get_transport(db, transport_id)

    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")

    if transport.transporter_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    delete_transport(db, transport_id)

    return {"message": "Deleted successfully"}