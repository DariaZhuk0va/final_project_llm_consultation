import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# Создаём in-memory базу для тестов
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncTestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_db] = override_get_db
    yield
    await engine.dispose()
    app.dependency_overrides.clear()

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

async def test_register_and_login_flow(client):
    # Регистрация
    reg_data = {"email": "test@example.com", "password": "12345678"}
    resp = await client.post("/auth/register", json=reg_data)
    assert resp.status_code == 201
    user = resp.json()
    assert user["email"] == reg_data["email"]
    assert "id" in user
    assert user["role"] == "user"

    # Логин (OAuth2 form)
    login_data = {"username": reg_data["email"], "password": reg_data["password"]}
    resp = await client.post("/auth/login", data=login_data)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    # Запрос /me
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me = resp.json()
    assert me["email"] == reg_data["email"]
    assert me["id"] == user["id"]

async def test_register_duplicate_email(client):
    reg_data = {"email": "duplicate@example.com", "password": "12345678"}
    await client.post("/auth/register", json=reg_data)
    resp = await client.post("/auth/register", json=reg_data)
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]

async def test_login_invalid_credentials(client):
    # Несуществующий email
    resp = await client.post("/auth/login", data={"username": "none@ex.com", "password": "pass"})
    assert resp.status_code == 401
    # Существующий, но неверный пароль
    await client.post("/auth/register", json={"email": "valid@ex.com", "password": "correct"})
    resp = await client.post("/auth/login", data={"username": "valid@ex.com", "password": "wrong"})
    assert resp.status_code == 401

async def test_me_without_token(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401

async def test_me_with_invalid_token(client):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401