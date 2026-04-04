import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserCreate


class TestAuthentication:
    """Test authentication functionality."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com", "role": "manufacturer"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password(self):
        """Test password verification."""
        password = "testpassword123"
        hashed = user_crud.get_password_hash(password)

        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_user_creation(self, db_session: Session, test_user_data):
        """Test user creation in database."""
        from app.models.user import UserRole
        user_in = UserCreate(**test_user_data)
        user = user_crud.create_user(db_session, user_in, UserRole(test_user_data["role"]))

        assert user.email == test_user_data["email"]
        assert user.role == UserRole(test_user_data["role"])
        assert hasattr(user, "password")

    def test_duplicate_user_creation(self, db_session: Session, test_user_data):
        """Test that duplicate user creation fails."""
        user_in = UserCreate(**test_user_data)

        # Create first user
        user_crud.create_user(db_session, user_in)

        # Try to create duplicate
        with pytest.raises(Exception):  # Should raise IntegrityError
            user_crud.create_user(db_session, user_in)

    def test_user_authentication(self, db_session: Session, test_user_data):
        """Test user authentication."""
        user_in = UserCreate(**test_user_data)
        user = user_crud.create_user(db_session, user_in)

        # Test successful authentication
        authenticated_user = user_crud.authenticate_user(
            db_session, test_user_data["email"], test_user_data["password"]
        )
        assert authenticated_user is not None
        assert authenticated_user.email == user.email

        # Test failed authentication
        wrong_auth = user_crud.authenticate_user(
            db_session, test_user_data["email"], "wrongpassword"
        )
        assert wrong_auth is None


class TestAuthAPI:
    """Test authentication API endpoints."""

    def test_register_user(self, client, test_user_data):
        """Test user registration endpoint."""
        response = client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["role"] == test_user_data["role"]
        assert "id" in data
        assert "token" in data

    def test_register_duplicate_user(self, client, test_user_data):
        """Test duplicate user registration fails."""
        # Register first user
        client.post("/api/auth/register", json=test_user_data)

        # Try to register again
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400

    def test_login_success(self, client, test_user_data):
        """Test successful login."""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)

        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == test_user_data["email"]

    def test_login_wrong_password(self, client, test_user_data):
        """Test login with wrong password."""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)

        # Try login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401

    def test_get_current_user(self, client, test_user_data):
        """Test getting current user info."""
        # Register and login
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["token"]

        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["role"] == test_user_data["role"]

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401