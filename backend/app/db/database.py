from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def build_database_url():
    if settings.database_url:
        return settings.database_url

    parts = [
        f"DRIVER={{{settings.db_driver}}}",
        f"SERVER={settings.db_server}",
        f"DATABASE={settings.db_name}",
        f"TrustServerCertificate={settings.db_trust_server_certificate}",
    ]

    if settings.db_username:
        parts.extend([
            f"UID={settings.db_username}",
            f"PWD={settings.db_password or ''}",
        ])
    else:
        parts.append(f"Trusted_Connection={settings.db_trusted_connection}")

    odbc_connect = ";".join(parts)
    return URL.create("mssql+pyodbc", query={"odbc_connect": odbc_connect})


engine = create_engine(
    build_database_url(),
    pool_pre_ping=True,
    fast_executemany=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
