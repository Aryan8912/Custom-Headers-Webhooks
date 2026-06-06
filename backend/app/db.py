from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import get_settings

settings = get_settings()

# ── Engine ─────────────────────────────────────────────
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    **({} if _is_sqlite else {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })
)

# ── Session factory ────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Dependency: get async DB session ──────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Create all tables (used on startup) ───────────────
async def init_db():
    # import models so the correct Base sees them
    from app.models.base import Base
    from app.models import execution_log, tenant

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)