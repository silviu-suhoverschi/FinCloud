"""
Test configuration and fixtures
"""

import pytest
import pytest_asyncio
import asyncio
import uuid
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import JSON, String, event, TypeDecorator
from sqlalchemy.dialects import postgresql

# UUID type adapter for SQLite
class SQLiteUUID(TypeDecorator):
    """Platform-independent UUID type that stores UUID as string on SQLite"""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(String(36))
        else:
            return dialect.type_descriptor(postgresql.UUID())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'sqlite':
            return str(value)
        else:
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value

# Import app components
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


def _adapt_metadata_for_sqlite(target, connection, **kw):
    """Adapt PostgreSQL-specific types and constraints to SQLite-compatible ones"""
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    from sqlalchemy.schema import CheckConstraint
    from sqlalchemy import BigInteger, Integer

    # Replace PostgreSQL-specific types with SQLite-compatible ones
    for table in Base.metadata.tables.values():
        # Fix column types
        for column in table.columns:
            if isinstance(column.type, JSONB):
                column.type = JSON()
            elif isinstance(column.type, UUID):
                column.type = SQLiteUUID()
            elif isinstance(column.type, BigInteger) and column.primary_key:
                # SQLite needs INTEGER PRIMARY KEY for autoincrement
                column.type = Integer()
                column.autoincrement = True

            # Remove PostgreSQL-specific server defaults
            if column.server_default:
                server_default_text = str(column.server_default.arg)
                if 'gen_random_uuid' in server_default_text:
                    column.server_default = None

        # Remove PostgreSQL-specific check constraints (those with regex)
        constraints_to_remove = []
        for constraint in table.constraints:
            if isinstance(constraint, CheckConstraint):
                constraint_text = str(constraint.sqltext)
                if '~*' in constraint_text or 'regexp' in constraint_text.lower():
                    constraints_to_remove.append(constraint)

        for constraint in constraints_to_remove:
            table.constraints.discard(constraint)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine():
    """Create a test database engine using SQLite in-memory database"""
    # Use SQLite in-memory database for testing (no PostgreSQL required)
    test_db_url = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(test_db_url, echo=False)

    # Register event listener to adapt metadata for SQLite
    event.listen(Base.metadata, "before_create", _adapt_metadata_for_sqlite)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with transaction rollback"""
    # Create a connection
    async with test_engine.connect() as connection:
        # Begin a transaction
        trans = await connection.begin()

        # Create a session bound to the connection
        async_session = sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session() as session:
            yield session

        # Rollback the transaction to clean up test data
        await trans.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
