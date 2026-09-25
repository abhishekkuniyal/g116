"""Create the configured SQL Server database without assuming SQLEXPRESS.

Works with LocalDB, SQL Server Express, or a normal SQL Server instance as long
as DB_SERVER/DB_DRIVER/authentication are correctly set in backend/.env.
"""
from pathlib import Path
import sys

import pyodbc

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402

settings = get_settings()


def master_connection_string() -> str:
    parts = [
        f"DRIVER={{{settings.db_driver}}}",
        f"SERVER={settings.db_server}",
        "DATABASE=master",
        f"Encrypt={settings.db_encrypt}",
        f"TrustServerCertificate={settings.db_trust_server_certificate}",
    ]
    if settings.db_username:
        parts.extend([f"UID={settings.db_username}", f"PWD={settings.db_password or ''}"])
    else:
        parts.append(f"Trusted_Connection={settings.db_trusted_connection}")
    return ";".join(parts)


def main():
    if settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is set. Create the database using that server's administration tooling, "
            "or temporarily configure DB_SERVER/DB_* fields and leave DATABASE_URL blank."
        )

    print(f"Server: {settings.db_server}")
    print(f"Driver: {settings.db_driver}")
    print(f"Database: {settings.db_name}")

    conn = pyodbc.connect(master_connection_string(), autocommit=True)
    try:
        cursor = conn.cursor()
        exists = cursor.execute("SELECT DB_ID(?)", settings.db_name).fetchone()[0]
        if exists is None:
            safe_name = settings.db_name.replace("]", "]]" )
            cursor.execute(f"CREATE DATABASE [{safe_name}]")
            print(f"Created database: {settings.db_name}")
        else:
            print(f"Database already exists: {settings.db_name}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
