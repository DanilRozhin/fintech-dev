import os
from pathlib import Path

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.database import Base, db_helper
from app.main import app as main_app

from .fakes import FakeProviderClient

env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file, override=True)

TEST_DB_NAME = str(os.getenv("TEST__APP_CONFIG__DB__NAME"))
TEST_DB_USER = str(os.getenv("TEST__APP_CONFIG__DB__USER"))
TEST_DB_PASSWORD = str(os.getenv("TEST__APP_CONFIG__DB__PASSWORD"))
TEST_DB_HOST = str(os.getenv("TEST__APP_CONFIG__DB__HOST"))
TEST_DB_PORT = str(os.getenv("TEST__APP_CONFIG__DB__PORT"))
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
def session_maker(test_engine):
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine, session_maker):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client(db_session, session_maker):
    main_app.state.provider_client = FakeProviderClient()

    async def override_get_async_session():
        async with session_maker() as session:
            yield session

    main_app.dependency_overrides[db_helper.session_getter] = override_get_async_session

    original_session_factory = db_helper.session_factory
    db_helper.session_factory = session_maker

    try:
        async with AsyncClient(
            transport=ASGITransport(app=main_app),
            base_url="http://test",
            follow_redirects=True,
        ) as ac:
            ac.app = main_app
            yield ac
    finally:
        main_app.dependency_overrides.clear()
        db_helper.session_factory = original_session_factory
