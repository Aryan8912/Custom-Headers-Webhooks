import pytest
import fakeredis.aioredis as fakeredis
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import create_app
from app.db import get_db, Base
from app.cache import get_redis
import app.cache as cache_module


# ── Test DB setup ──────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Create all tables once per session ────────────────
@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── DB session per test ────────────────────────────────
@pytest.fixture
async def db():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


# ── Fake Redis per test ────────────────────────────────
@pytest.fixture(autouse=True)
async def fake_redis():
    fake = fakeredis.FakeRedis(decode_responses=True)
    cache_module.redis_client = fake
    yield fake
    await fake.aclose()
    cache_module.redis_client = None


# ── FastAPI test client ────────────────────────────────
@pytest.fixture
async def client(db):
    app = create_app()

    # override DB dependency
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Valid Bolna headers fixture ────────────────────────
@pytest.fixture
def bolna_headers():
    return {
        "Authorization": "Bearer test-secret-key",
        "X-API-Key": "test-x-api-key",
        "X-Tenant-ID": "tenant_a",
    }


# ── Sample Bolna payload fixture ───────────────────────
@pytest.fixture
def bolna_payload():
    return {
        "execution_id": "exec_test_123",
        "agent_id": "agent_test_456",
        "status": "completed",
        "transcript": "Hello, how can I help you today?",
        "duration": 45.5,
        "from_number": "+1234567890",
        "to_number": "+0987654321",
    }