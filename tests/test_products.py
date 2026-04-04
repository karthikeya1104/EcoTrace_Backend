import pytest
from sqlalchemy.orm import Session

from app.crud import product as product_crud
from app.schemas.product import ProductCreate, ProductUpdate


class TestProductCRUD:
    """Test product CRUD operations."""

    def test_create_product(self, db_session: Session, test_user_data, test_product_data):
        """Test product creation."""
        # Create user first
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        user = create_user(db_session, UserCreate(**test_user_data))

        # Create product
        product_in = ProductCreate(**test_product_data)
        product = product_crud.create_product(db_session, product_in, user.id)

        assert product.name == test_product_data["name"]
        assert product.category == test_product_data["category"]
        assert product.sku == test_product_data["sku"]
        assert product.created_by == user.id

    def test_get_product_by_id(self, db_session: Session, test_user_data, test_product_data):
        """Test getting product by ID."""
        # Create user and product
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        created_product = product_crud.create_product(db_session, product_in, user.id)

        # Get product
        product = product_crud.get_product_by_id(db_session, created_product.id)
        assert product is not None
        assert product.id == created_product.id

    def test_get_products_by_user(self, db_session: Session, test_user_data, test_product_data):
        """Test getting products by user."""
        # Create user and products
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        user = create_user(db_session, UserCreate(**test_user_data))

        # Create multiple products
        products_data = [
            test_product_data,
            {**test_product_data, "name": "Product 2", "sku": "TEST-002"},
            {**test_product_data, "name": "Product 3", "sku": "TEST-003"}
        ]

        for product_data in products_data:
            product_in = ProductCreate(**product_data)
            product_crud.create_product(db_session, product_in, user.id)

        # Get user's products
        products = product_crud.get_products_by_user(db_session, user.id)
        assert len(products) == 3

    def test_update_product(self, db_session: Session, test_user_data, test_product_data):
        """Test product update."""
        # Create user and product
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        product = product_crud.create_product(db_session, product_in, user.id)

        # Update product
        update_data = ProductUpdate(name="Updated Product", category="Updated Category")
        updated_product = product_crud.update_product(db_session, product.id, update_data)

        assert updated_product.name == "Updated Product"
        assert updated_product.category == "Updated Category"
        assert updated_product.sku == test_product_data["sku"]  # Unchanged

    def test_delete_product(self, db_session: Session, test_user_data, test_product_data):
        """Test product deletion."""
        # Create user and product
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        user = create_user(db_session, UserCreate(**test_user_data))
        product_in = ProductCreate(**test_product_data)
        product = product_crud.create_product(db_session, product_in, user.id)

        # Delete product
        result = product_crud.delete_product(db_session, product.id)
        assert result is True

        # Verify deletion
        deleted_product = product_crud.get_product_by_id(db_session, product.id)
        assert deleted_product is None


class TestProductAPI:
    """Test product API endpoints."""

    def test_create_product_api(self, client, test_user_data, test_product_data):
        """Test product creation via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product
        response = client.post("/api/products/", json=test_product_data, headers=headers)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == test_product_data["name"]
        assert data["category"] == test_product_data["category"]
        assert data["sku"] == test_product_data["sku"]

    def test_get_user_products_api(self, client, test_user_data, test_product_data):
        """Test getting user products via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product
        client.post("/api/products/", json=test_product_data, headers=headers)

        # Get products
        response = client.get("/api/products/my-products/all", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == test_product_data["name"]

    def test_get_product_by_id_api(self, client, test_user_data, test_product_data):
        """Test getting product by ID via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product
        create_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = create_response.json()["id"]

        # Get product by ID
        response = client.get(f"/api/products/{product_id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == test_product_data["name"]

    def test_update_product_api(self, client, test_user_data, test_product_data):
        """Test product update via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product
        create_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = create_response.json()["id"]

        # Update product
        update_data = {"name": "Updated Product", "category": "Updated Category"}
        response = client.put(f"/api/products/{product_id}", json=update_data, headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["category"] == "Updated Category"

    def test_delete_product_api(self, client, test_user_data, test_product_data):
        """Test product deletion via API."""
        # Register and login user
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create product
        create_response = client.post("/api/products/", json=test_product_data, headers=headers)
        product_id = create_response.json()["id"]

        # Delete product
        response = client.delete(f"/api/products/{product_id}", headers=headers)
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/products/{product_id}", headers=headers)
        assert get_response.status_code == 404

    def test_unauthorized_access(self, client, test_user_data, test_product_data):
        """Test that unauthorized users cannot access products."""
        # Register user1
        register_response1 = client.post("/api/auth/register", json=test_user_data)
        token1 = register_response1.json()["token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Create product for user1
        create_response = client.post("/api/products/", json=test_product_data, headers=headers1)
        product_id = create_response.json()["id"]

        # Register user2
        user2_data = {**test_user_data, "email": "user2@example.com"}
        register_response2 = client.post("/api/auth/register", json=user2_data)
        token2 = register_response2.json()["token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Try to access user1's product with user2's token
        response = client.get(f"/api/products/{product_id}", headers=headers2)
        assert response.status_code == 404  # Should not find the product