from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "G116 Fertilizer Forecast API"
    api_v1_prefix: str = "/api/v1"

    database_url: str | None = None
    db_server: str = r"localhost\SQLEXPRESS"
    db_name: str = "g116"
    db_driver: str = "ODBC Driver 17 for SQL Server"
    db_trust_server_certificate: str = "yes"
    db_trusted_connection: str = "yes"
    db_username: str | None = None
    db_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
