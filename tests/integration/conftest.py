"""
Fixtures pour tests d'intégration (API endpoints)
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import FastAPI
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Load .env file into environment variables BEFORE importing anything
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/.env'))
load_dotenv(env_path)

from models.db_schemes.minirag.schemes.minirag_base import SQLAlchemyBase as Base
from helpers.config import Settings

# Now load settings (will use environment variables loaded above)
settings = Settings()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_engine():
    """
    Create test database engine (PostgreSQL Docker - TEST DATABASE)
    Uses a separate test database 'minirag_test' to isolate from production
    """
    # Use SEPARATE test database to avoid touching production tables
    test_db_name = f"{settings.POSTGRES_MAIN_DATABASE}_test"

    test_db_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{test_db_name}"
    )

    engine = create_async_engine(
        test_db_url,
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables in TEST database only
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up - drop all tables from TEST database only (NOT production!)
    # Safe because we're using minirag_test, not minirag
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine):
    """
    Create test database session
    """
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def test_app(test_db_engine):
    """
    Create test FastAPI app without lifespan
    """
    # Create a simple app without lifespan for testing
    from routes import auth

    app = FastAPI()

    # Create session maker from test engine
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    # Attach db_client to app
    app.db_client = async_session

    # Register routes
    app.include_router(auth.auth_router)

    return app


@pytest.fixture(scope="function")
async def test_client(test_app):
    """
    Create test client with test app
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def registered_user(test_client, admin_user):
    """
    Create a registered user (not admin)
    Returns user credentials and token
    Requires admin_user fixture to create the user
    """
    # Create a regular user via admin endpoint using admin_user token
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "role": "user"
    }

    create_response = await test_client.post(
        "/api/v1/auth/admin/users",
        json=user_data,
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )

    # Check if user creation succeeded
    if create_response.status_code != 200:
        raise Exception(f"Admin create user failed: {create_response.status_code} - {create_response.json()}")

    # Login as regular user
    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )

    # Check if login succeeded
    if login_response.status_code != 200:
        raise Exception(f"Regular user login failed: {login_response.status_code} - {login_response.json()}")

    user_token = login_response.json()["access_token"]

    return {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": user_data["password"],
        "token": user_token,
        "role": "user"
    }


@pytest.fixture
async def admin_user(test_client):
    """
    Create an admin user
    Returns admin credentials and token
    """
    # First user automatically becomes admin
    admin_data = {
        "username": "admin",
        "email": "admin@test.com",
        "password": "AdminPass123!"
    }

    response = await test_client.post("/api/v1/auth/register", json=admin_data)

    # Check if registration succeeded
    if response.status_code != 200:
        raise Exception(f"Admin user registration failed: {response.status_code} - {response.json()}")

    return {
        "username": admin_data["username"],
        "email": admin_data["email"],
        "password": admin_data["password"],
        "token": response.json()["access_token"],
        "role": "admin"
    }


@pytest.fixture
def auth_headers(admin_user):
    """
    Helper to create authorization headers
    """
    def _auth_headers(token: str = None):
        token_to_use = token or admin_user["token"]
        return {"Authorization": f"Bearer {token_to_use}"}

    return _auth_headers
