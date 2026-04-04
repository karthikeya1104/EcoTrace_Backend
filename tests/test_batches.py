import pytest
from sqlalchemy.orm import Session

from app.crud import batch as batch_crud
from app.schemas.batch import BatchCreate, BatchUpdate


class TestBatchCRUD:
    """Test batch CRUD operations."""

    def test_create_batch(self, db_session: Session, test_user_data, test_product_data, test_batch_data):
        """Test batch creation."""
        # Create user and product first
        from app.crud.user import create_user
        from app.crud.product import create_product
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate

        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        product = create_product(db_session, product_in, user.id)

        # Create batch
        batch_in = BatchCreate(**{**test_batch_data, "product_id": product.id})
        batch = batch_crud.create_batch(db_session, batch_in, user.id)

        assert batch.product_id == product.id
        assert batch.quantity == test_batch_data["quantity"]
        assert batch.material_composition == test_batch_data["material_composition"]
        assert batch.created_by == user.id

    def test_get_batch_by_id(self, db_session: Session, test_user_data, test_product_data, test_batch_data):
        """Test getting batch by ID."""
        # Create user, product, and batch
        from app.crud.user import create_user
        from app.crud.product import create_product
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate

        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        product = create_product(db_session, product_in, user.id)
        batch_in = BatchCreate(**{**test_batch_data, "product_id": product.id})
        created_batch = batch_crud.create_batch(db_session, batch_in, user.id)

        # Get batch
        batch = batch_crud.get_batch_by_id(db_session, created_batch.id)
        assert batch is not None
        assert batch.id == created_batch.id

    def test_get_batches_by_user(self, db_session: Session, test_user_data, test_product_data, test_batch_data):
        """Test getting batches by user."""
        # Create user and product
        from app.crud.user import create_user
        from app.crud.product import create_product
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate

        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        product = create_product(db_session, product_in, user.id)

        # Create multiple batches
        for i in range(3):
            batch_data = {**test_batch_data, "product_id": product.id, "quantity": 100 + i}
            batch_in = BatchCreate(**batch_data)
            batch_crud.create_batch(db_session, batch_in, user.id)

        # Get user's batches
        batches = batch_crud.get_batches_by_user(db_session, user.id)
        assert len(batches) == 3

    def test_update_batch(self, db_session: Session, test_user_data, test_product_data, test_batch_data):
        """Test batch update."""
        # Create user, product, and batch
        from app.crud.user import create_user
        from app.crud.product import create_product
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate

        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        product = create_product(db_session, product_in, user.id)
        batch_in = BatchCreate(**{**test_batch_data, "product_id": product.id})
        batch = batch_crud.create_batch(db_session, batch_in, user.id)

        # Update batch
        update_data = BatchUpdate(quantity=200, status="completed")
        updated_batch = batch_crud.update_batch(db_session, batch.id, update_data)

        assert updated_batch.quantity == 200
        assert updated_batch.status == "completed"

    def test_delete_batch(self, db_session: Session, test_user_data, test_product_data, test_batch_data):
        """Test batch deletion."""
        # Create user, product, and batch
        from app.crud.user import create_user
        from app.crud.product import create_product
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate

        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        product = create_product(db_session, product_in, user.id)
        batch_in = BatchCreate(**{**test_batch_data, "product_id": product.id})
        batch = batch_crud.create_batch(db_session, batch_in, user.id)

        # Delete batch
        result = batch_crud.delete_batch(db_session, batch.id)
        assert result is True

        # Verify deletion
        deleted_batch = batch_crud.get_batch_by_id(db_session, batch.id)
        assert deleted_batch is None


class TestBatchAPI:
    """Test batch API endpoints."""

    def test_create_batch_api(self, client, test_user_data, test_product_data, test_batch_data):
        """Test batch creation via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product first
        product_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = product_response.json()["id"]

        # Create batch
        batch_data = {**test_batch_data, "product_id": product_id}
        response = client.post("/api/batches/", json=batch_data, headers=headers)
        assert response.status_code == 201

        data = response.json()
        assert data["product_id"] == product_id
        assert data["quantity"] == test_batch_data["quantity"]

    def test_get_user_batches_api(self, client, test_user_data, test_product_data, test_batch_data):
        """Test getting user batches via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product
        product_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = product_response.json()["id"]

        # Create batch
        batch_data = {**test_batch_data, "product_id": product_id}
        client.post("/api/batches/", json=batch_data, headers=headers)

        # Get batches
        response = client.get("/api/batches/my", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["product_id"] == product_id

    def test_get_batch_by_id_api(self, client, test_user_data, test_product_data, test_batch_data):
        """Test getting batch by ID via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product and batch
        product_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = product_response.json()["id"]
        batch_data = {**test_batch_data, "product_id": product_id}
        batch_response = client.post("/api/batches/", json=batch_data, headers=headers)
        batch_id = batch_response.json()["id"]

        # Get batch by ID
        response = client.get(f"/api/batches/{batch_id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == batch_id
        assert data["product_id"] == product_id

    def test_update_batch_api(self, client, test_user_data, test_product_data, test_batch_data):
        """Test batch update via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product and batch
        product_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = product_response.json()["id"]
        batch_data = {**test_batch_data, "product_id": product_id}
        batch_response = client.post("/api/batches/", json=batch_data, headers=headers)
        batch_id = batch_response.json()["id"]

        # Update batch
        update_data = {"quantity": 200, "status": "completed"}
        response = client.put(f"/api/batches/{batch_id}", json=update_data, headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["quantity"] == 200
        assert data["status"] == "completed"

    def test_delete_batch_api(self, client, test_user_data, test_product_data, test_batch_data):
        """Test batch deletion via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product and batch
        product_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = product_response.json()["id"]
        batch_data = {**test_batch_data, "product_id": product_id}
        batch_response = client.post("/api/batches/", json=batch_data, headers=headers)
        batch_id = batch_response.json()["id"]

        # Delete batch
        response = client.delete(f"/api/batches/{batch_id}", headers=headers)
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/batches/{batch_id}", headers=headers)
        assert get_response.status_code == 404

    def test_batch_qr_code_generation(self, client, test_user_data, test_product_data, test_batch_data):
        """Test QR code generation for batch."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product and batch
        product_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = product_response.json()["id"]
        batch_data = {**test_batch_data, "product_id": product_id}
        batch_response = client.post("/api/batches/", json=batch_data, headers=headers)
        batch_id = batch_response.json()["id"]

        # Generate QR code
        response = client.get(f"/api/batches/{batch_id}/qr", headers=headers)
        assert response.status_code == 200

        # Should return QR code data
        data = response.json()
        assert "qr_code" in data
        assert "batch_info" in data