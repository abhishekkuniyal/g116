from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()


def build_database_url():
    """Build a SQLAlchemy URL from .env, unless DATABASE_URL overrides it."""
    if settings.database_url:
        return settings.database_url

    parts = [
        f"DRIVER={{{settings.db_driver}}}",
        f"SERVER={settings.db_server}",
        f"DATABASE={settings.db_name}",
        f"Encrypt={settings.db_encrypt}",
        f"TrustServerCertificate={settings.db_trust_server_certificate}",
    ]

    if settings.db_username:
        parts.extend([
            f"UID={settings.db_username}",
            f"PWD={settings.db_password or ''}",
        ])
    else:
        parts.append(f"Trusted_Connection={settings.db_trusted_connection}")

    return URL.create("mssql+pyodbc", query={"odbc_connect": ";".join(parts)})


def _create_engine():
    database_url = build_database_url()
    url_text = str(database_url)

    # SQLite support is intentionally kept for fast isolated API tests.
    if url_text.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        fast_executemany=True,
    )


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
