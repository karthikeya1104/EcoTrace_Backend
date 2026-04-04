import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    # Use SQLite for testing
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "company_name": "Test Company",
        "role": "manufacturer"
    }


@pytest.fixture
def test_product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "category": "Electronics",
        "sku": "TEST-001",
        "description": "A test product for unit testing"
    }


@pytest.fixture
def test_batch_data():
    """Sample batch data for testing."""
    return {
        "batch_code": "BATCH-001",
        "manufacture_date": "2024-01-15",
        "expiry_date": "2026-01-15",
        "materials": [
            {"name": "plastic", "percentage": 30},
            {"name": "metal", "percentage": 50},
            {"name": "electronics", "percentage": 20}
        ]
    }