from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "G116 Fertilizer Forecast API"
    api_v1_prefix: str = "/api/v1"

    # Database: keep every machine-specific value in .env.
    database_url: str | None = None
    db_server: str = r"(localdb)\MSSQLLocalDB"
    db_name: str = "g116"
    db_driver: str = "ODBC Driver 18 for SQL Server"
    db_encrypt: str = "yes"
    db_trust_server_certificate: str = "yes"
    db_trusted_connection: str = "yes"
    db_username: str | None = None
    db_password: str | None = None

    # Data locations. DATA_DIR defaults to the repo's data/processed directory.
    # IFFCO_DATA_DIR is useful when the two IFFCO CSVs live outside the repo.
    data_dir: str | None = None
    iffco_data_dir: str | None = None

    # Comma-separated frontend origins.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Import completeness checks. These are the agreed project deliverables.
    strict_import_counts: bool = True
    expected_forecast_rows: int = 144
    expected_history_rows: int = 1440
    expected_iffco_rows: int = 44
    expected_rajasthan_rows: int = 132

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def configured_data_dir(self, repo_root: Path) -> Path:
        return Path(self.data_dir).expanduser() if self.data_dir else repo_root / "data" / "processed"

    @property
    def configured_iffco_data_dir(self) -> Path | None:
        return Path(self.iffco_data_dir).expanduser() if self.iffco_data_dir else None


@lru_cache
def get_settings() -> Settings:
    return Settings()
